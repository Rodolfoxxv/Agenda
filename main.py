import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import duckdb
import pandas as pd
import jwt
from flask import Flask, request, render_template, jsonify, abort

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "agenda.db"
JWT_SECRET = os.environ.get("INTEGRATION_JWT_SECRET", "change-this-secret")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = int(os.environ.get("INTEGRATION_JWT_EXP_MINUTES", "30"))
DEFAULT_INTEGRATION_USERNAME = os.environ.get("INTEGRATION_USERNAME", "integration")
DEFAULT_INTEGRATION_PASSWORD = os.environ.get("INTEGRATION_PASSWORD", "integration123")
INTEGRATION_USERS = (
    {DEFAULT_INTEGRATION_USERNAME: DEFAULT_INTEGRATION_PASSWORD}
    if DEFAULT_INTEGRATION_USERNAME
    else {}
)


def get_connection() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(DB_PATH))


def ensure_tables() -> None:
    with get_connection() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS agenda (
                "Dia da Semana" VARCHAR,
                "Mês" VARCHAR,
                "Ano" VARCHAR,
                "Atividade" VARCHAR,
                "Horário Planejado" VARCHAR,
                "Horário Planejado Concluído" VARCHAR,
                "Horário Real Início" VARCHAR,
                "Horário Real Final" VARCHAR,
                "Tarefa Concluída" VARCHAR,
                "Nível de Energia" VARCHAR
            )
            """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS integration_events (
                id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                received_at TIMESTAMP NOT NULL,
                payload JSON NOT NULL
            )
            """
        )


ensure_tables()

app = Flask(__name__)


def generate_token(username: str) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    payload = {"sub": username, "exp": expiration}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_bearer_token() -> str:
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        abort(401, description="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        abort(401, description=f"Token expired: {exc}")
    except jwt.InvalidTokenError as exc:
        abort(401, description=f"Invalid token: {exc}")
    return decoded["sub"]

@app.route('/', methods=['GET', 'POST'])
def home():
    with get_connection() as con:
        if request.method == 'POST':
            atividade = request.form.get('atividade')
            horario_planejado = request.form.get('horario_planejado')
            if atividade and horario_planejado:
                now = datetime.now()
                nova_atividade = pd.DataFrame({
                    'Dia da Semana': [now.strftime('%A')],
                    'Mês': [now.strftime('%B')],
                    'Ano': [now.strftime('%Y')],
                    'Atividade': [atividade],
                    'Horário Planejado': [horario_planejado],
                    'Horário Planejado Concluído': [None],
                    'Horário Real Início': [None],
                    'Horário Real Final': [None],
                    'Tarefa Concluída': [None],
                    'Nível de Energia': [None]
                })
                con.register('nova_atividade', nova_atividade)
                con.execute('INSERT INTO agenda SELECT * FROM nova_atividade')
        agenda = con.execute('SELECT * FROM agenda').fetchdf()
    return render_template('index.html', agenda=agenda)


@app.post('/integration/auth')
def integration_auth():
    data = request.get_json(silent=True) or {}
    username = data.get('username') or data.get('usuario')
    password = data.get('password') or data.get('senha')
    if not username or not password:
        return jsonify({'error': 'username and password are required'}), 400
    expected_password = INTEGRATION_USERS.get(username)
    if expected_password is None or expected_password != password:
        return jsonify({'error': 'invalid credentials'}), 401
    token = generate_token(username)
    return jsonify(
        {
            'access_token': token,
            'token_type': 'Bearer',
            'expires_in_minutes': JWT_EXPIRATION_MINUTES,
        }
    )


@app.post('/integration/events')
def receive_integration_event():
    username = verify_bearer_token()
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({'error': 'JSON body is required'}), 400
    with get_connection() as con:
        con.execute(
            'INSERT INTO integration_events (received_at, payload) VALUES (?, ?)',
            [
                datetime.now(timezone.utc),
                json.dumps(payload, ensure_ascii=False),
            ],
        )
    return jsonify({'status': 'accepted', 'processed_by': username}), 202


@app.get('/integration/events')
def list_integration_events():
    verify_bearer_token()
    with get_connection() as con:
        rows = con.execute(
            'SELECT id, received_at, payload FROM integration_events ORDER BY received_at DESC'
        ).fetchall()
    events = []
    for event_id, received_at, payload in rows:
        try:
            parsed_payload = json.loads(payload)
        except (TypeError, json.JSONDecodeError):
            parsed_payload = payload
        events.append(
            {
                'id': event_id,
                'received_at': received_at.isoformat() if received_at else None,
                'payload': parsed_payload,
            }
        )
    return jsonify({'events': events})

if __name__ == '__main__':
    app.run(debug=True)
