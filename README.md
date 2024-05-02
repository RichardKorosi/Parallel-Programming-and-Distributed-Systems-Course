# Korosi-111313-PPDS2024-Zadanie-11
## Úlohy zadania:
1) Implementujte plánovač pre koprogramy založené na rozšírených generátoroch (round-robin plánovanie).
2) Plánovač by mal reagovať na ukončenie koprogramu (zachytiť výnimku `StopIteration`) informačným výpisom.
3) Pripravte ukážku v main funkcii pre aspoň 3 koprogramy.
4) Dokumentácia: stručne slovne vysvetlite implementáciu.
## Implementácia:
### Plánovač:
Implementácia zadania spočívala vo vytvorení classy `Scheduler`, ktorá v "nekonečnom" loope dookola (round-robin štýlom) posiela dáta koprogramom. List koprogramov, ktoré sa majú spúšťať sa napĺňa pomocou metódy `add_job()`, ktorá sa volá v `main()` funkcii, po naplnení listu sa následne volá metóda `start()`, ktorá spúšťa plánovač.
```py
def main():
    scheduler = Scheduler()
    job1 = two_strings_fight()
    job2 = get_type()
    job3 = digits_vs_chars()
    scheduler.add_job(job1)
    scheduler.add_job(job2)
    scheduler.add_job(job3)
    scheduler.start()
```

Metóda `start()` v "nekonečnom" loope generuje dáta (stringy), s ktorými následne koprogramy pracujú. Prechádza cez každý ešte neukončený koprogram a pomocou `.send(data)` posiela danému koprogramu dáta. Taktiež ošetruje aj `StopIteration` výnimku, ktorá nastane pri ukončení koprogramu, v takom prípade vymaže daný koprogram z listu, cez ktorý iteruje.
Ak je list už prázdny (každý koprogram už skončil), tak sa celý loop `breakne`.
```py
def start(self):
    while True:
        rand = random.choices(string.ascii_lowercase + string.digits, k=10)
        data = ''.join(rand)
        data += random.choice(['!', '?', '.'])
        sleep(0.2)

        print(f'{Fore.WHITE}' + '-' * 50)
        for job in self.jobs[:]:
            try:
                current_job = job
                job.send(data)
            except StopIteration:
                self.jobs.remove(current_job)
                print(f'{Fore.RED}----Coprogram {current_job.__name__}'
                      f' has finished!----')
        if not self.jobs:
            print(f'{Fore.WHITE}' + '-' * 50)
            break
```

### Dekorátor `@consumer`:
Aby nebolo potrebné pred každým prvým použitím generátorového iterátora volať funkciu `next()`, tak súčasťou implementácie je aj prebraný dekorátor z prednášky a cvík (viď. zdroje).

### Koprogramy:
Princíp fungovania všetkých implementovaných koprogramov je nasledovný: V každom koprograme sa nachádza `while` cyklus, ktorý sa začína príkazom `yield`, na ktorom preruší svoje vykonávanie až pokiaľ neobdrží dáta z plánovača pomocou `.send()`. Loopy koprogramov trvajú pokiaľ sa nesplní špecifická podmienka. 

Prvý koprogram `two_strings_fight()` v sebe obsahuje 2 `yieldy`. Porovnávanie nastáva vždy po tom ako koprogram dostane novú dvojicu stringov (a vypočíta si súčty ASCII hodnôt v stringoch). Po obdržaní druhého stringu koprogram porovná hodnoty
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
## Výpis konzoly
Každá iterácia/kolo je oddelená pomlčkami. 
![image](https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/cf2298dc-adc8-47e8-8282-78807539b48c)
```
----Scheduler is ready!----
--------------------------------------------------
Job1: First contestant is: d2mkq7prfg!    
Job2: This is an order! d2mkq7prfg! (1/10)
Job3: Characters won! d2mkq7prfg!
--------------------------------------------------
Job1: Second contestant is: 8u2ch1kzl0?
Job1: Contestant one won! d2mkq7prfg! [998] vs 8u2ch1kzl0? [923]
Job2: This is a question! 8u2ch1kzl0? (2/10)
Job3: Characters won! 8u2ch1kzl0?
--------------------------------------------------
Job1: First contestant is: x512hpzho1!    
Job2: This is an order! x512hpzho1! (3/10)
Job3: Characters won! x512hpzho1!
--------------------------------------------------
Job1: Second contestant is: fkcy4vyl0i!
Job1: Contestant two won! x512hpzho1! [907] vs fkcy4vyl0i! [1014]
----Coprogram two_strings_fight has finished!----
Job2: This is an order! fkcy4vyl0i! (4/10)
Job3: Characters won! fkcy4vyl0i!
--------------------------------------------------
Job2: This is a statement! af6cejpnz0. (5/10)
Job3: Characters won! af6cejpnz0.
--------------------------------------------------
Job2: This is a statement! 9bwyazlyf4. (6/10)
Job3: Characters won! 9bwyazlyf4.
--------------------------------------------------
Job2: This is a question! o5vkb2gojz? (7/10)
Job3: Characters won! o5vkb2gojz?
--------------------------------------------------
Job2: This is an order! nux406i505! (8/10)     
Job3: Digits won! nux406i505!
----Coprogram digits_vs_chars has finished!----
--------------------------------------------------
Job2: This is a statement! 1m4660vb37. (9/10)
--------------------------------------------------
Job2: This is an order! j2qkbn7u4m! (10/10)       
----Coprogram get_type has finished!----
--------------------------------------------------
```

## Zdroje:
Inšpirácie, využité časti kódu a podobne:
* [README template](https://github.com/matiassingers/awesome-readme)
* [PEP 8 & PEP 257 validator](https://www.codewof.co.nz/style/python3/)
* [Conventional Commits guide](https://www.conventionalcommits.org/en/v1.0.0/)
* [Skripty a teória z predmetu](https://elearn.elf.stuba.sk/moodle/course/view.php?id=699)
* [Inšpirácia koprogramov](https://github.com/tj314/ppds-seminars/blob/ppds2024/lecture11/07-coroutine.py)
* [Consumer dekorátor](https://elearn.elf.stuba.sk/moodle/pluginfile.php/77428/mod_resource/content/0/2024-11.async.pdf)
* [Random string generátor](https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits)

