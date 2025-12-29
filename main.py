from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path

from config import NAS_FOLDER
from logging_config import setup_logger

# Tareas (ajusta estos imports si decides otro sitio/nombre)
from tasks.sync_photos import run_sync
from tasks.cleanup_photos import run_cleanup

log = setup_logger()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="photo_nas_tools",
        description="Herramientas para sincronizar y limpiar fotos en el NAS (ITMREF).",
    )

    sub = p.add_subparsers(dest="command", required=True)

    # --- sync ---
    ps = sub.add_parser("sync", help="Sincroniza fotos: DB -> crea <itmref>_ch.jpg en NAS si faltan.")
    ps.add_argument("--dry-run", action="store_true", help="No escribe archivos; solo muestra métricas.")
    ps.add_argument("--chunk-size", type=int, default=1000, help="Tamaño de lote para traer blobs (default: 1000).")

    # --- cleanup ---
    pc = sub.add_parser("cleanup", help="Borra <itmref>_ch.jpg si existe también <itmref>.jpg.")
    pc.add_argument("--dry-run", action="store_true", help="No borra; solo muestra qué borraría.")
    pc.add_argument(
        "--folder",
        type=Path,
        default=NAS_FOLDER,
        help=f"Carpeta objetivo (default: {NAS_FOLDER}).",
    )

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "sync":
        # Por consistencia, tu run_sync usa dry_run=True por defecto,
        # aquí lo activamos si pasan --dry-run
        m = run_sync(dry_run=args.dry_run, chunk_size=args.chunk_size)
        log.info("SYNC METRICS: %s", asdict(m))
        return 0

    if args.command == "cleanup":
        m = run_cleanup(dry_run=args.dry_run, folder=args.folder)
        log.info("CLEANUP METRICS: %s", asdict(m))
        return 0

    parser.error("Comando no reconocido")
    return 2


if __name__ == "__main__":
    #raise SystemExit(main())
