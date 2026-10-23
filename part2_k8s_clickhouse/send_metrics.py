#!/usr/bin/env python3
"""
send_metrics.py

Génère 10 lignes aléatoires de métriques de jobs et les insère dans la table
ClickHouse `job_metrics` via l'interface HTTP (port 8123), au format TabSeparated.

Configuration (variables d'environnement, toutes optionnelles) :
    CLICKHOUSE_URL       URL de ClickHouse        (défaut : http://localhost:8123)
    CLICKHOUSE_USER      utilisateur              (défaut : default)
    CLICKHOUSE_PASSWORD  mot de passe             (défaut : vide)
    CLICKHOUSE_DB        base de données          (défaut : default)

Usage :
    pip install requests
    python send_metrics.py
"""

import os
import random
import sys
from datetime import datetime, timedelta

import requests

# --- Configuration -----------------------------------------------------------

CLICKHOUSE_URL = os.getenv("CLICKHOUSE_URL", "http://localhost:8123")
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "test")
CLICKHOUSE_DB = os.getenv("CLICKHOUSE_DB", "default")

TABLE = "job_metrics"
NB_ROWS = 10
JOB_NAMES = ["etl-daily", "backup-db", "report-gen", "data-sync", "cleanup-logs"]


# --- Génération des données --------------------------------------------------

def generate_row() -> tuple:
    """Crée une ligne aléatoire : (job_id, timestamp, duration_sec, success)."""
    job_id = f"{random.choice(JOB_NAMES)}-{random.randint(1, 999):03d}"
    timestamp = datetime.now() - timedelta(seconds=random.randint(0, 24 * 3600))
    duration_sec = random.randint(1, 3600)
    success = random.random() < 0.8  # ~80 % de succès
    return job_id, timestamp, duration_sec, success


def to_tsv_line(row: tuple) -> str:
    """Convertit une ligne en texte TabSeparated (colonnes séparées par des tabulations)."""
    job_id, timestamp, duration_sec, success = row
    fields = [
        job_id,
        timestamp.strftime("%Y-%m-%d %H:%M:%S"),  # format attendu par DateTime
        str(duration_sec),
        "true" if success else "false",           # format texte du type Bool
    ]
    return "\t".join(fields)


# --- Communication avec ClickHouse -------------------------------------------

def run_query(query: str, data: str | None = None) -> str:
    """
    Envoie une requête à ClickHouse via HTTP POST.
    - La requête SQL passe dans le paramètre d'URL `query`.
    - Les données éventuelles (pour un INSERT) passent dans le corps de la requête.
    """
    response = requests.post(
        CLICKHOUSE_URL,
        params={"query": query, "database": CLICKHOUSE_DB},
        data=data.encode("utf-8") if data else None,
        auth=(CLICKHOUSE_USER, CLICKHOUSE_PASSWORD),
        timeout=10,
    )
    if response.status_code != 200:
        # ClickHouse renvoie le message d'erreur en texte brut dans le corps
        raise RuntimeError(f"ClickHouse a répondu {response.status_code} : {response.text.strip()}")
    return response.text


# --- Programme principal -----------------------------------------------------

def main() -> int:
    rows = [generate_row() for _ in range(NB_ROWS)]
    payload = "\n".join(to_tsv_line(row) for row in rows) + "\n"

    print(f"Envoi de {NB_ROWS} lignes vers {CLICKHOUSE_URL} ({CLICKHOUSE_DB}.{TABLE})")
    print(payload)

    try:
        run_query(f"INSERT INTO {TABLE} FORMAT TabSeparated", data=payload)
        total = run_query(f"SELECT count() FROM {TABLE}").strip()
    except requests.ConnectionError:
        print(f"Impossible de joindre ClickHouse sur {CLICKHOUSE_URL}. "
              "Le cluster tourne-t-il et le port est-il bien mappé ?", file=sys.stderr)
        return 1
    except RuntimeError as err:
        print(err, file=sys.stderr)
        return 1

    print(f"Insertion réussie. La table {TABLE} contient maintenant {total} lignes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
