from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from config import NAS_FOLDER, CLEANUP_LOG_FILE
from metrics.cleanup_metrics import CleanupMetrics
from fs.images import get_base_and_ch
from fs.result_writer import SyncResultWriter
from logging_config import setup_logger
from infra.smb import ensure_smb_connection

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
    return m
