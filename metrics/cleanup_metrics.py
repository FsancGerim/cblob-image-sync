from dataclasses import dataclass

@dataclass
class CleanupMetrics:
    scanned_files_total: int = 0
    jpg_base_total: int = 0
    jpg_ch_total: int = 0
    pairs_total: int = 0
    ch_deleted_total: int = 0
    ch_failed_total: int = 0
