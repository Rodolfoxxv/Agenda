import duckdb
import pandas as pd

# Inicialize o DuckDB no diretório especificado
con = duckdb.connect('C:/Users/rodol/OneDrive/Documents/GitHub/Agenda/agenda.db')

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

# Crie uma tabela no DuckDB a partir do DataFrame
con.register('agenda', agenda)

print("Banco de dados e tabela criados com sucesso!")
