from pathlib import Path
import ast
import re

def blob_to_bytes(blob) -> bytes:
    # bytes reales
    if isinstance(blob, (bytes, bytearray, memoryview)):
        return bytes(blob)

    if isinstance(blob, str):
        s = blob.strip()

        # Caso bytes
        if s.startswith("b'") or s.startswith('b"'):
            return ast.literal_eval(s)

        # Caso hex
        if s.lower().startswith("0x"):
            s = s[2:]
        s_clean = re.sub(r"[^0-9a-fA-F]", "", s)
        if len(s_clean) >= 4 and len(s_clean) % 2 == 0:
            return bytes.fromhex(s_clean)

    raise TypeError(f"Formato de blob no soportado: {type(blob)}")

def write_jpg(blob, out_path: str | Path, overwrite: bool = False) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    if out.exists() and not overwrite:
        return out

    data = blob_to_bytes(blob)

    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(out)
    return out
