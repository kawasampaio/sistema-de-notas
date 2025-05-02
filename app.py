from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    if request.method == "POST":
        try:
            nome = request.form.get("nome", "")
            disciplina = request.form.get("disciplina", "")
            nota = float(request.form.get("nota", 0))
            peso = float(request.form.get("peso", 1))

            media = nota * peso  # Exemplo simples
            aprovado = "Aprovado" if media >= 6 else "Reprovado"

            resultado = {
                "nome": nome,
                "disciplina": disciplina,
                "media": round(media, 2),
                "status": aprovado
            }
        except Exception as e:
            resultado = {"erro": f"Ocorreu um erro: {e}"}

    return render_template("index.html", resultado=resultado)

if __name__ == "__main__":
    app.run(debug=True)
