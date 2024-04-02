# Korosi-111313-PPDS2024-Zadanie-04
## Úlohy zadania
Program násobenia matíc upravte nasledovne:

1) Umožnite program vykonávať ľubovoľnému počtu pracovných uzlov. To znamená,
že počet riadkov matice A nebude musieť byť deliteľný bezo zvyšku počtom
uzlov výpočtu.
2) Na distribúciu podmatic A_i jednotlivým uzlom a poskladanie výslednej
matice C nepoužívajte P2P komunikáciu, ale metódy kolektívnej komunikácie
scatter()/gather().

Požiadavky na dokumentáciu kódu a repozitára zostávajú rovnaké ako v prvých
týždňoch semestra.

Experimentujte s programom a zistite, v ktorej verzii programu (s P2P
distribúciou matice A a skladaním matice C alebo s kolektívnymi operáciami
scatter()/gather()) a s akými parametrami je výhodnejšia tá-ktorá verzia
komunikačných metód. Experiment vhodne dokumentujte a interpretujte jeho
výsledky.

(Celé zadanie a k nemu poskytnuté skripty sú dostupné v sekcii zdroje na konci dokumentácie).
## Implementácia
### 1) P2P verzia
Implementácia verzie P2P spočívala v upravení poskytnutého súboru `mat_par.py` (viď. zdroje). A úlohou bolo umožniť výber ľubovoľného počtu pracovných uzlov, nie len počtu, ktorý by delil počet riadkov matice A bezo zvyšku. Riešenie bolo inšpirované poskytnutým riešením v jazyku C (viď. zdroje). 
Nasledujúce časti kódu predstavujú už upravenú verziu.
```python
avg_rows = nra // nproc
extras = nra % nproc
rows = None
offset = 0

if rank == MASTER:
    print(f"{rank}: Initializing matrices A and B.")
    A = (np.array([i + j for j in range(nra) for i in range(nca)])
         .reshape(nra, nca))
    B = (np.array([i * j for j in range(nca) for i in range(ncb)])
         .reshape(nca, ncb))
    rows = avg_rows + 1 if extras else avg_rows

    for proc in range(nproc):
        rows_for_process = avg_rows + 1 if proc < extras else avg_rows
        if proc == MASTER:
            A_loc = A[offset:(offset + rows_for_process)]
            offset += rows_for_process
            continue
        comm.send(A[offset:(offset + rows_for_process)], dest=proc)
        offset += rows_for_process
else:
    A_loc = comm.recv()
    rows = A_loc.shape[0]
    B = None

B = comm.bcast(B, root=MASTER)
```
Na rozdiel od pôvodneho riešenia nové riešenie využíva okrem `rows` aj `avg_rows`, `extras` a `offset`. Premenná `avg_rows` predstavuje priemerný počet riadkov pre pracovný uzol, `extras` predstavuje počet riadkov, ktoré by sa pri rovnomernom rozdelení medzi pracovné uzly nikam nedostali, `offset` sa využíva pre správne indexovanie v matici A.
Princíp fungovania implementácie distribúcie podmatíc je v novom riešení nasledovný:
1) MASTER vytvorí matice A a B a následne si určí hodnotu `rows` podľa toho či existujú riadky navyše (`extras`).
2) V loope prejde každý pracovný uzol VRÁTANE samého seba a zistí koľko riadkov má daný uzol spracovať (ak by sme mali `n` extra riadkov, tak si prvých `n` uzlov zoberie o jeden riadok navyše). U samého seba si akurát sám určí `A_loc` a posunie `offset`, tak aby pri nasledujúcom kroku sa pre ďalší pracovný uzol brali riadky od riadky matice A, ktoré MASTER u seba v `A_loc` nepokryl.
3) Rovnakou logikou ako v bode 2) následne MASTER vytvára a posiela `A_loc` ostatným pracovným uzlom.
4) Pracovné uzly, ktoré NIE SÚ MASTER sa dostanú do vetvy `else`, kde čakajú na dáta od MASTERa.
5) Následne sa pomocou `comm.bcast()` pošle každému pracovnému uzlu matica B.

```python
if rank == MASTER:
    C = np.zeros((nra, ncb), dtype=int)
    offset = 0
    for proc in range(nproc):
        rows_for_process = avg_rows + 1 if proc < extras else avg_rows
        if proc == MASTER:
            C[offset:(offset + rows_for_process)] = C_loc
            offset += rows_for_process
            continue
        C[offset:(offset + rows_for_process)] = comm.recv(source=proc)
        offset += rows_for_process
    print(f"{rank}: Here is the result matrix:")
    print(C)
else:
    comm.send(C_loc, dest=MASTER)
```
Druhý útržok z kódu, ktorý bol upravený funguje následovne:
1) MASTER si vytvorí celú, nulami naplnenú maticu C, ktorá reprezentuje výsledok výpočtu.
2) Následne vstúpi do loopu, kde si na začiatku podobne ako v predchádzajúcom prípade vypočíta pre daný proces počet spracovávaných riadkov. Následne ak "kontroluje sámeho seba", tak vloží na začiatok matice C svoj výsledok `C_loc` (keďže MASTER má u nás ID=0, tak sa kontroluje ako prvý, offset na nule zaručí, že vloží svoje dáta na začiatok a premenná `rows_for_process` zaručí, že sa tam vložia všetky vypočítané riadky pracovného uzlu). Následne už len pripočíta offset.
3) Ak `proc` v loope nereprezentuje MASTERa, tak MASTER dáta získa pomocou `comm.recv(source=proc)`, tieto dáta mu posielajú všetky ostatné uzly v `else` vetve. Keďže MASTER ide v loope proces za procesom, tak sa C postupne naplní ("zhora nadol").

### 2) Verzia kolektívnej komunikácie 
## Analýza výsledkov
## Zdroje
Inšpirácie, využité časti kódu a podobne:
* [README template](https://github.com/matiassingers/awesome-readme)
* [Využité poskytnuté skripty a zadanie](https://elearn.elf.stuba.sk/moodle/mod/folder/view.php?id=27376)
* [Využitý poskytnutý skript zo zdrojov riešenia v jazyku C](https://kurzy.kpi.fei.tuke.sk/pp/labs/pp_mm.c)
* [PEP 8 & PEP 257 validator](https://www.codewof.co.nz/style/python3/)
* [PEP 8 validator](https://pypi.org/project/pycodestyle/)
* [Conventional Commits guide](https://www.conventionalcommits.org/en/v1.0.0/)
* [Teoretické časti boli vysvetlené na základe vedomostí získaných na prednáške a seminári na predmete PPDS](https://uim.fei.stuba.sk/predmet/i-ppds/)
* [Dokumentácia k mpi4py](https://mpi4py.readthedocs.io/en/stable/tutorial.html)
* [Matplotlib grouped bar chart with labels](https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py)
