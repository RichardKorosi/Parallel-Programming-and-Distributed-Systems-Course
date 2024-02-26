# Korosi-111313-PPDS2024-Zadanie-02

## Úlohy zadania
1.) Opíšte problém modifikovaných divochov.\
2.) Opíšte, ako vaša implementácia funguje. Pridajte aj vhodnú charakteristiku, na ktorej sa model zakladá (počty vlákien, časovania aktivít, hodnoty ďalších premenných).\
3.) Opíšte implementáciu znovupoužiteľnej bariéry. V prípade, že si vyberiete variantu so stromom môžete získať bonusové body.\
4.) Zobrazte fragmenty vášho kódu a k nim uveďte synchronizačný vzor (pre každý vzor použitý pri riešení jeden príklad).\
5.) Umiestnite vhodné výpisy na overenie funkčnosti modelu a zahrňte ich do dokumentácie.\

## Opis problému a cieľe zadania
Cieľom zadania je implementovať (modifikovaný) problém "hodujúcich divochov". Problém spočíva v tom, že sa divosi vždy chcú najesť spolu a musia teda na seba vždy počkať. Následne keď príde na večeru aj posledný divoch, tak všetkým naokolo zasignalizuje, že tam sú už všetci a že sa môžu ísť najesť. Divosi následne pojednom pristupujú k hrncu a naberajú si jednu porciu gulášu. V prípade keď príde divoch k hrncu a zbadá, že je prázdny, tak ohlási kuchára a začne čakať pri hrnci až pokým ho kuchár nenaplní. Keď kuchár naplní hrniec tak dá signál divochovi, že si môže nabrať jedlo a ide "spať". Divosi, ktorí majú jedlo naložené môžu konkurentne jesť.

## Opis fungovania implementácie
Táto časť sa zaoberá vysvetlením fungovania implementácie na konkrétnych príkladoch zo zdrojového kódu programu.
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
Globálna premenná `savages` predstavuje počet divochov. Globálna premenná `pot_capacity` predstavuje veľkosť hrnca (koľko porcií sa doň zmestí). Trieda Shared predstavuje zdielanú pamäť medzi jadrami. Obsahuje `mutex`, ktorý jadrá využívaju aby zachovali integritu počítadiel. Ďalej obsahuje dve spomenuté počítadlá a to `goulash_portions` a `waiting_savages`. Prvé spomenuté počítadlo reprezentuje aktuálny počet porcií v hrnci a druhé počítadlo reprezentuje počet čakajúcich divochov v bariére. Ďalej tam je zadefinovaná dvojica semaforov `full_pot` a `empty_pot`, táto dvojica semafórov slúži na "komunikáciu" medzi divochmi a kuchárom (princíp fungovania bude vysvetlený neskôr v dokumentácii). Následne `waiting_room` a `dinner_table` sú semafory, ktoré sa využívajú pri bariérach v programe.

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
        sleep(0.5)
        savage_getting_goulash(shared, savage_name)
        sleep(0.5)
        savage_eating(savage_name)
        sleep(0.5)
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

## Opis znovupoužiteľnej baríery
V našom riešení sme implementovali 2 znovupoužiteľné bariéry, na konktrétnom príklade si vysvetlíme jej fungovanie.
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
Keď sa vlákno dostane do bariéry, tak sa pre zachovanie integrity zdielaného počítadla zamkne pomocou mutexu. Následne inkrementuje hodnotu počítadla a vypíše informáciu, že vlákno prišlo na miesto čakania. Po výpise vlákno skontroluje, či už prišlo ako úplne posledné (hodnota počítadla sa rovná počtu vlákien divochov v programe). Ak neprišlo ako posledné odomkne mutex a začne čakať na ostatné vlákna. Ak je posledné, tak vynuluje počídatlo (to má za príčinu znovupoužitelnosť bariéry) a dá signál všetkým vláknam, že môžu pokračovať vo vykonávaní kódu.
