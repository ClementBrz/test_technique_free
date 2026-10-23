from pyinfra.operations import files, pip, systemd

APP_DIR = "/opt/metrics-collector"

# 1. Créer le dossier
files.directory(
    name="Créer le dossier de l'application",
    path=APP_DIR,
    mode="755",
)

# 2. Copier les fichiers
app = files.put(
    name="Copier le script",
    src="metrics_collector.py",
    dest=f"{APP_DIR}/metrics_collector.py",
    mode="644",
)

unit = files.put(
    name="Copier le fichier systemd",
    src="metrics-collector.service",
    dest="/etc/systemd/system/metrics-collector.service",
    mode="644",
)

# 3. Installer Flask dans un venv
pip.venv(
    name="Créer le venv",
    path=f"{APP_DIR}/.venv",
    python="/usr/bin/python3",
)

pip.packages(
    name="Installer Flask",
    packages=["flask"],
    virtualenv=f"{APP_DIR}/.venv",
)

# 4. Recharger systemd (seulement si le .service a changé) et démarrer
systemd.daemon_reload(
    name="Recharger systemd",
    _if=unit.did_change,
)

systemd.service(
    name="Démarrer et activer le service",
    service="metrics-collector.service",
    running=True,
    enabled=True,
)

# 5. Redémarrer seulement si le script ou le .service a changé
systemd.service(
    name="Redémarrer si nécessaire",
    service="metrics-collector.service",
    restarted=True,
    _if=lambda: app.did_change() or unit.did_change(),
)
