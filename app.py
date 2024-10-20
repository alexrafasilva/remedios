from flask import Flask, render_template, request, redirect, url_for, jsonify
import time
import schedule
import threading

app = Flask(__name__)

# Lista global de remédios e horários
remedios = []

# Função para tocar alarme (notifica o frontend)
def tocar_alarme(remedio):
    hora_atual = time.strftime("%H:%M")
    print(f"Agora são {hora_atual}. Hora de tomar {remedio}.")

# Função para agendar o alarme
def agendar_alarme(horario, remedio):
    schedule.every().day.at(horario).do(tocar_alarme, remedio=remedio)

# Função para rodar agendamentos em paralelo
def rodar_agendamentos():
    while True:
        schedule.run_pending()
        time.sleep(60)

# Rota principal para visualizar e adicionar/remover/atualizar remédios
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        horario = request.form['horario']
        remedio = request.form['remedio']
        
        # Adicionar remédio à lista e agendar
        remedios.append({"horario": horario, "remedio": remedio})
        agendar_alarme(horario, remedio)
        
        return redirect(url_for('index'))
    
    return render_template('index.html', remedios=remedios)

# API para checar se algum alarme está agendado
@app.route('/check_alarm', methods=['GET'])
def check_alarm():
    hora_atual = time.strftime("%H:%M")
    for remedio in remedios:
        if remedio["horario"] == hora_atual:
            return jsonify({"alarme": True, "remedio": remedio["remedio"], "horario": remedio["horario"]})
    return jsonify({"alarme": False})

# Rota para deletar um remédio
@app.route('/remover/<int:remedio_id>', methods=['POST'])
def remover(remedio_id):
    remedios.pop(remedio_id)  # Remove pelo índice
    return redirect(url_for('index'))

# Rota para atualizar um remédio
@app.route('/atualizar/<int:remedio_id>', methods=['GET', 'POST'])
def atualizar(remedio_id):
    if request.method == 'POST':
        novo_horario = request.form['horario']
        novo_remedio = request.form['remedio']

        # Atualiza o remédio selecionado
        remedios[remedio_id] = {"horario": novo_horario, "remedio": novo_remedio}
        return redirect(url_for('index'))

    # Exibir formulário de atualização com os dados atuais
    remedio = remedios[remedio_id]
    return render_template('atualizar.html', remedio=remedio, remedio_id=remedio_id)

# Inicia a thread para rodar os agendamentos
if __name__ == "__main__":
    threading.Thread(target=rodar_agendamentos, daemon=True).start()
    app.run(debug=True)
