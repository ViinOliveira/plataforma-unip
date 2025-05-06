from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import hashlib
import statistics
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'segredo123'

ARQUIVO_DADOS = 'usuarios.json'

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []


def salvar_dados(usuarios):
    with open(ARQUIVO_DADOS, 'w') as f:
        json.dump(usuarios, f, indent=4)

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        idade = int(request.form['idade'])
        email = request.form['email']
        senha = hash_senha(request.form['senha'])

        usuarios = carregar_dados()
        if any(u['email'] == email for u in usuarios):
            return "Email já cadastrado."

        novo = {
            'nome': nome,
            'idade': idade,
            'email': email,
            'senha': senha,
            'acessos': []
        }
        usuarios.append(novo)
        salvar_dados(usuarios)
        return redirect(url_for('login'))

    return render_template('cadastro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = hash_senha(request.form['senha'])
        usuarios = carregar_dados()

        for u in usuarios:
            if u['email'] == email and u['senha'] == senha:
                session['usuario'] = u['nome']
                u['acessos'].append('conteudo')
                salvar_dados(usuarios)
                return redirect(url_for('conteudo'))

        return "Login inválido."

    return render_template('login.html')

@app.route('/meu_historico')
def meu_historico():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuarios = carregar_dados()
    acessos = []
    for u in usuarios:
        if u['nome'] == session['usuario']:
            acessos = u.get('acessos', [])
            break

    return render_template('historico.html', acessos=acessos, nome=session['usuario'])


@app.route('/conteudo')
def conteudo():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    usuarios = carregar_dados()
    for u in usuarios:
        if u['nome'] == session['usuario']:
            u['acessos'].append(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
            break
    salvar_dados(usuarios)

    return render_template('conteudo.html', nome=session['usuario'])

@app.route('/estatisticas')
def estatisticas():
    usuarios = carregar_dados()
    idades = [u['idade'] for u in usuarios]

    if not idades:
        return "Sem dados suficientes."

    media = round(statistics.mean(idades), 2)
    mediana = statistics.median(idades)
    try:
        moda = statistics.mode(idades)
    except:
        moda = "Sem moda"
    desvio = round(statistics.stdev(idades), 2) if len(idades) > 1 else 0
    idade_min = min(idades)
    idade_max = max(idades)
    total = len(idades)

    return render_template("estatisticas.html", media=media, mediana=mediana, moda=moda,
                           desvio=desvio, idade_min=idade_min, idade_max=idade_max, total=total)


@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)