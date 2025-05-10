from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import bcrypt
from bson.objectid import ObjectId


app = Flask(__name__)

# Conexão com o MongoDB local
client = MongoClient("mongodb://localhost:27017/")
db = client["notasfacil"]
usuarios = db["usuarios"]

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        senha = request.form.get("senha").encode('utf-8')

        usuario = usuarios.find_one({
            "$or": [{"nome": username}, {"email": username}]
        })

        if usuario and bcrypt.checkpw(senha, usuario["senha"]):
            return redirect(url_for("pagina_inicial"))
        else:
            erro = "Senha ou usuário incorretos"
            return render_template("index.html", erro=erro)

    return render_template("index.html", erro=None)


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha").encode('utf-8')
        hashed = bcrypt.hashpw(senha, bcrypt.gensalt())


        if not nome or not email or not senha:
            return "Preencha todos os campos"

        usuarios.insert_one({
            "nome": nome,
            "email": email,
            "senha": senha
        })

        return redirect(url_for("login"))
    
    return render_template("cadastro.html")



@app.route("/registrar", methods=["POST"])
def registrar():
    nome = request.form["nome"]
    email = request.form["email"]
    senha = request.form["senha"]

    usuarios.insert_one({"nome": nome, "email": email, "senha": senha})
    return redirect(url_for("login"))

@app.route("/autenticar", methods=["POST"])
def autenticar():
    username = request.form["username"]
    senha = request.form["senha"]

    user = usuarios.find_one({
        "$or": [{"nome": username}, {"email": username}],
        "senha": senha
    })

    if user:
        return "Login realizado com sucesso!"  # Ou redirecione para outra página
    else:
        return render_template("index.html", erro="Senha ou username incorretos")
    
@app.route("/home")
def pagina_inicial():
    user_id = session.get("user_id")
    projeto = db.projetos.find_one({"usuario_id": user_id}, sort=[("data_modificacao", -1)])
    return render_template("home.html", projeto=projeto)

@app.route("/continuar/<id>")
def continuar_projeto(id):
    projeto = db.projetos.find_one({"_id": ObjectId(id)})
    # Redireciona para a rota de edição do tipo correto
    if projeto["tipo"] == "notas":
        return redirect(url_for("inserir_notas", id=id))
    elif projeto["tipo"] == "grafico":
        return redirect(url_for("visualizar_grafico", id=id))
    # etc.
    return redirect(url_for("pagina_inicial"))


if __name__ == "__main__":
    app.run(debug=True)


