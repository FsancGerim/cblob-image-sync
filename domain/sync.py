from db.sqlserver import get_itmref_from_cblob
from domain.cblob import extract_itmrefs
from fs.images import get_jpg_names

def compare_itmrefs(folder: str):
    itmrefs_db = extract_itmrefs(get_itmref_from_cblob())
    itmrefs_fs = get_jpg_names(folder)

    missing_in_fs = itmrefs_db - itmrefs_fs
    extra_in_fs = itmrefs_fs - itmrefs_db
    common = itmrefs_db & itmrefs_fs

    print(f"DB total: {len(itmrefs_db)}")
    print(f"FS total: {len(itmrefs_fs)}")
    print(f"Faltan en carpeta: {len(missing_in_fs)}")
    print(f"Sobran en carpeta: {len(extra_in_fs)}")
    print(f"Comunes: {len(common)}")

    return missing_in_fs, extra_in_fs
