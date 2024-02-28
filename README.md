# Korosi-111313-PPDS2024-Zadanie-02

## Úlohy zadania
1) Opíšte problém modifikovaných divochov.
2) Opíšte, ako vaša implementácia funguje. Pridajte aj vhodnú charakteristiku, na ktorej sa model zakladá (počty vlákien, časovania aktivít, hodnoty ďalších premenných).
3) Opíšte implementáciu znovupoužiteľnej bariéry. V prípade, že si vyberiete variantu so stromom môžete získať bonusové body.
4) Zobrazte fragmenty vášho kódu a k nim uveďte synchronizačný vzor (pre každý vzor použitý pri riešení jeden príklad).
5) Umiestnite vhodné výpisy na overenie funkčnosti modelu a zahrňte ich do dokumentácie.

## Opis problému a cieľe zadania
Cieľom zadania je implementovať (modifikovaný) problém "hodujúcich divochov". Problém spočíva v tom, že sa divosi vždy chcú najesť spolu a musia teda na seba vždy počkať. Následne keď príde na večeru aj posledný divoch, tak všetkým naokolo zasignalizuje, že tam sú už všetci a že sa môžu ísť najesť. Divosi následne pojednom pristupujú k hrncu a naberajú si jednu porciu gulášu. V prípade keď príde divoch k hrncu a zbadá, že je prázdny, tak ohlási kuchára a začne čakať pri hrnci až pokým ho kuchár nenaplní. Keď kuchár naplní hrniec tak dá signál divochovi, že si môže nabrať jedlo a ide "spať". Divosi, ktorí majú jedlo naložené môžu konkurentne jesť.

## Opis fungovania implementácie
Táto časť sa zaoberá vysvetlením fungovania implementácie na konkrétnych príkladoch zo zdrojového kódu programu. Implementácia riešenia problému bola inšpirovaná poskytnutým pseudokódom na seminári PPDS.
### Inicializácia vlákien, hodnoty globálnych premenných
```python
savages = 7
pot_capacity = 5


class Shared:
    """This class represents shared data."""

    def __init__(self):
        """Initialize shared data."""
        self.mutex = Mutex()
        self.goulash_portions = pot_capacity
        self.waiting_savages = 0
        self.full_pot = Semaphore(0)
        self.empty_pot = Semaphore(0)

        self.waiting_room = Semaphore(0)
        self.dinner_table = Semaphore(0)
```
Globálna premenná `savages` predstavuje počet divochov. Globálna premenná `pot_capacity` predstavuje veľkosť hrnca (koľko porcií sa doň zmestí). Trieda Shared predstavuje zdielanú pamäť medzi jadrami. Obsahuje `mutex`, ktorý jadrá využívaju aby zachovali integritu počítadiel. Ďalej obsahuje dve spomenuté počítadlá a to `goulash_portions` a `waiting_savages`. Prvé spomenuté počítadlo reprezentuje aktuálny počet porcií v hrnci a druhé počítadlo reprezentuje počet čakajúcich divochov v bariére. Ďalej tam je zadefinovaná dvojica semaforov `full_pot` a `empty_pot`, táto dvojica semafórov slúži na "komunikáciu" medzi divochmi a kuchárom (princíp fungovania bude vysvetlený neskôr v dokumentácii). Následne `waiting_room` a `dinner_table` sú semafory, ktoré sa využívajú pri bariérach v programe. Daný úsek kódu bol inšpirovaný poskytnutým kódom zo semináru PPDS.

```python
def main():
    """Create certain number of savages threads and cook thread and start them.

    More specifically, this example demonstrates the case in which
    one group of threads (savages) are always eating together and
    wait for each-other every day, when pot is empty savages wait
    for the cook to cook until the pot is full.
    """
    shared = Shared()
    all_threads = []
    for i in range(savages):
        all_threads.append(Thread(daily_eating, shared, f"Savage({i})"))
    all_threads.append(Thread(cook_goulash, shared, "Cook"))
    for i in all_threads:
        i.join()
```
Vo funkcii `main()` sa inicializujú vlákna divochov a aj kuchára. Počet vlákien divochov závisí od nastavenej globálnej premennej `savages`, vlákno reprezentujúce kuchára je vždy len jedno.

### Princíp fungovania implementácie (hlavný loop)
```python
def daily_eating(shared, savage_name):
    """Execute the daily eating routine of the savages threads.

    More specifically, this function represents two barriers that
    synchronize the savages, activity of savages taking goulash
    from the pot (there can only be one savage at the pot at a same time)
    and eating (eating is concurrent).

    Keyword arguments:
    shared -- shared data between threads
    savage_name -- name of the thread (thread identifier)
    """
    while True:
        waiting_room_barrier(shared, savage_name)
        sleep(0.5)
        dinner_table_barrier(shared, savage_name)
        savage_getting_goulash(shared, savage_name)
        savage_eating(savage_name)
```
Divosi vykonávajú nekonečný loop 4 hlavných funkcií `waiting_room_barrier()`, `dinner_table_barrier()`, `savage_getting_goulash()` a `savage_eating()`. Samotné funkcie budú vysvetlené neskôr v dokumentácii. Všeobecný princíp fungovania je následovný:
1) Divosi sa spoločne stretnú v bariére `waiting_room_barrier()`
2) Následne prechádzajú do druhej bariéry `dinner_table_barrier()`, pointa tejto bariéry je aby zabránila prípadu kedy divoch po otvorení bariéry `waiting_room_barrier()` stihne zjesť guláš a dostať sa znova to `waiting_room_barrier()` predtým ako ostatní divosi stihli čo i len začať jesť, tento prípad je neželané správanie, keďže v tomto prípade existuje pravdepodobnosť, že jeden divoch môže jesť viackrát a iný divoch/divosi sa nemusia najesť vôbec. Výhodou využitia tejto druhej bariéry je, že aj ak by sa divoch stihol najesť predtým ako sa iný divoch ešte nedostal k hrncu, tak ostane zablokovaný v bariére `waiting_room_barrier()`, ktorá sa zavrela keď posledný divoch cez ňu v daný deň prešiel.
3) Vo funkcii `savage_getting_goulash()` pristupujú divosi po jednom k hrncu s gulášom a berú si porciu, v prípade kedy je hrniec prázdny, tak divoch ohlási kuchára (bližšie informácie neskôr v dokumentácii v sekcii zameranej na implementované funkcie).
4) Divosi následne zjedia guláš.

```python
def cook_goulash(shared, cook_name):
    """Simulate the cook activity.

    More specifically, this function represents the activity of the cook.
    Cook waits for the signal from the savages that the pot is empty
    and then cooks the goulash until the pot is full. After that, cook signals
    the savage that came to the pot to take the goulash portion and
    then waits for the another signal from the savages that the pot is empty.

    Keyword arguments:
    shared -- shared data between threads
    cook_name -- name of the thread (thread identifier)
    """
    while True:
        shared.empty_pot.wait()
        while shared.goulash_portions < pot_capacity:
            shared.goulash_portions += 1
            print(f"{Fore.LIGHTCYAN_EX}{cook_name} is cooking."
                  f"({shared.goulash_portions}/{pot_capacity}).")
        print(f"{Fore.RED}{cook_name} has cooked full pot of goulash.")
        shared.full_pot.signal()
```

## Opis znovupoužiteľnej bariéry
V našom riešení sme implementovali aj znovupoužiteľnú bariéru, jej fungovanie si vysvetlíme na príklade. Znovu použiteľná bariéra sa skladá z dvoch jednoduchých bariér (SimpleBarrier).
```python
def waiting_room_barrier(shared, savage_name):
    """Synchronize savages before eating using barrier.

    More specifically, this function represents a barrier that synchronize
    the savages before eating. Last savage that arrives to the barrier signals
    the barrier and all savages can continue. The last savage also resets
    the barrier for the next day (iteration in the loop).

    Keyword arguments:
    shared -- shared data between threads
    savage_name -- name of the thread (thread identifier)
    """
    shared.mutex.lock()
    shared.waiting_savages += 1
    print(f"{Fore.LIGHTMAGENTA_EX}{savage_name} is waiting for others. "
          f"({shared.waiting_savages}/{savages})")
    if shared.waiting_savages == savages:
        shared.waiting_savages = 0
        shared.waiting_room.signal(savages)
    shared.mutex.unlock()
    shared.waiting_room.wait()
```
Najprv si vysvetlime logiku jednoduchej bariéry. Keď sa vlákno dostane do bariéry, tak sa pre zachovanie integrity zdielaného počítadla zamkne pomocou mutexu. Následne inkrementuje hodnotu počítadla a vypíše informáciu, že vlákno prišlo na miesto čakania. Po výpise vlákno skontroluje, či už prišlo ako úplne posledné (hodnota počítadla sa rovná počtu vlákien divochov v programe). Ak neprišlo ako posledné odomkne mutex a začne čakať na ostatné vlákna. Ak je posledné, tak vynuluje počídatlo a dá signál všetkým vláknam, že môžu pokračovať vo vykonávaní kódu, odomkne mutex a prejde cez beriéru spolu aj s ostatnými vláknami.
```python
 while True:
        waiting_room_barrier(shared, savage_name)
        dinner_table_barrier(shared, savage_name)
```
Ako bolo spomenuté vyššie, znovu použiteľná bariéra sa skladá z dvoch jednoduchých bariér, jej implementácia je teda pomerne jednoduchá, ale jej význam je veľký. Jej význam už bol spomenutý v sekcii opisujúcej `daily_eating()`, konktrétnejšie pri opise prvého a druhého bodu. V skratke jej výhodou je to, že zabraňuje prípadu, kedy sa jeden divoch dokáže rýchlo najesť a ešte v ten istý deň prísť za zbytkom divochov a dostať večeru aj druhýkrát na úkor iného divocha.


## Synchronizácia v programe

### Synchronizácia divochov na začiatku večere
Prvá synchronizácia vlákien nastáva v bariére `waiting_room_barrier()`, rovnakým spôsobom funguje aj synchronizačná bariéra `dinner_table_barrier()` a preto si synchronizačné vzory vysvetlíme len na tejto jednej.
```python
shared.mutex.lock()
shared.waiting_savages += 1
print(f"{Fore.LIGHTMAGENTA_EX}{savage_name} is waiting for others. "
    f"({shared.waiting_savages}/{savages})")
if shared.waiting_savages == savages:
    shared.waiting_savages = 0
    shared.waiting_room.signal(savages)
shared.mutex.unlock()
shared.waiting_room.wait()
```
V danom fragmente kódu sa využíva aj `mutex` aj `semafor`. Mutex sa využíva v `bariére` na ochranu integrity dát (v našom konkrétnom príklade ide o počítadlo divochov čakajúcich na večeru). Vlákno po príchode k bariére si zamkne mutex, zvýši hodnotu počítadla. Ak sa hodnota počítadla rovná celkovému počtu divochov, tak vlákno počítadlo vynuluje a následne vytvorí signál pre semafor (hodnota poskytnutá semaforu sa rovná počtu všetkých divochov), vďaka ktorému sa všetci čakajúci divosi môžu cez bariéru dostať. Po práci s počítadlom vlákno odomyká mutex a v prípade, že neprišlo ako posledné čaká na signál.

### Synchronizácia naberania porcií a varenia
Okrem synchronizácie divochov na začiatku večere, je potrebné synchronizovať divochov a kuchára pri naberaní porcií a varení. Opäť si môžeme všimnúť mutex, ten nám podobne ako v predošlom príklade chráni integritu dát (v tomto konkrétnom prípade chránime integritu počtu porcií v hrnci). Mutex nám teda simuluje situáciu, pri ktorej si divosi chodia naberať guláš po jednom.
```python
shared.mutex.lock()
print(f"{Fore.GREEN}{savage_name}: I can see {shared.goulash_portions} "
    f"portion(s) in the pot.")
if shared.goulash_portions == 0:
    print(f"{Fore.RED}{savage_name} is telling the cook to cook.")
    shared.empty_pot.signal()
    shared.full_pot.wait()
print(f"{Fore.GREEN}{savage_name} has taken 1 portion.")
shared.goulash_portions -= 1
shared.mutex.unlock()
```
V prípade, keď sa v hrnci nenachádza už žiadna porcia, tak divoch signalizuje kuchárovi, že má začať variť a začne čakať. Kuchár na začiatku programu vojde do svojej funkcie a čaká kým nedostane práve spomínaný signál, že  má začať variť, akonáhle dovarí, dá signál divochovi, že je navarané a začne opäť čakať kým ho ďaľší divoch nezavolá. Implementovaná logika predstavuje synchronizačný vzor `Rendezvous`.
```python
shared.empty_pot.wait()
while shared.goulash_portions < pot_capacity:
    shared.goulash_portions += 1
    print(f"{Fore.LIGHTCYAN_EX}{cook_name} is cooking."
        f"({shared.goulash_portions}/{pot_capacity}).")
print(f"{Fore.RED}{cook_name} has cooked full pot of goulash.")
shared.full_pot.signal()
```
## Výpis programu
![image](https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/0a0db026-3445-4f86-b31b-8b08432d3dd8)
```
Savage(0) is waiting for others. (1/7)
Savage(1) is waiting for others. (2/7)
Savage(2) is waiting for others. (3/7)
Savage(3) is waiting for others. (4/7)
Savage(4) is waiting for others. (5/7)
Savage(5) is waiting for others. (6/7)
Savage(6) is waiting for others. (7/7)
Savage(5): We are all here, let's eat!
Savage(5): I can see 5 portion(s) in the pot.
Savage(5) has taken 1 portion.
Savage(5) is eating.
Savage(2): I can see 4 portion(s) in the pot.
Savage(2) has taken 1 portion.
Savage(2) is eating.
Savage(4): I can see 3 portion(s) in the pot.
Savage(4) has taken 1 portion.
Savage(4) is eating.
Savage(6): I can see 2 portion(s) in the pot.
Savage(6) has taken 1 portion.
Savage(6) is eating.
Savage(0): I can see 1 portion(s) in the pot.
Savage(0) has taken 1 portion.
Savage(0) is eating.
Savage(0) is waiting for others. (1/7)
Savage(1): I can see 0 portion(s) in the pot.
Savage(1) is telling the cook to cook.
Cook is cooking.(1/5).
Cook is cooking.(2/5).
Cook is cooking.(3/5).
Cook is cooking.(4/5).
Cook is cooking.(5/5).
Cook has cooked full pot of goulash.
Savage(1) has taken 1 portion.
Savage(1) is eating.
Savage(5) is waiting for others. (2/7)
Savage(2) is waiting for others. (3/7)
Savage(4) is waiting for others. (4/7)
Savage(6) is waiting for others. (5/7)
Savage(3): I can see 4 portion(s) in the pot.
Savage(3) has taken 1 portion.
Savage(3) is eating.
Savage(3) is waiting for others. (6/7)
Savage(1) is waiting for others. (7/7)
Savage(2): We are all here, let's eat!
Savage(2): I can see 3 portion(s) in the pot.
Savage(2) has taken 1 portion.
Savage(2) is eating.
Savage(6): I can see 2 portion(s) in the pot.
Savage(6) has taken 1 portion.
Savage(6) is eating.
Savage(6) is waiting for others. (1/7)
Savage(0): I can see 1 portion(s) in the pot.
Savage(0) has taken 1 portion.
Savage(0) is eating.
Savage(1): I can see 0 portion(s) in the pot.
Savage(1) is telling the cook to cook.
Cook is cooking.(1/5).
Cook is cooking.(2/5).
Cook is cooking.(3/5).
Cook is cooking.(4/5).
Cook is cooking.(5/5).
Cook has cooked full pot of goulash.
Savage(1) has taken 1 portion.
Savage(1) is eating.
Savage(1) is waiting for others. (2/7)
Savage(4): I can see 4 portion(s) in the pot.
Savage(4) has taken 1 portion.
Savage(4) is eating.
Savage(4) is waiting for others. (3/7)
Savage(3): I can see 3 portion(s) in the pot.
Savage(3) has taken 1 portion.
Savage(3) is eating.
Savage(3) is waiting for others. (4/7)
Savage(5): I can see 2 portion(s) in the pot.
Savage(5) has taken 1 portion.
Savage(5) is eating.
Savage(5) is waiting for others. (5/7)
Savage(0) is waiting for others. (6/7)
Savage(2) is waiting for others. (7/7)
Savage(5): We are all here, let's eat!
Savage(5): I can see 1 portion(s) in the pot.
Savage(5) has taken 1 portion.
Savage(5) is eating.
Savage(1): I can see 0 portion(s) in the pot.
Savage(1) is telling the cook to cook.
Cook is cooking.(1/5).
Cook is cooking.(2/5).
Cook is cooking.(3/5).
Cook is cooking.(4/5).
Cook is cooking.(5/5).
Cook has cooked full pot of goulash.
Savage(1) has taken 1 portion.
Savage(1) is eating.
Savage(1) is waiting for others. (1/7)
Savage(0): I can see 4 portion(s) in the pot.
Savage(0) has taken 1 portion.
Savage(0) is eating.
Savage(0) is waiting for others. (2/7)
Savage(5) is waiting for others. (3/7)
Savage(6): I can see 3 portion(s) in the pot.
Savage(6) has taken 1 portion.
Savage(6) is eating.
Savage(6) is waiting for others. (4/7)
Savage(3): I can see 2 portion(s) in the pot.
Savage(3) has taken 1 portion.
Savage(3) is eating.
Savage(3) is waiting for others. (5/7)
Savage(4): I can see 1 portion(s) in the pot.
Savage(4) has taken 1 portion.
Savage(4) is eating.
Savage(4) is waiting for others. (6/7)
Savage(2): I can see 0 portion(s) in the pot.
Savage(2) is telling the cook to cook.
Cook is cooking.(1/5).
Cook is cooking.(2/5).
Cook is cooking.(3/5).
Cook is cooking.(4/5).
Cook is cooking.(5/5).
Cook has cooked full pot of goulash.
Savage(2) has taken 1 portion.
Savage(2) is eating.
Savage(2) is waiting for others. (7/7)

Process finished with exit code -1
```
## Zdroje
Inšpirácie, využité časti kódu a podobne:
* [README template](https://github.com/matiassingers/awesome-readme)
* [Časti kódu (spomenuté vyššie v dokumentácii v sekcii "Implementácia")](https://github.com/tj314/ppds-seminars/tree/ppds2024)
* [PEP 8 & PEP 257 validator](https://www.codewof.co.nz/style/python3/)
* [Conventional Commits guide](https://www.conventionalcommits.org/en/v1.0.0/)
* [Teoretické časti boli vysvetlené na základe vedomostí získaných na prednáške a seminári na predmete PPDS](https://uim.fei.stuba.sk/predmet/i-ppds/)
