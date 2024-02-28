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
### Inicializácia vlákien, hodnoty globálnych premenných, využité triedy
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
```python
class Barrier:
    """This class represents barrier."""

    def __init__(self, n):
        """Initialize barrier data."""
        self.n = n
        self.counter = 0
        self.mutex = Mutex()
        self.barrier = Semaphore(0)

    def wait(self, signal_to_train):
        """Wait for all threads to reach the barrier and then signal them to continue.

        More specifically, this function simulates the basic
        behavior of the barrier, with one exception.
        It not only signals all threads in the barrier to continue,
        but also signals the train to finish loading/unloading passengers.

        Keyword arguments:
        signal_to_train -- semaphore to signal train to stop
        loading/unloading passengers
        """
        self.mutex.lock()
        self.counter += 1
        if self.counter == self.n:
            self.counter = 0
            self.barrier.signal(self.n)
            signal_to_train.signal()
        self.mutex.unlock()
        self.barrier.wait()
```
Trieda `Barrier` predstavuje implementáciu klasickej bariéry, až na jednu výnimku. Pri dosiahnutí určitej hodnoty počítadla nepošle posledné vlákno, ktoré prišlo do bariéry len signál pre ostatné vlákna, ale aj signál pre vlákno vlaku. Príkaz `self.barrier.signal(self.n)` má teda za úlohu poslať signál a teda otvoriť bariéru pre `n` vlákien, kde `n` reprezentuje kapacitu vláčika. Následne `signal_to_train.signal()` slúži už na informovanie vláčika, že je plný a že môže začať jazdu.
```python
def main():
    """Create certain number of passengers threads and train thread and start them.

    More specifically, this example demonstrates the case in which
    passengers are boarding and unboarding the train in the infinite loop.
    """
    shared = Shared()
    all_threads = []
    for i in range(no_passengers):
        all_threads.append(Thread(passengers_loop, shared, f"Passenger({i})"))
    all_threads.append(Thread(train_loop, shared, "Train"))
    for i in all_threads:
        i.join()
```
Vo funkcii `main()` sa inicializujú vlákna pasažierov a aj vláčika. Počet vlákien pasažierov závisí od nastavenej globálnej premennej `no_passengers`, vlákno reprezentujúce vláčik je vždy len jedno.
