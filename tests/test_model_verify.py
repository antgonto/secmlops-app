"""Lab 6.1 — the serving app must refuse a tampered artifact (fail closed)."""
import os
import shutil
import subprocess
import sys


def test_tampered_model_is_refused(tmp_path):
    tampered = tmp_path / "model.safetensors"
    shutil.copy("model/model.safetensors", tampered)
    with open(tampered, "r+b") as f:
        f.seek(100)
        f.write(b"\x00")
    (tmp_path / "model.safetensors.sha256").write_text("0" * 64 + "  model.safetensors\n")
    (tmp_path / "model.safetensors.sig").write_text("bogus")
    (tmp_path / "cosign.pub").write_text("-----BEGIN PUBLIC KEY-----\nAAAA\n-----END PUBLIC KEY-----\n")
    env = dict(os.environ, MODEL_PATH=str(tampered), COSIGN_PUB=str(tmp_path / "cosign.pub"),
               VERIFY_MODEL="true", PYTHONPATH=os.getcwd())
    r = subprocess.run([sys.executable, "-c", "import src.serve"], env=env, capture_output=True, text=True)
    assert r.returncode != 0 and "MODEL-LOAD-DENIED" in (r.stdout + r.stderr)
