import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / 'instance' / 'oficina.db'


def column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    cur = conn.execute(f'PRAGMA table_info({table})')
    cols = [row[1] for row in cur.fetchall()]
    return column in cols


def main():
    if not DB_PATH.exists():
        raise SystemExit(f"Banco não encontrado: {DB_PATH}")

    conn = sqlite3.connect(str(DB_PATH))
    try:
        # Garantir coluna 'pago' em servicos
        if not column_exists(conn, 'servicos', 'pago'):
            conn.execute(
                "ALTER TABLE servicos ADD COLUMN pago BOOLEAN NOT NULL DEFAULT 0"
            )
            conn.commit()
            print("OK: coluna 'servicos.pago' adicionada.")
        else:
            print("OK: coluna 'servicos.pago' já existe. Nada a fazer.")

        # (Opcional, mas comum) Garantir colunas extras do modelo caso faltem.
        # Se você NÃO quiser, pode remover.
        if not column_exists(conn, 'servicos', 'data_pagamento'):
            conn.execute("ALTER TABLE servicos ADD COLUMN data_pagamento DATETIME NULL")
            conn.commit()
            print("OK: coluna 'servicos.data_pagamento' adicionada.")

        if not column_exists(conn, 'servicos', 'bonus_aplicado'):
            conn.execute("ALTER TABLE servicos ADD COLUMN bonus_aplicado TEXT NULL")
            conn.commit()
            print("OK: coluna 'servicos.bonus_aplicado' adicionada.")

        if not column_exists(conn, 'servicos', 'mecanico_id'):
            conn.execute("ALTER TABLE servicos ADD COLUMN mecanico_id INTEGER NULL")
            conn.commit()
            print("OK: coluna 'servicos.mecanico_id' adicionada.")

    finally:
        conn.close()


if __name__ == '__main__':
    main()

