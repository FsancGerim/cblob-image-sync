from dataclasses import dataclass

@dataclass
class Metrics:
    db_itmrefs_total: int = 0
    nas_jpg_total: int = 0
    missing_total: int = 0

    blobs_fetched_total: int = 0
    jpg_created_total: int = 0
    jpg_skipped_exists_total: int = 0
    jpg_failed_total: int = 0

    t_scan_nas_seconds: float = 0.0
    t_fetch_blobs_seconds: float = 0.0
    t_write_jpg_seconds: float = 0.0
    t_total_seconds: float = 0.0