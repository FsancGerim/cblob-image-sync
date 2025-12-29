from __future__ import annotations

import subprocess
from pathlib import Path
from logging_config import setup_logger
from config import NAS_SHARE, NAS_USER, NAS_PASS

log = setup_logger()


def ensure_smb_connection() -> None:
    """
    Asegura que existe una conexión SMB válida a NAS_SHARE.
    Usa credenciales del entorno (.env).
    """
    if not NAS_SHARE:
        raise RuntimeError("NAS_SHARE no definido")

    if not NAS_USER or not NAS_PASS:
        raise RuntimeError("NAS_USER / NAS_PASS no definidos en entorno")

    # Limpia conexión previa (evita conflicto de credenciales)
    subprocess.run(
        ["net", "use", NAS_SHARE, "/delete"],
        capture_output=True,
        text=True,
    )

    log.info("Conectando a NAS %s como %s", NAS_SHARE, NAS_USER)

    p = subprocess.run(
        ["net", "use", NAS_SHARE, NAS_PASS, f"/user:{NAS_USER}"],
        capture_output=True,
        text=True,
    )

    if p.returncode != 0:
        raise RuntimeError(
            f"Error conectando a NAS {NAS_SHARE}\n{p.stdout}\n{p.stderr}"
        )
