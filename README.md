# Korosi-111313-PPDS2024-Zadanie-11
## Úlohy zadania:
1) Implementujte plánovač pre koprogramy založené na rozšírených generátoroch (round-robin plánovanie).
2) Plánovač by mal reagovať na ukončenie koprogramu (zachytiť výnimku StopIteration) informačným výpisom.
3) Pripravte ukážku v main funkcii pre aspoň 3 koprogramy.
4) Dokumentácia: stručne slovne vysvetlite implementáciu.
## Implementácia:
### Plánovač:
Implementácia zadania spočívala vo vytvorení classy `Scheduler`, ktorá v nekonečnom loope dookola (round-robin štýlom) posiela dáta koprogramom.
```py
# Main funkcia
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
```py
# Scheduler metody
def __init__(self):
    self.jobs = []

def add_job(self, it):
    self.jobs.append(it)

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
                      f'has finished!----')
        if not self.jobs:
            print(f'{Fore.WHITE}' + '-' * 50)
            break
```
Metóda `start` v nekonečnom loope generuje dáta (stringy), s ktorými následne koprogramy pracujú. Prechádza cez každý ešte neukončený koprogram a pomocou `.send(data)`
danému koprogramu dáta. Taktiež ošetruje aj `StopIteration` výnimku, ktorá nastane pri ukončení koprogramu, v takom prípade vymaže daný koprogram z listu, cez ktorý iteruje.
Ak je list už prázdny (každý koprogram už skončil), tak sa celý loop `breakne`.
### Koprogramy:
Prvý koprogram v sebe obsahuje 2 `yieldy`. Porovnávanie nastáva vždy po tom ako koprogram dostane novú dvojicu stringov ( a vypočíta si súčty ASCII hodnôt v stringoch). Po obdržaní druhého stringu koprogram porovná hodnoty
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
