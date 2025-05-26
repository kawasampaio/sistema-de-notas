from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# Conexão com o MongoDB local (altere se estiver usando Atlas)
client = MongoClient("mongodb://localhost:27017/")
db = client['meu_banco']
usuarios_collection = db['usuarios']

@app.route('/')
def login():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    senha = request.form['senha']

    user = usuarios_collection.find_one({'username': username, 'senha': senha})

    if user:
        return redirect(url_for('painel'))
    else:
        return "Usuário ou senha inválidos. <a href='/'>Tentar novamente</a>"

@app.route('/painel')
def painel():
    projetos = list(collection.find())
    return render_template('painel.html', projetos=projetos)



@app.route('/success')
def success():
    return "Login realizado com sucesso!"

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        senha = request.form['senha']

        if usuarios_collection.find_one({'username': username}):
            return "Usuário já existe. <a href='/cadastro'>Tente outro nome</a>"

        usuarios_collection.insert_one({
            'username': username,
            'email': email,
            'senha': senha
        })

        return redirect(url_for('login'))
    
    return render_template('cadastro.html')



if __name__ == '__main__':
    app.run(debug=True)
