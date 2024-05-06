# Korosi-111313-PPDS2024-Semestralne-Zadanie
## Úlohy zadania:
### Opis zadania
Napíšte paralelný program, ktorý vyrieši úlohu `Longest Common Subsequence` (ďalej už len LCS) troch reťazcov. Algoritmus môže hľadať výsledný text postupne pre dvojice zdrojov, ale aj takýto spôsob výpočtu je potrebné paralelizovať. Algoritmus ignoruje charakter hviezdičky `*`.
### Príklad správania programu
```
Zdroj A: **textje********skoro***citatelny******unich
Zdroj B: text*v*tejtoknihe****ma*po***usc*****koniec**robot*rozum
Zdroj C: f*te**xt**sa*je***sko*rio**tu*
Výstup: textjeskorotu
```

## Implementácia
### Zjednodušené vysvetlenie princípu fungovania implementácie
Výsledná implementácia využíva obe možné techniky paralelizácie a teda sa používa MPI a aj CUDA. Prvá paralelizácia je implementovaná za pomoci MPI, kde každý pracovný uzol dostane za úlohu vyriešiť LCS pre dvojicu reťazcov:
```
Pracovný uzol 0 má za úlohu zistiť: LCS(reťazec1, reťazec2)
Pracovný uzol 1 má za úlohu zistiť: LCS(reťazec1, reťazec3)
Pracovný uzol 2 má za úlohu zistiť: LCS(reťazec2, reťazec3)
```
Každý pracovný uzol následne pomocou CUDY počíta LCS. Paralelný výpočet LCS dvoch reťazcov spočíva na princípe počítania antidiagonál v matici `dp`. Antidiagonála sa rozdelí na menšie časti, ktoré následne môžu CUDA jadrá paralelne a nezávislo od seba počítať.
