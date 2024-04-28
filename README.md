# Korosi-111313-PPDS2024-Zadanie-11
## Úlohy zadania:
1) Implementujte plánovač pre koprogramy založené na rozšírených generátoroch (round-robin plánovanie).
2) Plánovač by mal reagovať na ukončenie koprogramu (zachytiť výnimku StopIteration) informačným výpisom.
3) Pripravte ukážku v main funkcii pre aspoň 3 koprogramy.
4) Dokumentácia: stručne slovne vysvetlite implementáciu.
## Implementácia:
### Plánovač:
Implementácia zadania spočívala vo vytvorení classy `Scheduler`, ktorá v nekonečnom loope dookola (round-robin štýlom) posiela dáta koprogramom. List koprogramov, ktoré sa majú spúšťať sa napĺňa pomocou metódy `add_job()`, ktorá sa volá v `main()` funkcii, po naplnení listu sa následne volá metóda `start()`, ktorá spúšťa plánovač.

Metóda `start()` v nekonečnom loope generuje dáta (stringy), s ktorými následne koprogramy pracujú. Prechádza cez každý ešte neukončený koprogram a pomocou `.send(data)`
danému koprogramu dáta. Taktiež ošetruje aj `StopIteration` výnimku, ktorá nastane pri ukončení koprogramu, v takom prípade vymaže daný koprogram z listu, cez ktorý iteruje.
Ak je list už prázdny (každý koprogram už skončil), tak sa celý loop `breakne`.
### Koprogramy:
Prvý koprogram `two_strings_fight()` v sebe obsahuje 2 `yieldy`. Porovnávanie nastáva vždy po tom ako koprogram dostane novú dvojicu stringov ( a vypočíta si súčty ASCII hodnôt v stringoch). Po obdržaní druhého stringu koprogram porovná hodnoty
a následne ak druhý string má väčšiu hodnotu, tak sa koprogram ukončí.
```py
@consumer
def two_strings_fight():
    while True:
        text1 = yield
        sum1 = sum(ord(c) for c in text1)
        print(f'{Fore.LIGHTCYAN_EX}Job1: First contestant is: {text1}')

        text2 = yield
        sum2 = sum(ord(c) for c in text2)
        print(f'{Fore.LIGHTCYAN_EX}Job1: Second contestant is: {text2}')

        if sum1 > sum2:
            print(f'{Fore.LIGHTCYAN_EX}Job1: Contestant one won! '
                  f'{text1} [{sum1}] vs {text2} [{sum2}]')
        elif sum1 == sum2:
            print(f'{Fore.LIGHTCYAN_EX}Job1: It is a draw! '
                  f'{text1} [{sum1}] vs {text2} [{sum2}]')
        else:
            print(f'{Fore.LIGHTCYAN_EX}Job1: Contestant two won! '
                  f'{text1} [{sum1}] vs {text2} [{sum2}]')
            break
```
Druhý koprogram `get_type()` zisťuje o akú "vetu" sa jedná (otázka, rozkaz, oznam). Má inú ukončovaciu podmienku a len jeden `yield`. Tento koprogram sa narozdiel od predchádzajúceho ukončí vždy po 10 vykonaných iteráciách.
```py
@consumer
def get_type():
    x = 0
    while x < 10:
        text = yield
        if "!" in text:
            print(f'{Fore.LIGHTGREEN_EX}Job2: This is an order! '
                  f'{text} ({x + 1}/10)')
        elif "?" in text:
            print(f'{Fore.LIGHTGREEN_EX}Job2: This is a question! '
                  f'{text} ({x + 1}/10)')
        elif "." in text:
            print(f'{Fore.LIGHTGREEN_EX}Job2: This is a statement! '
                  f'{text} ({x + 1}/10)')
        x += 1
```
Posledný implementovaný koprogram `digits_vs_chars()` porovnáva pomer vygenerovaných číslic a písmen v obdržanom stringu. Ak sa v stringu nachádza viac číslic ako písmen, koprogram sa ukončí.
```py
@consumer
def digits_vs_chars():
    while True:
        text = yield
        digits = sum(c.isdigit() for c in text)
        chars = sum(c.isalpha() for c in text)
        if digits > chars:
            print(f'{Fore.LIGHTMAGENTA_EX}Job3: Digits won! {text}')
            break
        elif digits == chars:
            print(f'{Fore.LIGHTMAGENTA_EX}Job3: It is a draw! {text}')
        else:
            print(f'{Fore.LIGHTMAGENTA_EX}Job3: Characters won! {text}')
```
