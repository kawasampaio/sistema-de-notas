from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# Conexão com o MongoDB local
client = MongoClient("mongodb://localhost:27017/")
db = client["notasfacil"]
usuarios = db["usuarios"]

@app.route("/")
def login():
    return render_template("index.html", erro=None)

@app.route("/cadastro")
def cadastro():
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

if __name__ == "__main__":
    app.run(debug=True)
