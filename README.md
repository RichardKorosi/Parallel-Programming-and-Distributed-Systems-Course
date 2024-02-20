# Korosi-111313-PPDS2024-Zadanie-01


## Popis a cieľe zadania
Cieľom zadania je implementovať problém "Kto raňajkoval skôr". Zadanie spočíva vo vytvorení dvoch vlákien, ktoré môžu súbežne vykonávať svoje "ranné rutiny" (funkcie) až do momentu, kým vlákna nedokončia určitú činnosť (v našom prípade rannú hygienu).\
V momente keď vlákno dokončí rannú hygienu tak:\
Vlákno "Jano" (bez ohľadu čo zatiaľ robí vlákno "Fero") začne raňajkovať. Po dojedení raňajok informuje vlákno "Fero", že už raňajkoval.\
Vlákno "Fero" (bez ohľadu čo zatiaľ robí vlákno "Jano") začne čakať na telefonát od vlákna "Jano" (inak povedané nevykonáva žiadnu aktivitu). Toto tvrdenie platí za predpokladu, že ho vlákno "Jano" ešte nekontaktovalo (môže nastať prípad kedy vlákno "Jano" začne volať vláknu "Fero" ešte predtým ako vlákno "Fero" dokončí rannú hygienu, v tomto prípade môže vlákno "Fero" okamžite zdvihnúť telefón a následne ísť raňajkovať).


## Úlohy zadania
1.) Implementujte problém „Kto raňajkoval skôr“ z prednášky.\
2.) Simulujte procesy spánok, ranná hygiena, telefonát, raňajky.\
3.) Zabezpečte, aby subjekt A (nazvime ho Jano) raňajkoval skôr ako
subjekt B (nazvime ho Fero). Inšpirujte sa schémou z prednášky.\
4.) Spíšte dokumentáciu. V nej uveďte všetky podstatné detaily
o implementácii. Súčasťou dokumentácie musia byť aj výpisy
z konzoly.

## Implementácia

### 1) Vytvorenie Shared classy (inšpirované a prevzaté zo semináru PPDS, viď. zdroje)
Za povšimnutie v tejto časti kódu stojí hodnota 0 pri inicializácii semafóru. Táto inicializácia nám zapríčiní, že ak vlákno "Fero", ktoré má mať raňajky až ako druhé, vykoná svoje aktivity rýchlejšie a dostane sa k časti `semaphore.wait()` skôr ako mu ako sa naraňajkuje vlákno "Jano", bude musieť čakať na signál (telefonát). 
```python
class Shared:
    """This class represents shared data."""

    def __init__(self):
        """Initialize shared data."""
        self.semaphore = Semaphore(0)
```
### 2) Vytvorenie dvoch vlákien (inšpirované zo semináru PPDS, viď. zdroje)
```python
def main():
    """Create two threads and start them.

    More specifically, this example demonstrates the case in which
    one thread has to wait for another thread to finish its
    tasks before it can continue with its own tasks.
    """
    shared = Shared()
    thread1 = Thread(routine_jano, shared, "Jano")
    thread2 = Thread(routine_fero, shared, "Fero")
    thread1.join()
    thread2.join()
```
### 3) Vytvorenie funkcií simulujúce ranné aktivity 
Funkcia funguje na princípe: [výpis o začiatku aktivity -> simulácia vykonávania aktivity (sleep) -> výpis o ukončení aktivity]. \
Rovnakým štýlom sú implementované aj funkcie `sleeping()`, `eating()`.
```python
def hygiene(tid):
    """Execute hygiene activity of the thread.

    This function prints a message that the thread is taking a shower
    and then waits for a while before printing a message that the thread
    is clean.

    Keyword arguments:
    tid -- thread identifier
    """
    highlighted_print(f"{tid} is taking a shower.", "hygiene")
    sleep(1)
    highlighted_print(f"{tid} has finished showering.", "hygiene")
```

### 4) Vytvorenie funkcií obsahujúce semafór
Funkcie `calling()` a `receiving()` majú v sebe implementovanú hlavnú logiku riešenia problému. Vo funkcii `calling()` si môžeme všimnúť `shared.semaphore.signal()`, to má za príčinu, že vlákno pošle signál a tým pádom odomkne možnosť druhému vláknu čakajúcemu v `receiving()` pokračovať ďalej vo vykonávaní aktivít.
```python
def calling(shared, tid):
    """Execute calling activity of the thread.

    This function prints a message that the thread has called
    and then signals the semaphore. This allows the other thread
    (that is waiting in the receiving() function) to continue with its tasks.

    Keyword arguments:
    shared -- shared data between threads
    tid -- thread identifier
    """
    highlighted_print(f"{tid} is calling.", "calling")
    sleep(1)
    shared.semaphore.signal()
```
Avšak môže nastať aj prípad kedy vlákno vo funkcii `receiving()` nebude musieť vôbec čakať, tento prípad by nastal ak vlákno "Jano" bolo schopné zavolať vláknu "Fero" ešte pred momentom kedy by sa vlákno "Fero" dostalo k riadku `shared.semaphore.wait()` vo funkcii `receiving()`.

```python
def receiving(shared, tid):
    """Execute receiving activity of the thread.

    This function makes the thread wait (assuming that semaphore
    was initialized with value 0 and has not received any signals yet)
    for the semaphore to be signaled (signal is in calling() function)
    and after receiving the signal it prints a message
    indicating that the thread has received a call.

    Keyword arguments:
    shared -- shared data between threads
    tid -- thread identifier
    """
    shared.semaphore.wait()
    highlighted_print(f"{tid} has received a call.", "receiving")
    sleep(1)
```
Výhodou tejto implementácie je fakt, že máme zaručené, že "Jano" bude raňajkovať vždy skôr ako "Fero", pretože aj ak by "Fero" dokončil rannú hygienu skôr ako "Jano", tak ostane čakať vo funkcii `receiving()`, pokiaľ mu "Jano" nezavolá.

### 5) Vytvorenie rutín pre vlákna
Obe vlákna vykonávajú v kóde vlastné ranné rutiny a preto sú rozdelené do dvoch funkcií (jedna pre vlákno "Jano" a druhá pre vlákno "Fero").
```python
def routine_jano(shared, tid):
    """Execute the routine of thread Jano.

    Keyword arguments:
    shared -- shared data between threads
    tid -- thread identifier
    """
    sleeping(tid)
    hygiene(tid)
    eating(tid)
    calling(shared, tid)
```
Vlákno "Jano" má rannú rutinu: Spanie -> Hygiena -> Raňajky -> Zavolanie vláknu "Fero".
```python
def routine_fero(shared, tid):
    """Execute the routine of thread Fero.

    Keyword arguments:
    shared -- shared data between threads
    tid -- thread identifier
    """
    sleeping(tid)
    hygiene(tid)
    receiving(shared, tid)
    eating(tid)
```
Vlákno "Fero" má rannú rutinu: Spanie -> Hygiena -> Čakanie na telefonát -> Raňajky.
### 6) Vytvorenie funkcie na zvýraznenie správ
Pre lepšiu čitatelnosť a prehladnosť je implementovaná aj funkcia, ktorá farebne rozlišuje výpisy aktivít vlákien.
```python
def highlighted_print(message, activity):
    """Print a highlighted message of a given activity.

    The color of the message is based on the type of activity.
    Cyan color represents sleeping activity.
    Blue color represents hygiene activity.
    Magenta color represents eating activity.
    Red color represents calling and receiving activities.

    Keyword arguments:
    message -- message to be printed
    activity -- name of the activity
    """
    if activity == "sleeping":
        print(Fore.CYAN + message)
    elif activity == "hygiene":
        print(Fore.BLUE + message)
    elif activity == "eating":
        print(Fore.MAGENTA + message)
    else:
        print(Fore.RED + message)
```




## Výpisy z konzoly
| Screenshot výpisu | Popis |
| --------- | -- |
| ![image](https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/0ae6aacc-ec5b-4aa6-9e8a-2dcf63f1f8ca) | V tomto prípade vlákno "Fero" vykonalo skôr rannú hygienu, ale počkalo kým sa vlákno "Jano" dosprchuje, naje a zavolá mu. |
| ![image](https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/cc6636f2-ec7a-4180-ac59-01b3c9b9bd50) | V tomto prípade vlákno "Fero" muselo už čakať len na dokončenie raňajkovej aktivity vlákna "Jano" a na následne zavolanie.|

```
Jano is sleeping.
Fero is sleeping.
Fero has woken up.
Fero is taking a shower.
Jano has woken up.
Jano is taking a shower.
Jano has finished showering.
Fero has finished showering.
Jano is eating.
Jano has eaten.
Jano is calling.
Fero has received a call.
Fero is eating.
Fero has eaten.

Process finished with exit code 0
```
## Zdroje
Inšpirácie, využité časti kódu a podobne:
* [README template](https://github.com/matiassingers/awesome-readme)
* [Časti kódu (spomenuté vyššie v dokumentácii v sekcii "Implementácia")](https://github.com/tj314/ppds-seminars/tree/ppds2024)
* [PEP 8 & PEP 257 validator](https://www.codewof.co.nz/style/python3/)
* [Conventional Commits guide](https://www.conventionalcommits.org/en/v1.0.0/)
* Teoretické časti boli vysvetlené na základe vedomostí získaných na prednáške a seminári
