from flask import Flask, render_template, request, redirect, url_for, session
import csv

from codigo import calcular_rota, ler_enderecos

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'fabianamoveis' and password == 'fab123':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return "Credenciais inválidas. Tente novamente."
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/home')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/cadastrar_entregas', methods=['GET', 'POST'])
def cadastrar_entregas():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        rua = request.form['rua']
        numero = request.form['numero']
        bairro = request.form['bairro']
        cidade = request.form['cidade']
        estado = request.form['estado']
        with open('enderecos.csv', mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([rua, numero, bairro, cidade, estado])
        return "Endereço cadastrado com sucesso!"
    return render_template('cadastrar_entregas.html')

@app.route('/criar_rota')
def criar_rota():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    enderecos = ler_enderecos('enderecos.csv')
    origem = enderecos[0]
    destino = enderecos[-1]
    paradas = enderecos[1:-1]
    resultado = calcular_rota(origem, destino, paradas)
    return render_template('mapa.html', resultado=resultado)

@app.route('/gerar_relatorios')
def gerar_relatorios():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return "Página de Geração de Relatórios"

@app.route('/ver_rotas_recentes')
def ver_rotas_recentes():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return "Página de Rotas Recentes"

if __name__ == '__main__':
    app.run(debug=True)