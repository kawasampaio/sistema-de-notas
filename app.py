from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from werkzeug.security import check_password_hash
from bson.objectid import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = 'seu_segredo_aqui'

# Configuração do MongoDB
app.config["MONGO_URI"] = "mongodb://localhost:27017/professor_app"
mongo = PyMongo(app)

# Página inicial (login)
@app.route('/login', methods=['GET'])
def login_page():
    return render_template('index.html', erro=None)

# Processa login
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('username')
    senha = request.form.get('password')

    usuario = mongo.db.usuarios.find_one({'email': email})

    if usuario and check_password_hash(usuario['senha'], senha):
        session['usuario'] = str(usuario['_id'])
        return redirect(url_for('home'))
    else:
        return render_template('index.html', erro="Usuário ou senha inválidos")

# Página principal após login
@app.route('/')
def home():
    if 'usuario' in session:
        usuario = mongo.db.usuarios.find_one({'_id': ObjectId(session['usuario'])})
        return f"Bem-vindo, {usuario['nome']}!"
    return redirect(url_for('login_page'))

# Página de cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')

        if mongo.db.usuarios.find_one({'email': email}):
            return "Usuário já cadastrado."

        senha_hash = generate_password_hash(senha)
        mongo.db.usuarios.insert_one({
            'nome': nome,
            'email': email,
            'senha': senha_hash,
            'criado_em': datetime.now()
        })
        return redirect(url_for('login_page'))

    return render_template('cadastro.html')

if __name__ == '__main__':
    app.run(debug=True)
