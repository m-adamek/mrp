from flask import Flask, render_template, request, jsonify
from logic import ghp, mrp, full_mrp

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


# z tego lecą wyniki pełne (w test.py możesz sprawdzić jak wygląda output):

@app.route("/full_mrp", methods=["POST"])
def full_mrp_api():
    data = request.json

    wynik = full_mrp(
        data["popyt"],
        data["zapasy"],
        data["czasy"],
        data["partie"]
    )

    return jsonify(wynik)



if __name__ == "__main__":
    app.run(debug=True)