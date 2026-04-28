from flask import Flask, render_template, request, jsonify, send_file
from logic import ghp, mrp, full_mrp
import os
import pandas as pd
import io

app = Flask(__name__)


# 
def clean_series(series):
    return [x if x != 0 else "" for x in series]


# 
def format_output(wynik):
    kolejność = [
        "Całkowite zapotrzebowanie",
        "Planowane przyjęcia",
        "Przewidywane na stanie",
        "Zapotrzebowanie netto",
        "Planowane zamówienia",
        "Planowane przyjęcie zamówień"
    ]

    formatted = {}

    for produkt, dane in wynik.items():
        formatted[produkt] = {}

        for key in kolejność:
            if key in dane:
                formatted[produkt][key] = clean_series(dane[key])
            else:
                # jeśli czegoś brak → pusta linia
                length = len(next(iter(dane.values())))
                formatted[produkt][key] = [""] * length

    return formatted


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

    return jsonify(format_output({"mrp": wynik})["mrp"])


# 
@app.route("/full_mrp", methods=["POST"])
def full_mrp_api():
    data = request.json

    popyt = data["popyt"]

    if isinstance(popyt, list):
        popyt = {"zapalniczka": popyt}

    wynik = full_mrp(
        popyt,
        data["zapasy"],
        data["czasy"],
        data["partie"]
    )

    return jsonify(format_output(wynik))


@app.route("/download-template")
def download_template():
    path = "static/szablon_mrp.xlsx"
    return send_file(
        path,
        as_attachment=True,
        download_name="Szablon_Danych_MRP.xlsx"
    )


# 
def safe_int(value):
    return int(value) if pd.notnull(value) else 0


@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "Brak pliku"}), 400

    file = request.files["file"]

    try:
        df_ghp = pd.read_excel(file, sheet_name='Popyt produktu (GHP)')
        df_bom = pd.read_excel(file, sheet_name='Parametry MRP (BOM)')

        # 🔥 bardziej odporne na nazwy
        kolumny_tygodni = [col for col in df_ghp.columns if 'tyd' in str(col).lower()]
        liczba_tygodni = len(kolumny_tygodni)

        popyt_glowny = [
            safe_int(df_ghp.iloc[0][tydz]) for tydz in kolumny_tygodni
        ]

        popyt_wszystkie = {}
        zapasy = {}
        czasy = {}
        partie = {}

        for _, row in df_bom.iterrows():
            raw = str(row['Część']).strip().lower()

            
            if "zapalniczka" in raw:
                nazwa = "zapalniczka"
                popyt_wszystkie[nazwa] = popyt_glowny
            elif "obudowa" in raw:
                nazwa = "obudowa"
            elif "mechanizm" in raw:
                nazwa = "mechanizm"
            elif "zbiornik" in raw:
                nazwa = "zbiornik"
            elif "kółko" in raw or "kolko" in raw:
                nazwa = "kółko"
            elif "krzesiwo" in raw:
                nazwa = "krzesiwo"
            else:
                continue

            if nazwa != "zapalniczka":
                popyt_wszystkie[nazwa] = [0] * liczba_tygodni

            zapasy[nazwa] = safe_int(row['Na stanie'])
            czasy[nazwa] = safe_int(row['Czas realizacji'])
            partie[nazwa] = safe_int(row['Wielkość partii'])

        wyniki = full_mrp(popyt_wszystkie, zapasy, czasy, partie)

        return jsonify(format_output(wyniki))

    except Exception as e:
        return jsonify({"error": f"Błąd: {str(e)}"}), 500


@app.route("/export", methods=["POST"])
def export_results():
    data = request.json
    if not data:
        return jsonify({"error": "Brak danych do eksportu"}), 400

    output = io.BytesIO()

    try:
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for produkt, info in data.items():
                df = pd.DataFrame(info)

                liczba_tygodni = len(df.columns)
                nazwy_kolumn = [f"Tydzień {i+1}" for i in range(liczba_tygodni)]

                df.columns = nazwy_kolumn
                df.to_excel(writer, sheet_name=str(produkt)[:31])

        output.seek(0)
        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="wyniki_mrp.xlsx"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        debug=True
    )