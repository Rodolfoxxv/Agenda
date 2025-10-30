from pathlib import Path

import duckdb
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'agenda.db'

with duckdb.connect(DB_PATH.as_posix()) as con:
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

    agenda = pd.DataFrame(
        {
            'Dia da Semana': ['Segunda-feira', 'Segunda-feira'],
            'Mês': ['Janeiro', 'Janeiro'],
            'Ano': ['2024', '2024'],
            'Atividade': ['Trabalho', 'Academia'],
            'Horário Planejado': ['8:00', '15:30'],
            'Horário Planejado Concluído': [None, None],
            'Horário Real Início': [None, None],
            'Horário Real Final': [None, None],
            'Tarefa Concluída': [None, None],
            'Nível de Energia': [None, None],
        }
    )

    con.register('agenda_seed', agenda)
    con.execute('DELETE FROM agenda')
    con.execute('INSERT INTO agenda SELECT * FROM agenda_seed')

print('Banco de dados e tabelas criados com sucesso!')
