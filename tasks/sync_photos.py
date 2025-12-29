from __future__ import annotations

import time
from dataclasses import asdict

from config import (
    NAS_FOLDER,
    MAIL_TO,
    MAIL_FROM,
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASS,
    RESULT_LOG_FILE,
)
from logging_config import setup_logger
from db.sqlserver import get_itmref_from, get_blobs_by_itmrefs
from domain.cblob import extract_itmrefs
from metrics.sync_metrics import Metrics
from fs.images import get_jpg_names
from fs.jpg_writer import write_jpg
from fs.result_writer import SyncResultWriter
from infra.smb import ensure_smb_connection
from infra.email import send_mail

log = setup_logger()


def run_sync(dry_run: bool = True, chunk_size: int = 1000) -> Metrics:
    ensure_smb_connection()
    m = Metrics()
    t0 = time.perf_counter()

    result_writer = SyncResultWriter(RESULT_LOG_FILE)
    log.info("Inicio sync | dry_run=%s | NAS_FOLDER=%s", dry_run, NAS_FOLDER)

    # 1) ITMREFs desde ZPRO
    itmref_zpr = extract_itmrefs(get_itmref_from("ZPROVEART"))
    m.db_itmrefs_total = len(itmref_zpr)

    # 2) ITMREFs existentes en NAS (JPGs)
    t_scan = time.perf_counter()
    itmref_nas = get_jpg_names(NAS_FOLDER)
    m.t_scan_nas_seconds = time.perf_counter() - t_scan
    m.nas_jpg_total = len(itmref_nas)

    # 3) Diferencia (candidatos)
    missing = itmref_zpr - itmref_nas
    m.missing_total = len(missing)

    log.info(
        "ZPRO=%d | NAS=%d | FALTAN_EN_NAS=%d | scan_nas=%.2fs",
        m.db_itmrefs_total, m.nas_jpg_total, m.missing_total, m.t_scan_nas_seconds
    )

    if dry_run:
        log.info("DRY RUN activo. Ejemplo faltantes: %s", list(missing)[:10])
        m.t_total_seconds = time.perf_counter() - t0
        log.info("METRICS: %s", asdict(m))

        _send_sync_email(m, dry_run=True)
        return m

    output_folder = NAS_FOLDER
    log.info("OUTPUT_FOLDER=%s", output_folder)

    # 4) Traer blobs y crear JPGs (por chunks para poder detectar NO_BLOB)
    missing_list = sorted(missing)

    t_fetch = time.perf_counter()

    for start in range(0, len(missing_list), chunk_size):
        chunk = missing_list[start:start + chunk_size]
        chunk_set = set(chunk)

        fetched_itmrefs: set[str] = set()

        for itmref, blob in get_blobs_by_itmrefs(chunk_set, chunk_size=chunk_size):
            fetched_itmrefs.add(itmref)
            m.blobs_fetched_total += 1

            out_file = output_folder / f"{itmref}_ch.jpg"

            if out_file.exists():
                m.jpg_skipped_exists_total += 1
                result_writer.write("SKIPPED", itmref, out_file, "already exists")
                continue

            try:
                t_w = time.perf_counter()
                write_jpg(blob, out_file, overwrite=False)
                m.t_write_jpg_seconds += (time.perf_counter() - t_w)

                if out_file.exists():
                    m.jpg_created_total += 1
                    result_writer.write("CREATED", itmref, out_file)
                else:
                    m.jpg_failed_total += 1
                    result_writer.write("FAILED", itmref, out_file, "not created (no exception)")
                    log.warning("No se creó el JPG (sin excepción) para ITMREF=%s", itmref)

            except Exception as e:
                m.jpg_failed_total += 1
                result_writer.write("FAILED", itmref, out_file, str(e))
                log.exception("Error creando JPG para ITMREF=%s", itmref)

        # Los que estaban en ZPRO y faltaban en NAS, pero no existen en CBLOB
        not_in_cblob = chunk_set - fetched_itmrefs
        for itmref in sorted(not_in_cblob):
            m.blobs_missing_total += 1
            out_file = output_folder / f"{itmref}_ch.jpg"
            result_writer.write("NO_BLOB", itmref, out_file, "not found in GERIMPORT.CBLOB")

        # progreso por chunk (opcional)
        done = min(start + chunk_size, len(missing_list))
        if done % 1000 == 0 or done == len(missing_list):
            log.info(
                "Progreso chunks: %d/%d | creados=%d | no_blob=%d | fallos=%d",
                done, len(missing_list), m.jpg_created_total, m.blobs_missing_total, m.jpg_failed_total
            )

    m.t_fetch_blobs_seconds = time.perf_counter() - t_fetch
    m.t_total_seconds = time.perf_counter() - t0

    log.info(
        "FIN sync | creados=%d | skipped=%d | no_blob=%d | fallos=%d",
        m.jpg_created_total, m.jpg_skipped_exists_total, m.blobs_missing_total, m.jpg_failed_total
    )
    log.info("METRICS: %s", asdict(m))

    _send_sync_email(m, dry_run=False)
    return m


def _send_sync_email(m: Metrics, dry_run: bool) -> None:
    status = "OK" if m.jpg_failed_total == 0 else "ERROR"
    subject = f"[CBlob Sync] {status}" + (" (DRY RUN)" if dry_run else "")

    body = (
        "Proceso de sincronización finalizado.\n\n"
        f"Dry run: {dry_run}\n"
        f"Total ZPRO: {m.db_itmrefs_total}\n"
        f"Total NAS: {m.nas_jpg_total}\n"
        f"Faltan en NAS: {m.missing_total}\n"
        f"Blobs encontrados (CBLOB): {m.blobs_fetched_total}\n"
        f"Sin blob en CBLOB: {m.blobs_missing_total}\n"
        f"Creados: {m.jpg_created_total}\n"
        f"Saltados: {m.jpg_skipped_exists_total}\n"
        f"Fallos: {m.jpg_failed_total}\n"
        f"Tiempo total: {m.t_total_seconds:.2f}s\n"
    )

    try:
        send_mail(
            subject=subject,
            body=body,
            to=[x.strip() for x in MAIL_TO if x.strip()],
            attachments=[RESULT_LOG_FILE],
            sender=MAIL_FROM,
            smtp_server=SMTP_SERVER,
            smtp_port=int(SMTP_PORT),
            smtp_user=SMTP_USER,
            smtp_pass=SMTP_PASS,
        )
    except Exception:
        log.exception("No se pudo enviar el mail de resumen del sync")
