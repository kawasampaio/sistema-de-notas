from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    resultado = None
    if request.method == "POST":
        nome = request.form["nome"]
        disciplina = request.form["disciplina"]
        nota = float(request.form["nota"])
        peso = float(request.form["peso"])

        media = nota * peso  # simplificado (apenas uma nota por enquanto)
        aprovado = "Aprovado" if media >= 6 else "Reprovado"

        resultado = {
            "nome": nome,
            "disciplina": disciplina,
            "media": round(media, 2),
            "status": aprovado
        }

    return render_template("index.html", resultado=resultado)

if __name__ == "__main__":
    app.run(debug=True)
