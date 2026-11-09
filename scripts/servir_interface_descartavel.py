"""Servidor de demonstração com SQLite temporário, sem tocar no banco da equipe."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--port", type=int, default=8000)
args = parser.parse_args()
root = Path(__file__).resolve().parent.parent

with tempfile.TemporaryDirectory(prefix="catalogo-interface-") as directory:
    settings = Path(directory) / "interface_descartavel.py"
    database = str(Path(directory) / "db.sqlite3")
    settings.write_text(
        "from config.settings import *\n"
        "DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', "
        f"'NAME': {database!r}}}}}\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([directory, str(root)])
    env["DJANGO_SETTINGS_MODULE"] = "interface_descartavel"
    subprocess.run([sys.executable, "manage.py", "migrate", "--noinput"], cwd=root, env=env, check=True)
    print(f"Interface descartável: http://127.0.0.1:{args.port}/catalogo/", flush=True)
    try:
        subprocess.run(
            [sys.executable, "manage.py", "runserver", f"127.0.0.1:{args.port}", "--noreload"],
            cwd=root, env=env, check=True,
        )
    except KeyboardInterrupt:
        pass
