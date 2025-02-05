from flask import Flask, render_template
from codigo import calcular_rota, ler_enderecos

app = Flask(__name__)

@app.route('/')
def index():
    enderecos = ler_enderecos('enderecos.csv')
    origem = enderecos[0]
    destino = enderecos[-1]
    paradas = enderecos[1:-1]
    resultado = calcular_rota(origem, destino, paradas)
    return render_template('mapa.html', resultado=resultado)

if __name__ == '__main__':
    app.run(debug=True)