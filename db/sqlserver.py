import pyodbc

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

def get_itmref_from_cblob():
    sql="""
    SELECT IDENT1_0 AS ITMREF_0 FROM GERIMPORT.CBLOB;
    """
    with _get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql)
        return {str(itmref) for (itmref,) in cur}

def get_blobs():
    sql="""
    SELECT TOP 1 IDENT1_0 AS ITMREF_0, BLOB_0 FROM GERIMPORT.CBLOB;
    """
    with _get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


if __name__ == "__main__":
    print("funcionando")
    test = get_blobs()
    itmrefs = [row["ITMREF_0"] for row in test]
    print(itmrefs)
    