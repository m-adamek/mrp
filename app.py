from flask import Flask, render_template, request, jsonify, send_file
from logic import ghp, mrp, full_mrp
import os
import json
import csv
import pandas as pd
import io


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

    popyt = data["popyt"]

    if isinstance(popyt, list):
        popyt = {"zapalniczka": popyt}

    wynik = full_mrp(
        popyt,
        data["zapasy"],
        data["czasy"],
        data["partie"]
    )

    return jsonify(wynik)
@app.route("/download-template")
def download_template():

    path = "static/szablon_mrp.xlsx"
    return send_file(
        path, 
        as_attachment=True, 
        download_name="Szablon_Danych_MRP.xlsx"
    )


@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "Brak pliku"}), 400
    
    file = request.files["file"]

    try:
        df_ghp = pd.read_excel(file, sheet_name='Popyt produktu (GHP)')
        df_bom = pd.read_excel(file, sheet_name='Parametry MRP (BOM)')

        kolumny_tygodni = [col for col in df_ghp.columns if 'Tydzień' in str(col)]
        liczba_tygodni = len(kolumny_tygodni)

        popyt_glowny = [int(df_ghp.iloc[0][tydz]) if pd.notnull(df_ghp.iloc[0][tydz]) else 0 for tydz in kolumny_tygodni]

        popyt_wszystkie = {}
        zapasy = {}
        czasy = {}
        partie = {}

        for _, row in df_bom.iterrows():
            nazwa = str(row['Część']).strip().lower()
            
            if "zapalniczka" in nazwa:
                popyt_wszystkie[nazwa] = popyt_glowny
            else:
                popyt_wszystkie[nazwa] = [0] * liczba_tygodni
            
            zapasy[nazwa] = int(row['Na stanie']) if 'Na stanie' in row else 0
            czasy[nazwa] = int(row['Czas realizacji'])
            partie[nazwa] = int(row['Wielkość partii'])


        wyniki = full_mrp(popyt_wszystkie, zapasy, czasy, partie)

        return jsonify(wyniki)

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
                # dataframe z wyników (pionowy)
                df = pd.DataFrame(info)
                
                liczba_tygodni = len(df)
                nazwy_kolumn = [f"Tydzień {i+1}" for i in range(liczba_tygodni)]
                
                df_horizontal = df.transpose()
                df_horizontal.columns = nazwy_kolumn
                
                sheet_name = str(produkt).capitalize()[:31]
                df_horizontal.to_excel(writer, sheet_name=sheet_name)
        output.seek(0)
        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name="wyniki_mrp.xlsx"
        )
    except Exception as e:
        print(f"Błąd eksportu: {e}")
        return jsonify({"error": str(e)}), 500




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
