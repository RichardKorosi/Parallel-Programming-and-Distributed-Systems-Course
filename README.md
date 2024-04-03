# Korosi-111313-PPDS2024-Zadanie-04
## Úlohy zadania
Program násobenia matíc upravte nasledovne:

1) Umožnite program vykonávať ľubovoľnému počtu pracovných uzlov. To znamená,
že počet riadkov matice `A` nebude musieť byť deliteľný bezo zvyšku počtom
uzlov výpočtu.
2) Na distribúciu podmatic `A_i` jednotlivým uzlom a poskladanie výslednej
matice `C` nepoužívajte P2P komunikáciu, ale metódy kolektívnej komunikácie
scatter()/gather().

Požiadavky na dokumentáciu kódu a repozitára zostávajú rovnaké ako v prvých
týždňoch semestra.

Experimentujte s programom a zistite, v ktorej verzii programu (s P2P
distribúciou matice `A` a skladaním matice `C` alebo s kolektívnymi operáciami
scatter()/gather()) a s akými parametrami je výhodnejšia tá-ktorá verzia
komunikačných metód. Experiment vhodne dokumentujte a interpretujte jeho
výsledky.

(Celé zadanie a k nemu poskytnuté skripty sú dostupné v sekcii zdroje na konci dokumentácie).
## Implementácia
### 1) P2P verzia
Implementácia verzie P2P spočívala v upravení poskytnutého súboru `mat_par.py` (viď. zdroje). A úlohou bolo umožniť výber ľubovoľného počtu pracovných uzlov, nie len počtu, ktorý by delil počet riadkov matice `A` bezo zvyšku. Riešenie bolo inšpirované poskytnutým riešením v jazyku C (viď. zdroje). 
Nasledujúce časti kódu predstavujú už upravenú verziu.
```python
avg_rows = nra // nproc
extras = nra % nproc
rows = None
offset = 0

if rank == MASTER:
    print(f"{rank}: Initializing matrices A and B.")
    a = (np.array([i + j for j in range(nra) for i in range(nca)])
         .reshape(nra, nca))
    b = (np.array([i * j for j in range(nca) for i in range(ncb)])
         .reshape(nca, ncb))
    rows = avg_rows + 1 if extras else avg_rows

    for proc in range(nproc):
        rows_for_process = avg_rows + 1 if proc < extras else avg_rows
        if proc == MASTER:
            a_loc = a[offset:(offset + rows_for_process)]
            offset += rows_for_process
            continue
        comm.send(a[offset:(offset + rows_for_process)], dest=proc)
        offset += rows_for_process
else:
    a_loc = comm.recv()
    rows = a_loc.shape[0]
    b = None

b = comm.bcast(b, root=MASTER)
```
Na rozdiel od pôvodneho riešenia nové riešenie využíva okrem `rows` aj `avg_rows`, `extras` a `offset`. Premenná `avg_rows` predstavuje priemerný počet riadkov pre pracovný uzol, `extras` predstavuje počet riadkov, ktoré by sa pri rovnomernom rozdelení medzi pracovné uzly nikam nedostali, `offset` sa využíva pre správne indexovanie v matici A.
Princíp fungovania implementácie distribúcie podmatíc je v novom riešení nasledovný:
1) MASTER vytvorí matice A a B a následne si určí hodnotu `rows` podľa toho či existujú riadky navyše (`extras`).
2) V loope prejde každý pracovný uzol VRÁTANE samého seba a zistí koľko riadkov má daný uzol spracovať (ak by sme mali `n` extra riadkov, tak si prvých `n` uzlov zoberie o jeden riadok navyše). U samého seba si akurát sám určí `A_loc` a posunie `offset`, tak aby pri nasledujúcom kroku sa pre ďalší pracovný uzol brali riadky od riadku matice `A`, ktoré MASTER u seba v `A_loc` nepokryl.
3) Rovnakou logikou ako v bode 2) následne MASTER vytvára a posiela `A_loc` ostatným pracovným uzlom.
4) Pracovné uzly, ktoré NIE SÚ MASTER sa dostanú do vetvy `else`, kde čakajú na dáta od MASTERa.
5) Následne sa pomocou `comm.bcast()` pošle každému pracovnému uzlu matica `B`.

```python
if rank == MASTER:
    c = np.zeros((nra, ncb), dtype=int)
    offset = 0
    for proc in range(nproc):
        rows_for_process = avg_rows + 1 if proc < extras else avg_rows
        if proc == MASTER:
            c[offset:(offset + rows_for_process)] = c_loc
            offset += rows_for_process
            continue
        c[offset:(offset + rows_for_process)] = comm.recv(source=proc)
        offset += rows_for_process
    print(f"{rank}: Here is the result matrix:")
    print(c)
else:
    comm.send(c_loc, dest=MASTER)
```
Druhý útržok z kódu, ktorý bol upravený funguje následovne:
1) MASTER si vytvorí celú, nulami naplnenú maticu `C`, ktorá reprezentuje výsledok výpočtu.
2) Následne vstúpi do loopu, kde si na začiatku podobne ako v predchádzajúcom prípade vypočíta pre daný proces počet spracovávaných riadkov. Následne ak "kontroluje sámeho seba", tak vloží na začiatok matice C svoj výsledok `C_loc` (keďže MASTER má u nás ID=0, tak sa kontroluje ako prvý, offset na nule zaručí, že vloží svoje dáta na začiatok a premenná `rows_for_process` zaručí, že sa tam vložia všetky vypočítané riadky pracovného uzlu). Následne už len pripočíta offset.
3) Ak `proc` v loope nereprezentuje MASTERa, tak MASTER dáta získa pomocou `comm.recv(source=proc)`, tieto dáta mu posielajú všetky ostatné uzly v `else` vetve. Keďže MASTER ide v loope proces za procesom, tak sa C postupne naplní ("zhora nadol").

### 2) Verzia kolektívnej komunikácie
Implementácia verzie kolektívnej komunikácie spočívala v upravení poskytnutého súboru `mat_parsg.py` (viď. zdroje). A úlohou bolo umožniť výber ľubovoľného počtu pracovných uzlov, nie len počtu, ktorý by delil počet riadkov matice `A` bezo zvyšku. Nasledujúce časti kódu predstavujú už upravenú verziu.

```python
a = None
b = None
if rank == MASTER:
    print(f"{rank}: Initializing matrices A and B.")
    a = (np.array([i + j for j in range(nra) for i in range(nca)])
         .reshape(nra, nca))
    a = np.array_split(a, nproc)
    b = (np.array([i * j for j in range(nca) for i in range(ncb)])
         .reshape(nca, ncb))

a_loc = comm.scatter(a, root=MASTER)
b = comm.bcast(b, root=MASTER)
rows = a_loc.shape[0]
```
Táto verzia riešenia nebola inšpirovaná verziou poskytnutou v jazyku C nakoľko tá obsahovala akurát P2P riešenie. Namiesto toho využíva numpy funkciu `array_split()`, ktorá dokáže rovnomerne rozdeliť maticu `A` s tým, že riadky navyše rozdelí rovnakým spôsobom ako v našom predošlom riešení.
Príklad fungovania `array_split` (príklad bol prevzatý a upravený z dokumentácie numpy, viď. zdroje):
```python
>>> x = np.arange(10)
>>> x2 = np.array_split(x, 4)

[array([0, 1, 2]), array([3, 4, 5]), array([6, 7]), array([8, 9])]
```
Po rovnomernom rozdelení matice `A` sa pomocou `comm.scatter()` rozošle každému pracovnému uzlu časť matice `A` a následne pomocou `comm.bcast()` celá matica `B`. Uzol teda môže vykonať násobenie matíc na jeho podprobléme. Každý uzol si však najprv musí overiť, koľko riadková matica `A_loc` mu prišla. To vykoná pomocou príkazu `A_loc.shape[0]`.
```python
c = comm.gather(c_loc, root=MASTER)
if rank == MASTER:
    c = np.array([ss for s in c for ss in s])
    print(f"{rank}: Here is the result matrix:")
    print(c)
```
Následne sa pomocou `comm.gather(root=MASTER)` dáta pošlú a zozbierajú v pracovnom uzle `MASTER`, ktorý ich následne spracuje pre a vypíše do konzoly.
### 3) Výpisy z konzoly
![image](https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/dfc42359-dd2a-47bd-88f1-d04a6fa9ece9)
Obrázok nad textom ukazuje, novo implementované riešenia a pôvodné riešenie (pre prehľadnosť bolo `mat_parsg.py` vynechané). Tento prípad bol pri vybraní pracovných uzlov, ktorých počet delil bezozvyšku počet riadkov matice `A`. Obrázok pod textom ukazuje prípad, kedy tento jav neplatí.
![image](https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/2288a71c-eaea-499b-aaae-013a1e495b09)
Poznámka: Vo finálnom riešení sú všetky pôvodné printy zakomentované. Dôvodom je lepšia čitatelnosť výstupu pre analýzu a porovnanie. V tejto časti boli printy využité na vizualizáciu priebehu programu rovnako ako v vzorovom riešení `mat_par.py` (viď. zdroje). 



## Porovnanie oboch verzií
Táto sekcia sa zoberá porovnaním oboch implementovaných verzií. Na tento účel sa využívajú dve funkcie `measure_version()` a `create_graph()`. V jednoduchosti: vo funkcii `measure_version()` sa 50krát pre každú maticu, ktorá je definovaná priamo vo funkcii, zavolá fukcia podľa zvoleného vstupného parametru. Vždy sa pritom meria čas odkedy bola funkcia zavolaná až pokiaľ neskončí. Následne sa hodnoty spriemerujú. Funkcia následne vráti List slovníkov, ktoré obsahujú podrobnejšie dáta o experimente. 
Funckia `create_graph()` má následne za úlohu vykrelisť graf na základe informácií o experimente, ktoré vznikajú vo funkcii `measure_version()`. Funkcia `create_graph()` bola vytvorená na základe dokumentácie knižnice matplotlib (viď. zdroje).
```python
results2 = measure_version("COLLECTIVE")
results = measure_version("P2P")

if rank == MASTER:
    for result in results:
        print(result, end="\n")
    print("\n")
    for result in results2:
        print(result, end="\n")

if rank == MASTER:
    create_graph(results, results2)
```
Keďže všetky pracovné uzly vykonajú funkciu `measure_version()`, v ktorej sa volajú naše implementované funkcie, tak si musíme určiť, že chceme využiť MASTERove získané dáta z experimentu.
Príklad výpisu výsledkov experimentu:
```
PS C:\Users\koros\SKOLA\PPDS\Zadania\Korosi-111313-PPDS2024> mpiexec -n 7  python .\assignment07.py
{'nra': 256, 'nca': 20, 'ncb': 20, 'time': 0.024013333320617676, 'version': 'P2P', 'nproc': 7}
{'nra': 256, 'nca': 40, 'ncb': 10, 'time': 0.02342719554901123, 'version': 'P2P', 'nproc': 7}
{'nra': 512, 'nca': 50, 'ncb': 20, 'time': 0.10638868808746338, 'version': 'P2P', 'nproc': 7}
{'nra': 512, 'nca': 40, 'ncb': 30, 'time': 0.12710588932037353, 'version': 'P2P', 'nproc': 7}
{'nra': 512, 'nca': 20, 'ncb': 50, 'time': 0.1071474552154541, 'version': 'P2P', 'nproc': 7}


{'nra': 256, 'nca': 20, 'ncb': 20, 'time': 0.02033309459686279, 'version': 'COLLECTIVE', 'nproc': 7}
{'nra': 256, 'nca': 40, 'ncb': 10, 'time': 0.02083247184753418, 'version': 'COLLECTIVE', 'nproc': 7}
{'nra': 512, 'nca': 50, 'ncb': 20, 'time': 0.09581642627716064, 'version': 'COLLECTIVE', 'nproc': 7}
{'nra': 512, 'nca': 40, 'ncb': 30, 'time': 0.11310394287109375, 'version': 'COLLECTIVE', 'nproc': 7}
{'nra': 512, 'nca': 20, 'ncb': 50, 'time': 0.10066853046417236, 'version': 'COLLECTIVE', 'nproc': 7}
```
Na základe nižšie zobrazených obrázkov si môžeme všimnúť, že verzia s kolektívnou komunikáciou je častejšie časovo efektívnejšia ako verzia s P2P. Taktiež si môžeme všimnúť fakt, že viac pracovných uzlov neznamená automaticky lepší čas. Najlepšie výlsedky boli dosiahnuté pri nastavení `nporc = 7`. Následne pri ďalšom zvyšovaní pracovných uzlov sa priemerný čas výpočtov zvyšoval.\
Pri zvolení `nproc = 2` si môžeme všimnúť, že obe verzie boli približne rovnako časovo efektívne. Následne pri zvyšovaní počtu `nproc` na väčších maticiach vidno, že tam je verzia s kolektívnou komunikáciou rýchlejšia, zatiaľ čo pri menších maticiach sa javí byť pomalšia.
![image](https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/c40187ce-d208-464f-af94-2f8ab854e5e7)
![image](https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/90026373-a942-4a17-bba3-08299e533775)
![image](https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/fb401a1b-fdc5-4c6a-a7c2-dcb83188d543)
![image](https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/cd86a1bb-cb7d-42f1-b479-0e150689a8fa)
![image](https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/54836178-968a-48ca-bd29-74a2d429c3a0)





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
* [Numpy array_split](https://numpy.org/doc/stable/reference/generated/numpy.array_split.html)
* [Matplotlib grouped bar chart with labels](https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py)
