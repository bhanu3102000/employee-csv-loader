"""Small, configuration-driven CSV loader. Start with --dry-run."""
import argparse
import csv
import json
import os
from pathlib import Path
import re


def identifier(value):
    """Restrict SQL names; values are passed separately as parameters."""
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,127}", value):
        raise ValueError(f"Invalid SQL identifier: {value!r}")
    return f"[{value}]"


def odbc_value(value):
    return "{" + str(value).replace("}", "}}") + "}"


def read_source(config_path):
    config_path = Path(config_path).resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    source_path = Path(config["source"]["csv_path"])
    if not source_path.is_absolute():
        source_path = config_path.parent / source_path
    target = config["target"]
    table = identifier(target["schema"]) + "." + identifier(target["table"])
    with source_path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.reader(source)
        columns = next(reader, None)
        if not columns or len(set(columns)) != len(columns):
            raise ValueError("CSV needs nonempty, unique column headers")
        quoted_columns = [identifier(column) for column in columns]
        rows = []
        for line_number, row in enumerate(reader, 2):
            if len(row) != len(columns):
                raise ValueError(f"CSV line {line_number}: column count mismatch")
            if any(not value.strip() for value in row):
                raise ValueError(f"CSV line {line_number}: missing value")
            rows.append(tuple(row))
    sql = f"INSERT INTO {table} ({', '.join(quoted_columns)}) VALUES ({', '.join('?' for _ in columns)})"
    return target, source_path, rows, sql


def load(config_path, dry_run=False):
    target, source_path, rows, sql = read_source(config_path)
    print(f"Source: {source_path}")
    print(f"Target: {target['database']}.{target['schema']}.{target['table']}")
    print(f"Validated rows: {len(rows)}")
    if dry_run:
        print("Dry run complete. Database was not contacted.")
        return
    if not rows:
        print("No rows to load.")
        return
    import pyodbc  # Only needed when actually loading SQL Server.
    connection_string = (
        f"DRIVER={odbc_value(target['driver'])};"
        f"SERVER={odbc_value(target['server'])};"
        f"DATABASE={odbc_value(target['database'])};Encrypt=yes;"
        f"TrustServerCertificate={'yes' if target.get('trust_server_certificate', False) else 'no'};"
    )
    if target.get("windows_auth", True):
        connection_string += "Trusted_Connection=yes;"
    else:
        connection_string += (
            f"UID={odbc_value(os.environ['SQLSERVER_USERNAME'])};"
            f"PWD={odbc_value(os.environ['SQLSERVER_PASSWORD'])};"
        )
    connection = pyodbc.connect(connection_string, autocommit=False, timeout=15)
    try:
        cursor = connection.cursor()
        cursor.executemany(sql, rows)
        connection.commit()
        print(f"Loaded {len(rows)} rows successfully.")
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=str(Path(__file__).with_name("config.json")))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    load(args.config, args.dry_run)
