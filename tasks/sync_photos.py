from __future__ import annotations

import time
from dataclasses import asdict

from config import NAS_FOLDER, RESULT_LOG_FILE
from logging_config import setup_logger
from db.sqlserver import get_itmref_from, get_blobs_by_itmrefs
from domain.cblob import extract_itmrefs
from metrics.sync_metrics import Metrics
from fs.images import get_jpg_names
from fs.jpg_writer import write_jpg
from fs.result_writer import SyncResultWriter
from infra.smb import ensure_smb_connection

log = setup_logger()


def run_sync(dry_run: bool = True, chunk_size: int = 1000) -> Metrics:
    ensure_smb_connection()
    m = Metrics()
    t0 = time.perf_counter()

    result_writer = SyncResultWriter(RESULT_LOG_FILE)
    log.info("Inicio sync | dry_run=%s | NAS_FOLDER=%s", dry_run, NAS_FOLDER)

    itmref_zpr = extract_itmrefs(get_itmref_from("ZPROVEART"))
    m.db_itmrefs_total = len(itmref_zpr)

    t_scan = time.perf_counter()
    itmref_nas = get_jpg_names(NAS_FOLDER)
    m.t_scan_nas_seconds = time.perf_counter() - t_scan
    m.nas_jpg_total = len(itmref_nas)

    missing = itmref_zpr - itmref_nas
    m.missing_total = len(missing)

    log.info("ZPRO=%d | NAS=%d | FALTANTES=%d | scan_nas=%.2fs",
             m.db_itmrefs_total, m.nas_jpg_total, m.missing_total, m.t_scan_nas_seconds)

    if dry_run:
        log.info("DRY RUN activo. Ejemplo faltantes: %s", list(missing)[:10])
        m.t_total_seconds = time.perf_counter() - t0
        log.info("METRICS: %s", asdict(m))
        return m

    output_folder = NAS_FOLDER
    log.info("OUTPUT_FOLDER=%s", output_folder)

    t_fetch = time.perf_counter()
    for i, (itmref, blob) in enumerate(get_blobs_by_itmrefs(missing, chunk_size=chunk_size), start=1):
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

        if i % 100 == 0:
            log.info("Progreso: %d/%d | creados=%d | fallos=%d",
                     i, m.missing_total, m.jpg_created_total, m.jpg_failed_total)

    m.t_fetch_blobs_seconds = time.perf_counter() - t_fetch
    m.t_total_seconds = time.perf_counter() - t0

    log.info("FIN sync | creados=%d | skipped=%d | fallos=%d",
             m.jpg_created_total, m.jpg_skipped_exists_total, m.jpg_failed_total)
    log.info("METRICS: %s", asdict(m))
    return m
