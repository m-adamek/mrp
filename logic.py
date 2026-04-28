import math

# jeżeli produkcja to zapotrzebowanie netto to..:

def ghp(przewidywany_popyt, na_stanie, wielkość_partii):
    tydzień = len(przewidywany_popyt)
    produkcja = [0] * tydzień
    dostępne = [0] * tydzień
    poprzednio_dostępne = na_stanie

    for i in range(tydzień):
        if poprzednio_dostępne >= przewidywany_popyt[i]:
            produkcja[i] = 0
        else:
            zapotrzebowanie_netto = przewidywany_popyt[i] - poprzednio_dostępne
            produkcja[i] = zapotrzebowanie_netto

        dostępne[i] = poprzednio_dostępne + produkcja[i] - przewidywany_popyt[i]
        poprzednio_dostępne = dostępne[i]

    return produkcja, dostępne


# algorytm obliczający mrp dla elementu, dane do użycia w full_mrp
def mrp(całkowite_zapotrzebowanie, na_stanie, czas_realizacji, wielkość_partii):
    n = len(całkowite_zapotrzebowanie)

    planowane_przyjęcia = [0] * n
    przewidywane_na_stanie = [0] * n
    zapotrzebowanie_netto = [0] * n
    planowane_przyjęcie_zamówień = [0] * n
    planowane_zamówienia = [0] * n

    stan = na_stanie

    for i in range(n):

        # przyjęcia z wcześniejszych zamówień
        stan += planowane_przyjęcia[i] + planowane_przyjęcie_zamówień[i]

        if stan < całkowite_zapotrzebowanie[i]:
            brak = całkowite_zapotrzebowanie[i] - stan
            zapotrzebowanie_netto[i] = brak

            ilość = wielkość_partii

            release = i - czas_realizacji

            if release >= 0:
                # ✅ poprawny przypadek
                planowane_zamówienia[release] = ilość
                planowane_przyjęcie_zamówień[i] = ilość
                stan += ilość
            else:
                # ❗ brak możliwości zamówienia → brak dostawy
                # stan może być ujemny
                pass

        stan -= całkowite_zapotrzebowanie[i]
        przewidywane_na_stanie[i] = stan

    return {
        "Całkowite zapotrzebowanie": całkowite_zapotrzebowanie,
        "Planowane przyjęcia": planowane_przyjęcia,
        "Przewidywane na stanie": przewidywane_na_stanie,
        "Zapotrzebowanie netto": zapotrzebowanie_netto,
        "Planowane zamówienia": planowane_zamówienia,
        "Planowane przyjęcie zamówień": planowane_przyjęcie_zamówień
    }

def full_mrp(popyt, zapasy, czasy, partie):

    wyniki = {}

    #  GHP (produkt końcowy - zapalniczka)
    produkcja, _ = ghp(
        popyt["zapalniczka"], # (pobiera listę)
        zapasy["zapalniczka"],
        partie["zapalniczka"]
    )

    # MRP dla zapalniczki (POZIOM 0)
    mrp_zapalniczka = mrp(
        popyt["zapalniczka"],   
        zapasy["zapalniczka"],
        czasy["zapalniczka"],
        partie["zapalniczka"]
    )

    wyniki["zapalniczka"] = mrp_zapalniczka  #zapis wyników do słownika z wynikami

    # POZIOM 1 (BOM)
    parent_orders = mrp_zapalniczka["Planowane przyjęcie zamówień"]

    # obudowa
    mrp_obudowa = mrp(
        parent_orders,                     
        zapasy["obudowa"],
        czasy["obudowa"],
        partie["obudowa"]
    )
    wyniki["obudowa"] = mrp_obudowa

    # mechanizm
    mrp_mechanizm = mrp(
        parent_orders,
        zapasy["mechanizm"],
        czasy["mechanizm"],
        partie["mechanizm"]
    )
    wyniki["mechanizm"] = mrp_mechanizm

    # zbiornik
    mrp_zbiornik = mrp(
        parent_orders,
        zapasy["zbiornik"],
        czasy["zbiornik"],
        partie["zbiornik"]
    )
    wyniki["zbiornik"] = mrp_zbiornik

    # POZIOM 2 (z mechanizmu - kółko i krzesiwo)
    planowane_zamowienia_mechanizm = mrp_mechanizm["Planowane zamówienia"]

    zapotrzebowanie_kolko = [x * 1 for x in planowane_zamowienia_mechanizm]                 # *1 bo jeden element na jeden mechanizm
    zapotrzebowanie_krzesiwo = [x * 1 for x in planowane_zamowienia_mechanizm]

    mrp_kolko = mrp(
        zapotrzebowanie_kolko,
        zapasy["kółko"],
        czasy["kółko"],
        partie["kółko"]
    )
    wyniki["kółko"] = mrp_kolko

    mrp_krzesiwo = mrp(
        zapotrzebowanie_krzesiwo,
        zapasy["krzesiwo"],
        czasy["krzesiwo"],
        partie["krzesiwo"]
    )
    wyniki["krzesiwo"] = mrp_krzesiwo

    return wyniki


