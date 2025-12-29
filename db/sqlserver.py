import pyodbc
from typing import Iterable

from config import (
    SQL_SERVER,
    SQL_DB,
    SQL_USER,
    SQL_PASS,
    SQL_DRIVER,
)

def _get_connection():
    conn_str = (
        f"DRIVER={{{SQL_DRIVER}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DB};"
        f"UID={SQL_USER};"
        f"PWD={SQL_PASS};"
        "TrustServerCertificate=yes;"
        "Encrypt=yes;"
    )
    return pyodbc.connect(conn_str, timeout=10, autocommit=True)

def _norm(s) -> str | None:
    if s is None:
        return None
    v = str(s).strip()
    return v or None

def get_itmref_from(table_name: str) -> set[str]:
    if table_name == 'ZPROVEART':
        sql = """
        SELECT
            ZTP.ITMREF_0 AS ITMREF_0
        FROM ZTPROVEART AS ZTP
        LEFT JOIN BPSUPPLIER AS BPS
            ON ZTP.BPSNUM_0 = BPS.BPSNUM_0
        LEFT JOIN ZURLIMAGENES AS ZURL
            ON ZTP.ITMREF_0 = ZURL.ITMREF_0
        LEFT JOIN ZPROART4 AS Z4
            ON ZTP.ITMREF_0 = Z4.ITMREF_0
        WHERE COALESCE(ZTP.BPSNUM_0, '') <> '';
        """
    elif table_name == 'CBLOB':
        sql = "SELECT IDENT1_0 AS ITMREF_0 FROM GERIMPORT.CBLOB"
    else:
        raise ValueError(f"Tabla no soportada: {table_name}")

    with _get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql)
        out: set[str] = set()
        for (itmref,) in cur:
            v = _norm(itmref)
            if v:
                out.add(v)
        return out

def _chunks(seq: list[str], size: int):
    for i in range(0, len(seq), size):
        yield seq[i:i+size]

def get_blobs_by_itmrefs(itmrefs: Iterable[str], chunk_size: int = 1000):
    # normaliza entrada (por si viene con espacios)
    itmrefs = [x for x in (_norm(x) for x in itmrefs) if x]

    sql_template = """
        SELECT IDENT1_0 AS ITMREF_0, BLOB_0
        FROM GERIMPORT.CBLOB
        WHERE IDENT1_0 IN ({placeholders})
    """

    with _get_connection() as conn:
        cur = conn.cursor()

        for chunk in _chunks(itmrefs, chunk_size):
            placeholders = ",".join(["?"] * len(chunk))
            sql = sql_template.format(placeholders=placeholders)

            cur.execute(sql, chunk)
            for itmref, blob in cur:
                v = _norm(itmref)
                if v is None:
                    continue
                yield v, blob
