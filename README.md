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
## Implementácia
### 1)
### 2)
## Analýza výsledkov
## Zdroje
Inšpirácie, využité časti kódu a podobne:
* [README template](https://github.com/matiassingers/awesome-readme)
* [Využité poskytnuté skripty a zadanie](https://elearn.elf.stuba.sk/moodle/mod/folder/view.php?id=27376)
* [PEP 8 & PEP 257 validator](https://www.codewof.co.nz/style/python3/)
* [PEP 8 validator](https://pypi.org/project/pycodestyle/)
* [Conventional Commits guide](https://www.conventionalcommits.org/en/v1.0.0/)
* [Teoretické časti boli vysvetlené na základe vedomostí získaných na prednáške a seminári na predmete PPDS](https://uim.fei.stuba.sk/predmet/i-ppds/)
* [Dokumentácia k mpi4py](https://mpi4py.readthedocs.io/en/stable/tutorial.html)
* [Matplotlib grouped bar chart with labels](https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py)
