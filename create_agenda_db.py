import duckdb
import pandas as pd

# Inicialize o DuckDB no diretório especificado
con = duckdb.connect('C:/Users/rodol/OneDrive/Documents/GitHub/Agenda/agenda.db')

# Crie a tabela agenda se ela não existir
con.execute("""
CREATE TABLE IF NOT EXISTS agenda (
    "Dia da Semana" VARCHAR,
    "Atividade" VARCHAR,
    "Horário Planejado" VARCHAR,
    "Horário Planejado Concluído" VARCHAR,
    "Horário Real Início" VARCHAR,
    "Horário Real Final" VARCHAR,
    "Tarefa Concluída" VARCHAR,
    "Nível de Energia" VARCHAR
)
""")

# Crie um DataFrame pandas com a estrutura da sua agenda
agenda = pd.DataFrame({
    'Dia da Semana': ['Segunda-feira', 'Segunda-feira'],
    'Atividade': ['Trabalho', 'Academia'],
    'Horário Planejado': ['8:00', '15:30'],
    'Horário Planejado Concluído': [None, None],
    'Horário Real Início': [None, None],
    'Horário Real Final': [None, None],
    'Tarefa Concluída': [None, None],
    'Nível de Energia': [None, None]
})

# Insira os dados do DataFrame na tabela
for index, row in agenda.iterrows():
    con.execute("""
    INSERT INTO agenda VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, row.tolist())

print("Banco de dados e tabela criados com sucesso!")
