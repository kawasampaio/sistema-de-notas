from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId


app = Flask(__name__)
app.secret_key = "alguma_chave_secreta"

# Conexão com o MongoDB local (altere se estiver usando Atlas)
client = MongoClient("mongodb://localhost:27017/")
db = client['meu_banco']
usuarios_collection = db['usuarios']
projetos = db["projetos"]

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        senha = request.form['senha']

        usuario = usuarios_collection.find_one({'username': username, 'senha': senha})
        if usuario:
            session['usuario_id'] = str(usuario['_id'])  # ou session['username'] = username
            return redirect('/painel')
        else:
            return "Login inválido", 401
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    senha = request.form['senha']

    user = usuarios_collection.find_one({'username': username, 'senha': senha})

    if user:
        session['usuario_id'] = str(user['_id'])
        return redirect(url_for('painel'))
    else:
        return "Usuário ou senha inválidos. <a href='/'>Tentar novamente</a>"

@app.route('/painel')
def painel():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return redirect(url_for('login'))  # segurança: redireciona se não estiver logado
    lista_projetos = list(projetos.find({"usuario_id": usuario_id}))
    return render_template('painel.html', projetos=lista_projetos)


@app.route('/novo-projeto', methods=['GET', 'POST'])
def novo_projeto():
    if request.method == 'POST':
        usuario_id = session.get('usuario_id')
        if not usuario_id:
            return redirect(url_for('login'))

        turma = request.form['turma']
        titulo = request.form['titulo']
        data = datetime.now().strftime("%d/%m/%Y")
        
        projetos.insert_one({
            "usuario_id": usuario_id,
            "turma": turma,
            "titulo": titulo,
            "data": data
        })
        
        return redirect('/painel')
    
    return render_template('novo_projeto.html')



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

@app.route('/projeto/<id>', methods=['GET', 'POST'])
def detalhes_projeto(id):
    projeto = projetos.find_one({"_id": ObjectId(id)})

    if not projeto:
        return "Projeto não encontrado", 404

    if request.method == 'POST':
        alunos = []
        for i in range(10):
            nome = request.form.get(f"aluno_{i}")
            nota1 = request.form.get(f"nota1_{i}")
            peso1 = request.form.get(f"peso1_{i}")
            nota2 = request.form.get(f"nota2_{i}")
            peso2 = request.form.get(f"peso2_{i}")
            media = request.form.get(f"media_{i}")

            if nome:
                alunos.append({
                    "nome": nome,
                    "nota1": float(nota1 or 0),
                    "peso1": float(peso1 or 1),
                    "nota2": float(nota2 or 0),
                    "peso2": float(peso2 or 1),
                    "media": float(media or 0)
                })

        projetos.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"alunos": alunos}}
        )
        return redirect(url_for('detalhes_projeto', id=id))

    return render_template("projeto_detalhes.html", projeto=projeto)

if __name__ == '__main__':
    app.run(debug=True)
