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
    tydzień = len(całkowite_zapotrzebowanie)

    planowane_przyjęcia = [0] * tydzień
    przewidywane_na_stanie = [0] * tydzień
    zapotrzebowanie_netto = [0] * tydzień
    planowane_przyjęcie_zamówień = [0] * tydzień
    planowane_zamówienia = [0] * tydzień

    poprzedni_stan = na_stanie

    for i in range(tydzień):
        przewidywane_na_stanie[i] = poprzedni_stan + planowane_przyjęcia[i] + planowane_przyjęcie_zamówień[i] - całkowite_zapotrzebowanie[i]


        if przewidywane_na_stanie[i] < 0:
            zapotrzebowanie_netto[i] = abs(przewidywane_na_stanie[i])      #abs(-15) = 15

            ilość = math.ceil(zapotrzebowanie_netto[i] / wielkość_partii) * wielkość_partii

            planowane_przyjęcie_zamówień[i] = ilość
            przewidywane_na_stanie[i] += ilość

            if i - czas_realizacji >= 0:
                planowane_zamówienia[i - czas_realizacji] = ilość

        poprzedni_stan = przewidywane_na_stanie[i]

    return {
        "Całkowite zapotrzebowanie": całkowite_zapotrzebowanie,
        "Planowane przyjęcia": planowane_przyjęcia,
        "Przewidywane na stanie": przewidywane_na_stanie,
        "Zapotrzebowanie netto": zapotrzebowanie_netto,
        "Planowane przyjęcie zamówień": planowane_przyjęcie_zamówień,
        "Planowane zamówienia": planowane_zamówienia
    }


# algorytm używający algorytmu mrp i ghp do uzyskania ostatecznych wyników dla każdego z elementów

def full_mrp(popyt, zapasy, czasy, partie):

    wyniki = {}

    #  GHP (produkt końcowy - zapalniczka)
    produkcja, _ = ghp(
        popyt,
        zapasy["zapalniczka"],
        partie["zapalniczka"]
    )

    # MRP dla zapalniczki (POZIOM 0)
    mrp_zapalniczka = mrp(
        produkcja,
        zapasy["zapalniczka"],
        czasy["zapalniczka"],
        partie["zapalniczka"]
    )

    wyniki["zapalniczka"] = mrp_zapalniczka  #zapis wyników do słownika z wynikami

    # POZIOM 1 (BOM)
    parent_orders = mrp_zapalniczka["Planowane zamówienia"]

    # obudowa
    mrp_obudowa = mrp(
        parent_orders,                     #idk jak to przetłumaczyć i czy warto xD
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


