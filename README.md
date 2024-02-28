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
Premenné v tejto triede si vieme rozdeliť na dve skupiny. Prvá skupina sa využíva pri logike nastupovania do vláčika a druhá skupina zasa pri vystupovaní z vláčika. Obe obsahujú dva semafory a bariéru, ich využitie si vysvetlíme neskôr v dokumentácii.
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
### Hlavné slučky vláčiku a pasažierov
```python
def passengers_loop(shared, tid):
    """Simulate passenger's behavior in the infinite loop.

    More specifically, this function simulates the following behavior:
    - passengers start waiting for the train to start loading
    (signal from semaphore in train_loop)
    - passengers board the train (and wait for train to be full),
    last passenger signals the train to start moving (signal in barrier)
    - passengers wait for the train to stop and start unboarding
    (signal from semaphore in train_loop)
    - passengers unboard the train (and wait for each other),
    last passenger signals the train to start loading (signal in barrier)

    Keyword arguments:
    shared -- shared data
    tid -- thread identifier
    """
    while True:
        shared.boarding_queue.wait()
        board(tid)
        shared.boarding_barrier.wait(shared.boarded)
        shared.unboarding_queue.wait()
        unboard(tid)
        shared.unboarding_barrier.wait(shared.unboarded)
```
Pasažieri začínajú čakaním kým vláčik nezačne príjmať pasažierov. Keď obdržia signál začnú nastupovať do vláčika (vojsť však môže len taký počet pasažierov aká je kapacita vláčika), nastupovanie do vláčika predstavuje jednoduchá funkcia, ktorá akurát vypíše, že konkrétny pasažier doň vstúpil. Podobnou logikou, kde hlavnou úlohou funkcie je akurát výpis sú implementované aj ďaľšie funkcie ako `run()`, `unboard()`, `load()` a `unload()`.
```python
def board(passenger):
    """Print message about passenger boarding.

    Keyword arguments:
    passenger -- name of the passenger (thread identifier)
    """
    print(Fore.LIGHTBLUE_EX + f"{passenger} is boarding." + Style.RESET_ALL)
```
Následne po nastúpení pasažieri čakajú v `shared.boarding_barrier.wait()`, kým sa vláčik nenaplní, posledný cestujúci následne otvorí bariéru a umožní teda pasažierom prejsť k `shared.unboarding_queue.wait()`. Okrem signálu pre cestujúcich taktiež posledný pasažier pošle aj signál vláčiku a ten tým pádom už nebude čakať v `shared.boarded.wait()` a môže teda začať jazdu. Následne program simuluje cestu vláčikom funkciou `run()`, po jej skončení vláčik informuje, sa otvára a že pasažieri majú vystúpiť a následne vláčik začne čakať kým sa vyprázdni. Do tohto momentu čakali pasažieri v `shared.unboarding_queue.wait()`, teraz však dostali signál od vláčiku a začínajú vychádzať von. Pod pojmom vychádzať von rozumieme barériu `unboarding_barrier()`, kde podobne ako pri `boarding_barrier()` posledný pasažier otvorí bariéru ostatným pasažierom (a sebe) a idú na začiatok slučky a teda znova čakajú na vláčik. Okrem iného posledný pasažier znova informuje aj vláčik, teraz ho však informuje, že už je prázdny a po tomto signále vláčik môže prejsť cez `shared.unboarded.wait()` a začína svoju slučku, podobne ako aj pasažieri, znova od začiatku.


```python
def train_loop(shared, tid):
    """Simulate train's behavior in the infinite loop.

    More specifically, this function simulates the following behavior:
    - train starts loading passengers (signals passengers to board)
    - train waits for all passengers to board (to full capacity)
    - train starts running
    - train stops and starts unboarding passengers
    (signals passengers to unboard)
    - train waits for all passengers to unboard (to empty capacity)
    - after all passengers unboarded, train starts loading passengers again


    Keyword arguments:
    shared -- shared data
    tid -- thread identifier
    """
    while True:
        load(tid)
        shared.boarding_queue.signal(train_capacity)
        shared.boarded.wait()
        run(tid)
        unload(tid)
        shared.unboarding_queue.signal(train_capacity)
        shared.unboarded.wait()
```
### Problém, ktorý môže nastať
Problém, ktorým táto implementácia trpí je možnosť vyhladovenia. Vyhladovenie môžeme opísať ako problém pri ktorom sa nejaký proces nikdy „nedostane k slovu”. U nás tento problém môže nastať medzi pasažiermi keďže podľa zadania je pasažierov viac ako je maximálna kapatica vláčiku. Môže teda nastať prípad kedy sa pasažier nikdy nedostane do vláčika (naša implementácia nevyužíva FIFO/Silný semafor).

### Výpis
```
Train is loading passengers.
Passenger(3) is boarding.
Passenger(10) is boarding.
Passenger(9) is boarding.
Passenger(6) is boarding.
Passenger(7) is boarding.
Passenger(2) is boarding.
Train is running.
Train is unloading passengers.
Passenger(7) is unboarding.
Passenger(2) is unboarding.
Passenger(9) is unboarding.
Passenger(10) is unboarding.
Passenger(3) is unboarding.
Passenger(6) is unboarding.
Train is loading passengers.
Passenger(9) is boarding.
Passenger(11) is boarding.
Passenger(0) is boarding.
Passenger(7) is boarding.
Passenger(6) is boarding.
Passenger(8) is boarding.
Train is running.
Train is unloading passengers.
Passenger(11) is unboarding.
Passenger(9) is unboarding.
Passenger(6) is unboarding.
Passenger(7) is unboarding.
Passenger(0) is unboarding.
Passenger(8) is unboarding.
Train is loading passengers.
Passenger(8) is boarding.
Passenger(5) is boarding.
Passenger(9) is boarding.
Passenger(0) is boarding.
Passenger(4) is boarding.
Passenger(12) is boarding.
Train is running.
Train is unloading passengers.

Process finished with exit code -1
```
![image](https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/edd44510-5e54-45a1-bbcc-6de8985b28ac)

## Zdroje
Inšpirácie, využité časti kódu a podobne:
* [README template](https://github.com/matiassingers/awesome-readme)
* [Časti kódu (spomenuté vyššie v dokumentácii v sekcii "Implementácia")](https://github.com/tj314/ppds-seminars/tree/ppds2024)
* [PEP 8 & PEP 257 validator](https://www.codewof.co.nz/style/python3/)
* [Conventional Commits guide](https://www.conventionalcommits.org/en/v1.0.0/)
* [Teoretické časti boli vysvetlené na základe vedomostí získaných na prednáške a seminári na predmete PPDS](https://uim.fei.stuba.sk/predmet/i-ppds/)

