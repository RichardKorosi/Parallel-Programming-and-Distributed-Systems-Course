# Korosi-111313-PPDS2024-Zadanie-02

## Úlohy zadania
1.) Opíšte problém modifikovaných divochov.\
2.) Opíšte, ako vaša implementácia funguje. Pridajte aj vhodnú charakteristiku, na ktorej sa model zakladá (počty vlákien, časovania aktivít, hodnoty ďalších premenných).\
3.) Opíšte implementáciu znovupoužiteľnej bariéry. V prípade, že si vyberiete variantu so stromom môžete získať bonusové body.\
4.) Zobrazte fragmenty vášho kódu a k nim uveďte synchronizačný vzor (pre každý vzor použitý pri riešení jeden príklad).\
5.) Umiestnite vhodné výpisy na overenie funkčnosti modelu a zahrňte ich do dokumentácie.\

## Opis problému a cieľe zadania
Cieľom zadania je implementovať (modifikovaný) problém "hodujúcich divochov". Problém spočíva v tom, že sa divosi vždy chcú najesť spolu a musia teda na seba vždy počkať. Následne keď príde na večeru aj posledný divoch, tak všetkým naokolo zasignalizuje, že tam sú už všetci a že sa môžu ísť najesť. Divosi následne pojednom pristupujú k hrncu a naberajú si jednu porciu gulášu. V prípade keď príde divoch k hrncu a zbadá, že je prázdny, tak ohlási kuchára a začne čakať pri hrnci až pokým ho kuchár nenaplní. Keď kuchár naplní hrniec tak dá signál divochovi, že si môže nabrať jedlo a ide "spať". Divosi, ktorí majú jedlo naložené môžu konkurentne jesť.

## Opis implementácie

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
