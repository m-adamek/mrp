from flask import Flask, render_template, request, jsonify
from logic import ghp, mrp, full_mrp
import os
import json
import csv


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

# json przez html

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    data = json.load(file)

    wyniki = full_mrp(
        data["popyt"],
        data["zapasy"],
        data["czasy"],
        data["partie"]
    )

    return wyniki 

# json jako plik w folderze projektu

# def load_data_from_file(path="data.json"):
#     with open(path, "r", encoding="utf-8") as f:
#         data = json.load(f)
#     return data

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
