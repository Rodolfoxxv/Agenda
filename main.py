from flask import Flask, request, render_template
import duckdb
import pandas as pd
from datetime import datetime

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    # Conecte-se ao banco de dados
    con = duckdb.connect('C:/Users/rodol/OneDrive/Documents/GitHub/Agenda/agenda.db')
    if request.method == 'POST':
        # Obtenha os dados do formulário
        atividade = request.form.get('atividade')
        horario_planejado = request.form.get('horario_planejado')
        # Os campos Dia da Semana, Mês e Ano são preenchidos automaticamente
        dia_da_semana = datetime.now().strftime('%A')
        mes = datetime.now().strftime('%B')
        ano = datetime.now().strftime('%Y')
        # Insira a nova atividade na agenda
        nova_atividade = pd.DataFrame({
            'Dia da Semana': [dia_da_semana],
            'Mês': [mes],
            'Ano': [ano],
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
    # Obtenha a agenda do banco de dados
    agenda = con.execute('SELECT * FROM agenda').fetchdf()
    # Feche a conexão com o banco de dados
    con.close()
    return render_template('index.html', agenda=agenda)

if __name__ == '__main__':
    app.run(debug=True)
