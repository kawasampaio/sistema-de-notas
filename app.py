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
        return redirect(url_for('login'))

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
        serie = request.form['serie']
        materia = request.form['materia']
        data = datetime.now().strftime("%d/%m/%Y")

        projetos.insert_one({
            "usuario_id": usuario_id,
            "turma": turma,
            "titulo": titulo,
            "serie": serie,
            "materia": materia,
            "data_ultima_edicao": data
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

def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def calcular_media(n1,n2, n3, n4,):

    soma_notas = n1  + n2 + n3  + n4 
    return round(soma_notas / 4)

@app.route("/projeto/<id>", methods=["GET", "POST"])
def projeto_detalhes(id):
    projeto = projetos.find_one({"_id": ObjectId(id)})

    if request.method == "POST":
        alunos = []
        for i in range(10):
            nome = request.form.get(f"aluno_{i}")
            if nome:
                nota1 = to_float(request.form.get(f"nota1_{i}"))       
                nota2 = to_float(request.form.get(f"nota2_{i}"))            
                nota3 = to_float(request.form.get(f"nota3_{i}"))               
                nota4 = to_float(request.form.get(f"nota4_{i}"))              

                media = calcular_media(nota1,nota2,nota3,nota4)

                alunos.append({
                    "nome": nome,
                    "nota1": nota1, 
                    "nota2": nota2, 
                    "nota3": nota3, 
                    "nota4": nota4, 
                    "media": media
                })

        projetos.update_one({"_id": ObjectId(id)}, {"$set": {"alunos": alunos}})
        return redirect(url_for("projeto_detalhes", id=id))

    return render_template("projeto_detalhes.html", projeto=projeto)

@app.route('/gerar-boletim', methods=['GET', 'POST'])
def boletim_completo():
    if request.method == 'POST':
        aluno = request.form['aluno'].strip().lower()
        turma = request.form['turma'].strip().lower()
        serie = request.form['serie'].strip()
        bimestre = request.form['bimestre'].strip()
        ano = request.form['ano'].strip()

        boletim = []
        cursor = projetos.find({
            'turma': turma,
            'serie': serie,
            'titulo': bimestre
        })

        for doc in cursor:
            aluno_info = next((a for a in doc.get('alunos', [])
                               if a['nome'].strip().lower() == aluno), None)
            if aluno_info:
                nota = aluno_info.get(f'nota{bimestre}', 0)
                conceito = (
                    "MB" if nota >= 9 else
                    "B" if nota >= 7 else
                    "R" if nota >= 5 else
                    "PF"
                )
                boletim.append({
                    'disciplina': doc['materia'],
                    'nota': nota,
                    'conceito': conceito
                })

        if not boletim:
            return render_template('boletim.html', erro="Aluno ou dados não encontrados.")

        return render_template('boletim_visual.html', aluno=aluno.title(), turma=turma,
                               serie=serie, ano=ano, bimestre=bimestre, boletim=boletim)

    return render_template('boletim.html')


if __name__ == '__main__':
    app.run(debug=True)
