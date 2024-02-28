# Korosi-111313-PPDS2024-Zadanie-03
## Úlohy zadania
Stručný popis zadania v bodoch:
1) Znovu máme 2 typy vlákien. Vláčik (na húsenkovej dráhe) a N pasažierov
2) Pasažieri opakovane čakajú na jazdu vláčikom
3) Vláčik môže poňať iba `C` pasažierov (`C < N`) a urobiť jazdu, iba ak je naplnený

Úlohy ohľadom dokumentácie:
1) Popíšte riešený problém
2) Vysvetlite vašu implementáciu
3) Zamyslite sa nad tým aký problém môže v tomto riešení nastať (Pomôcka: nastal aj pri filozofoch) a spomente ho v dokumentácii
4) Do dokumentácie umiestnite aj výpisy z konzoly

## Opis problému a cieľe zadania
Cieľom zadania je implementovať problém pasažierov a vláčiku. Problém spočíva v tom, že máme pasažierov (počet pasažierov je väčší ako počet miest vo vláčiku), ktorí v nekonečnej slučke čakajú a následne nastupujú na vlak, potom sa na ňom povozia a následne z neho vystúpia a opäť naň idú čakať.

## Opis fungovania implementácie
Táto časť sa zaoberá vysvetlením fungovania implementácie na konkrétnych príkladoch zo zdrojového kódu programu. Implementácia riešenia problému bola inšpirovaná poskytnutým pseudokódom na seminári PPDS.
### Inicializácia vlákien, hodnoty globálnych premenných
```python
no_passengers = 7
train_capacity = 4


class Shared:
    """This class represents shared data."""

    def __init__(self):
        """Initialize shared data."""

        self.boarding_queue = Semaphore(0)
        self.boarding_barrier = Barrier(train_capacity)
        self.boarded = Semaphore(0)

        self.unboarding_queue = Semaphore(0)
        self.unboarding_barrier = Barrier(train_capacity)
        self.unboarded = Semaphore(0)
```
Globálna premenná `no_passengers` predstavuje celkový počet pasažierov, ktorí sa chcú prejsť na vláčiku. Premenná `train_capacity` predstavuje kapacitu vláčika (koľko pasažierov sa doň zmestí). Trieda `Shared` predstavuje zdielanú pamäť medzi jadrami.
Premenné v tejto triede si vieme rozdeliť na dve skupiny. Prvá skupina sa využíva pri logike nastupovania do vláčika a druhá skupina zasa pri vystupovaní z vláčika. Obe obsahujú dva semafóry a bariéru, ich využitie si vysvetlíme neskôr v dokumentácii.
