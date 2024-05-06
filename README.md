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
### MPI paralelizácia
Vo funkcii main sa volá (5 + 1) paralelný experiment s tým, že `MASTER` pracovný uzol má na starosti taktiež meranie a zápis časov, aby sa z nich neskôr mohol spraviť priemer. Prvá iterácia pokusu následne z výsledkov vymaže, keďže pri prvom spustení CUDY sú výsledky nereprezentatívne a prvá iterácia teda slúži len ako tzv. `CUDA Warmup`.
```py
if rank == MASTER:
    times = []

for i in range(5 + 1):
    if rank == MASTER:
        time_start = time.perf_counter()
    parallel_experiment(list_of_jobs, info_about_threads)
    if rank == MASTER:
        times.append(time.perf_counter() - time_start)
```
Samotná funkcia `parallel_experiment()`, ktorú vykonávajú všetky 3 pracovné uzly má nasledovnú logiku: Každý pracovný uzol si zistí, ktoré nad ktorými dvoma reťazcami má počítať LCS. Ak sa jedná o `MASTER-a` tak po dokončení jeho výpočtu si uloží výsledok do premennej `final_result` a prejde do cyklu, kde sa zavolá `comm.recv`, v tomto cykle obdrží dáta od ostatných pracovných uzlov. Ak sa nejedná o `MASTER-a` tak pracovný uzol po vypočítaní LCS pomocou `comm.send` odošle výsledok `MASTER-ovi`.
```py
def parallel_experiment(list_of_jobs, info_about_threads):
    if rank == MASTER:
        final_result = []

    for i in range(3):
        if rank == i:
            result = cuda_lcs(list_of_jobs[i][0], list_of_jobs[i][1],
                              info_about_threads)

            if rank == MASTER:
                final_result.append(result)
                for j in range(1, nproc):
                    result = comm.recv(source=j)
                    final_result.append(result)
            else:
                comm.send(result, dest=MASTER)

    if rank == MASTER:
        min_result = min(final_result, key=lambda x: x[1])
        print("LCS:", min_result[1], end=" ")
```

### CUDA paralelizácia
