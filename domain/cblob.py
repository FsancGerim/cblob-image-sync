from typing import Iterable, Iterator, Any

def extract_itmrefs(rows: Iterable[Any]) -> set[str]:
    """
    Extrae ITMREFs desde:
    - dicts
    - tuplas
    - strings
    """
    out = set()
    for row in rows:
        if isinstance(row, dict):
            for k in ("itmref", "ITMREF", "ITMREF_0"):
                if k in row and row[k] is not None:
                    out.add(str(row[k]))
                    break
        elif isinstance(row, (tuple, list)):
            if row and row[0] is not None:
                out.add(str(row[0]))
        else:
            out.add(str(row))
    return out


def extract_blobs(rows: Iterable[Any]) -> Iterator[tuple[str, Any]]:
    """
    Extrae pares (itmref, blob) desde dicts o tuplas.
    """
    for row in rows:
        if isinstance(row, dict):
            itmref = row.get("itmref") or row.get("ITMREF") or row.get("ITMREF_0")
            blob = row.get("blob") or row.get("BLOB") or row.get("BLOB_0")
        else:
            itmref, blob = row[0], row[1]

        if itmref is None or blob is None:
            continue

        yield str(itmref), blob

