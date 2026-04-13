from logic import full_mrp



#Dodawanie wartości przewidywanego popytu dla poszczególnych tygodni
#(tyle ile wprowadzimy, tyle będzie, dopóki będziemy wprowadzać liczby), otherwise przerwiemy dodawanie

popyt = []


while True:
    x = input("Podaj popyt (enter = stop): ")
    if x == "":
        break
    popyt.append(int(x))


try:
  wielkość_partii_ghp = int(input("Podaj wielkość partii GHP: "))
  na_stanie = int(input("Podaj ile jest na stanie: "))
except:
  print("Podano wartość nieliczbową")


# przykładowe dane bez wpisywania ręczengo (zakomentuj to co u góry ^)

popyt = [0,0,0,0,20,0,40,0,0,0]

zapasy = {
    "zapalniczka": 2,
    "obudowa": 10,
    "mechanizm": 5,
    "zbiornik": 10,
    "kółko": 30,
    "krzesiwo": 10
}

czasy = {
    "zapalniczka": 1,
    "obudowa": 2,
    "mechanizm": 2,
    "zbiornik": 2,
    "kółko": 1,
    "krzesiwo": 1
}

partie = {
    "zapalniczka": 30,
    "obudowa": 50,
    "mechanizm": 20,
    "zbiornik": 10,
    "kółko": 50,
    "krzesiwo": 40
}


wynik = full_mrp(popyt, zapasy, czasy, partie)   # ---> zwraca słownik, k - nazwa (np. planowane przyjęcie), v: listy z wartościami na każdy tydzień


# sposób na sensowny printing:

for produkt, dane in wynik.items():
    print("\n", produkt.upper())
    for k, v in dane.items():
        print(k, ":", v)


# print(wynik)           #---> ten słownik, jak chcesz zobaczyć raw strukturę
