"""Local authenticity for canonical records. This is not public-key PDF signing."""
import hashlib
import hmac
import json
import os
from pathlib import Path

def canonical(payload):
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")

def load_key():
    folder = Path(os.environ.get("OCULOEDGE_STATE_DIR", Path(__file__).resolve().parents[1] / ".local"))
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "report.key"
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        key = path.read_bytes()
    else:
        key = os.urandom(32)
        with os.fdopen(fd, "wb") as stream:
            stream.write(key)
    if len(key) != 32:
        raise ValueError("La clave local de reportes debe tener 32 bytes.")
    return key

def sign_record(payload, key):
    data = canonical(payload)
    return {"payload": payload, "sha256": hashlib.sha256(data).hexdigest(),
            "signature": hmac.new(key, data, hashlib.sha256).hexdigest(), "scheme": "HMAC-SHA256-local-v1"}

def verify_record(record, key):
    expected = sign_record(record["payload"], key)
    pdf_valid = True
    if "pdf_sha256" in record or "pdf_signature" in record:
        digest = str(record.get("pdf_sha256", ""))
        pdf_valid = len(digest) == 64 and hmac.compare_digest(
            str(record.get("pdf_signature", "")), sign_pdf(digest, key))
    return (pdf_valid and record.get("scheme") == expected["scheme"] and
            hmac.compare_digest(str(record.get("sha256", "")), expected["sha256"]) and
            hmac.compare_digest(str(record.get("signature", "")), expected["signature"]))


def sign_pdf(digest, key):
    return hmac.new(key, ("oculoedge-pdf:" + digest).encode("ascii"), hashlib.sha256).hexdigest()
