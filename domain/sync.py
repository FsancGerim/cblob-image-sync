from db.sqlserver import get_itmref_from
from domain.cblob import extract_itmrefs
from fs.images import get_jpg_names


def compare_itmrefs(folder: str):
    itmrefs_db = extract_itmrefs(get_itmref_from("ZPROVEART"))
    itmrefs_fs = get_jpg_names(folder)

    missing = itmrefs_db - itmrefs_fs
    extra = itmrefs_fs - itmrefs_db
    common = itmrefs_db & itmrefs_fs

    return missing, extra, common

