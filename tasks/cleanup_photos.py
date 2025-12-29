from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from config import (
    NAS_FOLDER,
    CLEANUP_LOG_FILE,
    MAIL_TO,
    MAIL_FROM,
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASS,
)
from metrics.cleanup_metrics import CleanupMetrics
from fs.images import get_base_and_ch
from fs.result_writer import SyncResultWriter
from logging_config import setup_logger
from infra.smb import ensure_smb_connection
from infra.email import send_mail

log = setup_logger()


def run_cleanup(dry_run: bool = True, folder: Path = NAS_FOLDER) -> CleanupMetrics:
    ensure_smb_connection()
    m = CleanupMetrics()

    result_writer = SyncResultWriter(CLEANUP_LOG_FILE)

    base, ch = get_base_and_ch(folder)
    m.jpg_base_total = len(base)
    m.jpg_ch_total = len(ch)

    pairs = base & ch
    m.pairs_total = len(pairs)

    log.info(
        "Inicio cleanup | folder=%s | base=%d | ch=%d | pairs=%d | dry_run=%s",
        folder, m.jpg_base_total, m.jpg_ch_total, m.pairs_total, dry_run
    )

    for itmref in sorted(pairs):
        ch_file = Path(folder) / f"{itmref}_ch.jpg"

        # Puede pasar si alguien lo borra entre el scan y este bucle
        if not ch_file.exists():
            result_writer.write("SKIPPED", itmref, ch_file, "missing at deletion time")
            continue

        if dry_run:
            result_writer.write("WOULD_DELETE", itmref, ch_file, "dry_run")
            continue

        try:
            ch_file.unlink()
            m.ch_deleted_total += 1
            result_writer.write("DELETED", itmref, ch_file, "")
        except Exception as e:
            m.ch_failed_total += 1
            result_writer.write("FAILED", itmref, ch_file, str(e))
            log.exception("No se pudo borrar %s", ch_file)

    log.info("FIN cleanup | deleted=%d | failed=%d", m.ch_deleted_total, m.ch_failed_total)
    log.info("CLEANUP METRICS: %s", asdict(m))

    _send_cleanup_email(m, dry_run=dry_run, folder=Path(folder))
    return m


def _send_cleanup_email(m: CleanupMetrics, dry_run: bool, folder: Path) -> None:
    status = "OK" if m.ch_failed_total == 0 else "ERROR"
    subject = f"[CBlob Cleanup] {status}" + (" (DRY RUN)" if dry_run else "")

    body = (
        "Proceso de limpieza finalizado.\n\n"
        f"Carpeta: {folder}\n"
        f"Dry run: {dry_run}\n\n"
        f"Base JPG: {m.jpg_base_total}\n"
        f"CH JPG: {m.jpg_ch_total}\n"
        f"Pares detectados (base & ch): {m.pairs_total}\n"
        f"Borrados: {m.ch_deleted_total}\n"
        f"Fallos: {m.ch_failed_total}\n"
    )

    try:
        send_mail(
            subject=subject,
            body=body,
            to=[x.strip() for x in MAIL_TO if x.strip()],
            attachments=[CLEANUP_LOG_FILE],
            sender=MAIL_FROM,
            smtp_server=SMTP_SERVER,
            smtp_port=int(SMTP_PORT),
            smtp_user=SMTP_USER,
            smtp_pass=SMTP_PASS,
        )
    except Exception:
        # No queremos que el cleanup falle por culpa del email
        log.exception("No se pudo enviar el mail de resumen del cleanup")
