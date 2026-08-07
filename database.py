import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, Iterable

DB_PATH = Path(__file__).with_name('clinica.db')


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with closing(connect()) as connection, connection:
        connection.execute(
            '''
            CREATE TABLE IF NOT EXISTS pacientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                edad INTEGER NOT NULL CHECK (edad >= 0),
                tratamiento TEXT NOT NULL,
                proxima_cita TEXT
            )
            '''
        )

        existing_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(pacientes)").fetchall()
        }

        if "telefono" not in existing_columns:
            connection.execute(
                "ALTER TABLE pacientes ADD COLUMN telefono TEXT DEFAULT ''"
            )

        if "email" not in existing_columns:
            connection.execute(
                "ALTER TABLE pacientes ADD COLUMN email TEXT DEFAULT ''"
            )

        if "observaciones" not in existing_columns:
            connection.execute(
                "ALTER TABLE pacientes ADD COLUMN observaciones TEXT DEFAULT ''"
            )

        connection.execute(
            '''
            CREATE TABLE IF NOT EXISTS analisis_ia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente TEXT NOT NULL,
                fecha TEXT NOT NULL,
                sintomas TEXT NOT NULL,
                duracion TEXT,
                dolor INTEGER,
                antecedentes TEXT,
                fiebre INTEGER NOT NULL DEFAULT 0,
                inflamacion INTEGER NOT NULL DEFAULT 0,
                valoracion TEXT,
                prioridad TEXT,
                pruebas TEXT,
                alarmas TEXT,
                estado TEXT NOT NULL DEFAULT 'Pendiente'
            )
            '''
        )


def list_patients(search: str = '') -> list[sqlite3.Row]:
    with closing(connect()) as connection:
        if search:
            return connection.execute(
                '''
                SELECT
                    id,
                    nombre,
                    edad,
                    telefono,
                    email,
                    tratamiento,
                    proxima_cita,
                    observaciones
                FROM pacientes
                WHERE LOWER(nombre) LIKE ?
                ORDER BY nombre COLLATE NOCASE
                ''',
                (f'%{search.lower()}%',),
            ).fetchall()

        return connection.execute(
            '''
            SELECT
                id,
                nombre,
                edad,
                telefono,
                email,
                tratamiento,
                proxima_cita,
                observaciones
            FROM pacientes
            ORDER BY id
            '''
        ).fetchall()
def add_patient(
    nombre: str,
    edad: int,
    tratamiento: str,
    proxima_cita: str,
    telefono: str = '',
    email: str = '',
    observaciones: str = '',
) -> int:
    with closing(connect()) as connection, connection:
        cursor = connection.execute(
            '''
            INSERT INTO pacientes (
                nombre,
                edad,
                tratamiento,
                proxima_cita,
                telefono,
                email,
                observaciones
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                nombre,
                edad,
                tratamiento,
                proxima_cita,
                telefono,
                email,
                observaciones,
            ),
        )
        return int(cursor.lastrowid)


def update_patient(
    patient_id: int,
    nombre: str,
    edad: int,
    tratamiento: str,
    proxima_cita: str,
    telefono: str = "",
    email: str = "",
    observaciones: str = "",
) -> None:
    with closing(connect()) as connection, connection:
        connection.execute(
            '''
            UPDATE pacientes
            SET nombre=?,
                edad=?,
                tratamiento=?,
                proxima_cita=?,
                telefono=?,
                email=?,
                observaciones=?
            WHERE id=?
            ''',
            (
                nombre,
                edad,
                tratamiento,
                proxima_cita,
                telefono,
                email,
                observaciones,
                patient_id,
            ),
        )
def delete_patient(patient_id: int) -> None:
    with closing(connect()) as connection, connection:
        connection.execute('DELETE FROM pacientes WHERE id=?', (patient_id,))


def import_patients(records: Iterable[dict[str, Any]]) -> int:
    imported = 0
    with closing(connect()) as connection, connection:
        for record in records:
            nombre = str(record.get('nombre', '')).strip()
            tratamiento = str(record.get('tratamiento', '')).strip()
            if not nombre or not tratamiento:
                continue
            try:
                edad = int(record.get('edad', 0))
            except (TypeError, ValueError):
                continue
            connection.execute(
                '''
                INSERT INTO pacientes (nombre, edad, tratamiento, proxima_cita)
                VALUES (?, ?, ?, ?)
                ''',
                (nombre, edad, tratamiento, str(record.get('proxima_cita', '')).strip()),
            )
            imported += 1
    return imported


def patient_stats() -> dict[str, Any]:
    with closing(connect()) as connection:
        total = connection.execute('SELECT COUNT(*) FROM pacientes').fetchone()[0]
        avg_age = connection.execute('SELECT AVG(edad) FROM pacientes').fetchone()[0]
        minors = connection.execute('SELECT COUNT(*) FROM pacientes WHERE edad < 18').fetchone()[0]
        adults = connection.execute('SELECT COUNT(*) FROM pacientes WHERE edad >= 18').fetchone()[0]
        frequent = connection.execute(
            '''
            SELECT tratamiento, COUNT(*) AS cantidad
            FROM pacientes
            GROUP BY tratamiento
            ORDER BY cantidad DESC, tratamiento
            LIMIT 1
            '''
        ).fetchone()
    return {
        'total': total,
        'avg_age': avg_age or 0,
        'minors': minors,
        'adults': adults,
        'frequent_treatment': frequent['tratamiento'] if frequent else 'Sin datos',
    }


def add_analysis(data: dict[str, Any]) -> int:
    with closing(connect()) as connection, connection:
        cursor = connection.execute(
            '''
            INSERT INTO analisis_ia (
                paciente, fecha, sintomas, duracion, dolor, antecedentes,
                fiebre, inflamacion, valoracion, prioridad, pruebas, alarmas, estado
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                data['paciente'], data['fecha'], data['sintomas'], data.get('duracion', ''),
                data.get('dolor'), data.get('antecedentes', ''), int(bool(data.get('fiebre'))),
                int(bool(data.get('inflamacion'))), data.get('valoracion', ''),
                data.get('prioridad', ''), data.get('pruebas', ''), data.get('alarmas', ''),
                data.get('estado', 'Pendiente'),
            ),
        )
        return int(cursor.lastrowid)


def list_analyses(state: str = 'Todos', patient_search: str = '') -> list[sqlite3.Row]:
    clauses: list[str] = []
    params: list[Any] = []
    if state != 'Todos':
        clauses.append('estado = ?')
        params.append(state)
    if patient_search:
        clauses.append('LOWER(paciente) LIKE ?')
        params.append(f'%{patient_search.lower()}%')
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ''
    with closing(connect()) as connection:
        return connection.execute(
            f'''
            SELECT id, paciente, fecha, prioridad, estado
            FROM analisis_ia
            {where}
            ORDER BY id DESC
            ''',
            params,
        ).fetchall()


def get_analysis(analysis_id: int) -> sqlite3.Row | None:
    with closing(connect()) as connection:
        return connection.execute(
            'SELECT * FROM analisis_ia WHERE id=?', (analysis_id,)
        ).fetchone()


def update_analysis_state(analysis_id: int, new_state: str) -> None:
    if new_state not in {'Pendiente', 'Validado', 'Rechazado'}:
        raise ValueError('Estado no válido')
    with closing(connect()) as connection, connection:
        connection.execute(
            'UPDATE analisis_ia SET estado=? WHERE id=?',
            (new_state, analysis_id),
        )


def analysis_counts() -> dict[str, int]:
    with closing(connect()) as connection:
        rows = connection.execute(
            'SELECT estado, COUNT(*) AS cantidad FROM analisis_ia GROUP BY estado'
        ).fetchall()
        counts = {'Pendiente': 0, 'Validado': 0, 'Rechazado': 0}
        for row in rows:
            counts[row['estado']] = row['cantidad']
        counts['Total'] = sum(counts.values())
        return counts
