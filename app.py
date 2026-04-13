from flask import Flask, render_template, request, jsonify
from logic import ghp, mrp

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ghp", methods=["POST"])
def ghp_api():
    data = request.json

    produkcja, dostępne = ghp(
        data["popyt"],
        data["na_stanie"],
        data.get("partia", None)
    )

    return jsonify({
        "produkcja": produkcja,
        "dostępne": dostępne
    })


@app.route("/mrp", methods=["POST"])
def mrp_api():
    data = request.json

    wynik = mrp(
        data["zapotrzebowanie"],
        data["na_stanie"],
        data["czas_realizacji"],
        data["partia"]
    )

    return jsonify(wynik)




if __name__ == "__main__":
    app.run(debug=True)