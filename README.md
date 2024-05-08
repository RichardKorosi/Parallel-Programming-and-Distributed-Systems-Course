# Korosi-111313-PPDS2024-Semestralne-Zadanie
## Úloha zadania:
Napíšte paralelný program, ktorý vyrieši úlohu `Longest Common Subsequence` (ďalej už len LCS) troch reťazcov. Algoritmus môže hľadať výsledný text postupne pre dvojice zdrojov, ale aj takýto spôsob výpočtu je potrebné paralelizovať. Algoritmus ignoruje charakter hviezdičky `*`.
### Príklad správania programu
```
Zdroj A: **textje********skoro***citatelny******unich
Zdroj B: text*v*tejtoknihe****ma*po***usc*****koniec**robot*rozum
Zdroj C: f*te**xt**sa*je***sko*rio**tu*
Výstup: textjeskorotu
```

## Implementácia:
### Zjednodušené vysvetlenie princípu fungovania implementácie
Výsledná implementácia využíva obe možné techniky paralelizácie a teda sa používa MPI a aj CUDA. Prvá paralelizácia je implementovaná za pomoci MPI, kde každý pracovný uzol dostane za úlohu vyriešiť LCS pre dvojicu reťazcov:
```
Pracovný uzol 0 má za úlohu zistiť: LCS(reťazec1, reťazec2)
Pracovný uzol 1 má za úlohu zistiť: LCS(reťazec1, reťazec3)
Pracovný uzol 2 má za úlohu zistiť: LCS(reťazec2, reťazec3)
```
Každý pracovný uzol následne pomocou CUDY počíta LCS. Paralelný výpočet LCS dvoch reťazcov spočíva na princípe počítania antidiagonál v matici `dp`. Antidiagonála sa rozdelí na menšie časti, ktoré následne môžu CUDA jadrá paralelne a nezávislo od seba počítať.
### MPI paralelizácia
Vo funkcii main sa volá (5+1)krát paralelný experiment s tým, že `MASTER` pracovný uzol má na starosti taktiež meranie a zápis časov, aby sa z nich neskôr mohol spraviť priemer. Prvá iterácia pokusu sa ale z výsledkov vymaže, keďže pri prvom spustení CUDY sú výsledky nereprezentatívne a prvá iterácia teda slúži len ako tzv. `CUDA Warmup` (viď. útržok z funkcie main).
```py
main():
    ---------------------------------------------------------
    if rank == MASTER:
        times = []
    
    for i in range(5 + 1):
        if rank == MASTER:
            time_start = time.perf_counter()
        parallel_experiment(list_of_jobs, info_about_threads)
        if rank == MASTER:
            times.append(time.perf_counter() - time_start)
    ---------------------------------------------------------
    if rank == MASTER:
        avg_time = sum(times[1:]) / (len(times) - 1)
    ---------------------------------------------------------
    ...
```
Samotná funkcia `parallel_experiment()`, ktorú vykonávajú všetky 3 pracovné uzly má nasledovnú logiku: Každý pracovný uzol si zistí, nad ktorými dvoma reťazcami má počítať LCS. Ak sa jedná o `MASTER-a` tak po dokončení jeho výpočtu si uloží výsledok do premennej `final_result` a prejde do cyklu, kde sa zavolá `comm.recv`, v tomto cykle obdrží dáta od ostatných pracovných uzlov. Ak sa nejedná o `MASTER-a` tak pracovný uzol po vypočítaní LCS pomocou `comm.send` odošle výsledok `MASTER-ovi`. (POZNÁMKA: Podobným spôsobom sa pre rovnaké reťazce počíta LCS aj sériovo, avšak pre pokus o zachovanie stručnosti dokumentácie sa bude kapitola ohľadom implementácie zaoberať len paralelnou verziou).
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
Cuda paralelizácia začína prípravou dát, rozdelením CUDA jadier a poslaním dát na grafickú kartu. Reťazce sa konvertujú na zoznamy enkódovaných charakterov, aby s nimi mohla CUDA pracovať. Následne sa "reťazce" a matica "dp" pošle na grafickú kartu. Následne sa vypočíta počet antidiagonál, ktoré bude treba spracovať a taktiež sa určí počet CUDA jadier pre daný pracovný uzol. Grafická karta `Nvidia GeForce RTX 4070 Super` má 7168 CUDA jadier. Implementácia má napriamo určený počet jadier na blok (256). Avšak aby každý pracovný uzol mal k dispozícii rovnaký počet CUDA jadier tak počet blokov na gride sa počíta na základe vzorca `cuda_cores / (threads_per_block * 3)`, kde 3 reprezentuje 3 pracovné uzly. Následne sa na základe určených jadier pre pracovný uzol vypočíta jednoduchým vzorcom rozdelí práca medzi samotné CUDA jadrá (koľko prvkov z antidiagonál bude musieť jedno jadro spracovať). Následne sa v cykle postupne vypočítajú všetky antidiagonály a výsledok (naplnená matica "dp") sa pošle z grafickej karty naspäť pracovnému uzlu. Pracovný uzol následne spracuje vyplnenú maticu a získa LCS za pomoci funkcie `get_result()`. 
```py
def cuda_lcs(s1, s2, info_about_threads):
    col_string = s1 if len(s1) < len(s2) else s2
    row_string = s2 if len(s1) < len(s2) else s1
    cuda_cores = 7168

    col_string = list(col_string.encode('utf-8'))
    row_string = list(row_string.encode('utf-8'))
    dp = np.zeros((len(col_string) + 1, len(row_string) + 1), dtype=np.int32)

    dp_cuda = cuda.to_device(dp)
    col_string_cuda = cuda.to_device(col_string)
    row_string_cuda = cuda.to_device(row_string)

    no_anti_diagonal = len(col_string) + len(row_string) - 1

    threads_per_block = 256
    blocks_per_grid = math.floor(cuda_cores / (threads_per_block * 3))
    elements_for_thread = math.ceil(no_anti_diagonal /
                                    (blocks_per_grid * threads_per_block))
    info_about_threads["threads"] = threads_per_block * blocks_per_grid
    info_about_threads["blocks_per_grid"] = blocks_per_grid
    info_about_threads["threads_per_block"] = threads_per_block

    for i in range(1, no_anti_diagonal + 1):
        col = min(i, len(col_string))
        row = i - col + 1

        (cuda_kernel[blocks_per_grid, threads_per_block]
         (dp_cuda, col_string_cuda, row_string_cuda,
          col, row, elements_for_thread))

    dp_result = dp_cuda.copy_to_host()
    col_string = bytes(col_string).decode('utf-8')
    row_string = bytes(row_string).decode('utf-8')

    result = get_result(dp_result, col_string, row_string)
    return result
```
Výpočet jednej antidiagonály sa začína tým, že si CUDA jadro zistí pozíciu, od ktorej má začať. Následne postupuje podľa algoritmu, kde zisťuje či sa na aktuálnej pozícii rovnajú znaky v reťazcoch. Ak sa rovnajú (a nejde o hviezdičku), tak sa na dané políčko zapíše hodnota o 1 väčšia ako sa nachádza na políčku, ktoré je o jednu pozíciu naľavo-hore. Ak sa znaky v reťazcoch nerovnajú vyberá sa maximum z políčok, ktoré sú od aktuálneho políčka naľavo a hore. Algoritmus obsahuje aj ukončovaciu podmienku v prípade, že by posledné jadro malo zadaný väčší počet úloh ako ešte reálne ostáva do konca antidiagonály. 
```py
@cuda.jit
def cuda_kernel(dp, col_string, row_string, start_col,
                start_row, elements_for_thread):
    pos = cuda.grid(1)
    col = start_col - pos * elements_for_thread
    row = start_row + pos * elements_for_thread
    for i in range(elements_for_thread):
        if col < 1 or row >= len(dp[0]):
            break
        if (col_string[col - 1] == row_string[row - 1]
                and col_string[col - 1] != 42):
            dp[col, row] = dp[col - 1, row - 1] + 1
        else:
            dp[col, row] = max(dp[col - 1, row], dp[col, row - 1])
        col -= 1
        row += 1
```
### Finálny výsledok
Po vyplnení "dp" matice si každý pracovný uzol následne zistí samotnú LCS a jej dĺžku vo funkcii `get_result()`. Tento výsledok následne pracovné uzly, ktoré nie sú `MASTER`, posielajú `MASTER-ovi`. Po tom ako `MASTER` dostane aj zvyšné výsledky ostatných pracovných uzlov, vyberie minimálnu hodnotu zo všetkých troch výsledkov a to je výsledný LCS medzi troma reťazcami.
```py
if rank == MASTER:
    min_result = min(final_result, key=lambda x: x[1])
    print("LCS:", min_result[1], end=" ")
```
## Analýza výsledkov:
### Overenie funkčnosti
Overenie funkčnosti spočívalo v porovnávaní výsledkom medzi výsledkami paralelnej verzie, sekvenčnej verzie (ktorá bola implementovaná dynamickým programovaním, ale nie verziou antidiagonál) a verzie tretej strany, ktorá je dostupná na internete (viď. zdroje).
#### Vstup
```py
source1 = ["**textje********skoro***citatelny******unich" * i for i in [1, 5, 15, 25, 35, 45]]
source2 = [("text*v*tejtoknihe****ma*po***usc*****koniec**robot*rozum") * i for i in [1, 5, 15, 25, 35, 45]]
source3 = ["f*te**xt**sa*je***sko*rio**tu*" * i for i in [1, 5, 15, 25, 35, 45]]
--------
source1 = ["**lo***xy**z*n***ge***w**st" * i for i in [1, 5, 15, 25, 35, 45]]
source2 = ["st**o****ma*po***ne***" * i for i in [1, 5, 15, 25, 35, 45]]
source3 = ["l****o**n**g**e***s*t*" * i for i in [1, 5, 15, 25, 35, 45]]
--------
source1 = ["**x***yyyy**z*zz********" * i for i in [1, 5, 15, 25, 35, 45]]
source2 = ["xxyyy**z*zz**x*" * i for i in [1, 5, 15, 25, 35, 45]]
source3 = ["a**b***cd**" * i for i in [1, 5, 15, 25, 35, 45]]
-------
source1 = ["qkajflpwuzvbnmcxieoruytahgdjsqpftzvnklsoirqwpfxvcmznehuytpoasjlxqikwmgfncdybheusjzpwq"]
source2 = ["rwpfqzmvnxylkguhdpotieascbjflkrwpgvnquzymldjcxobvkpytienmrwqalsxfjuqzgoatphvknwcxidbej"]
source3 = ["vcmzujqpnksohbrwigecxyfuqzvdlatpcnrxjsqkiwmgeaopbvnlrykdshcixftuqpajzomfwnkstgubvycxlhei"]

```
#### Výstup
```
LCS: 13 textjeskorotu
LCS: 65 textjeskorotu...textjeskorotu
LCS: 195 textjeskorotu...textjeskorotu
LCS: 325 textjeskorotu...textjeskorotu
LCS: 455 textjeskorotu...textjeskorotu
LCS: 585 textjeskorotu...textjeskorotu
--------
LCS: 3 one
LCS: 23 onestonestonestonestone
LCS: 73 onestonestone...onestonestone
LCS: 123 onestonestone...onestonestone
LCS: 173 onestonestone...onestonestone
LCS: 223 onestonestone...onestonestone
--------
LCS: 0 
LCS: 0 
LCS: 0 
LCS: 0 
LCS: 0 
LCS: 0
--------
LCS: 29 vmujqpnksorwfvcnsqiwmgndhujzw
```
### Analýza časov viacerých experimentov
#### Paralelná verzia vs sekvenčná verzia
Táto časť dokumentácie slúži na zobrazenie a porovnanie výsledkov medzi paralelným a sekvenčným prístupom pomocou grafov. Z grafu je možné vyčítať, že pri krátkych reťazcoch je efektívnejšia sekvenčná verzia. Je to z dôvodu, že samotný výpočet trvá krátko a v paralelnej verzii sa stráca čas posielaním dát medzi pracovnými uzlami medzi sebou a CUDOU. Avšak so zväčšujúcim sa vstupom už jednoznačne vidno lepšiu efektivitu paralelného riešenia.

![image](https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/4266e664-9014-46f1-bf8b-bf863704a52d)

#### Rôzne nastavenia paralelnej verzie
Po porovnaní medzi sekvenčnou a paralelnou verziou prichádza porovnanie rôznych nastavení (počet CUDA jadier prístupných jednému pracovnému uzlu) paralelnej verzie. (POZNÁMKA: sekvenčný experiment bol pre veľké vstupy vypnutý z dôvodu ušetrenia času pri experimentoch).
<table style="width:100%">
  <tr>
    <td align="center"><img src="https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/c79d9f53-1980-4547-a55d-bfbfac73ee75" style="width:100%"></td>
    <td align="center"><img src="https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/30ff3992-31bf-443a-a7e8-ffcc505def79" style="width:100%"></td>
  </tr>
  <tr>
    <td align="center"><img src="https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/9c3cc965-6eeb-44ec-98ec-9004329ce1fe" style="width:100%"></td>
    <td align="center"><img src="https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/58dba4a4-b5e7-4466-920b-b073fce1f122" style="width:100%"></td>
  </tr>
</table>

<table style="width:100%">
  <tr>
    <td align="center"><img src="https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/70a84592-1c97-48d8-a343-90327779d190" style="width:100%"></td>
    <td align="center"><img src="https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/7471f74a-7b64-4350-bdca-4ae4e9c64e68" style="width:100%"></td>
  </tr>
  <tr>
    <td align="center"><img src="https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/21b0f847-3a04-4734-a384-378200c85a34" style="width:100%"></td>
    <td align="center"><img src="https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/23871351-5bb3-4898-bc41-5d62bbe6b400" style="width:100%"></td>
  </tr>
</table>

![image](https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/862c6053-c59a-4a47-8330-995b0a0c2a92)
## Záver:
Z tabuľky a grafov vidno jednoznačný efekt paralelizácie na problém nájdenia LCS medzi troma reťazcami. Pri grafoch a tabuľke, ktoré sa zaoberali porvnaním verzií s rôznym počtom CUDA jadier je taktiež povšimnutiahodný fakt, že zozačiatku boli všetky verzie približne rovnako rýchle a to z dôvodu, že aj verzie s menším počtom CUDA jadier mali dostatok jadier na to aby každé jadro nemuselo počítať príliš veľa elementov v "dp" matici. Pri väčších vstupoch už verzie s nižším počtom CUDA jadier nestíhali, tým najlepším práve z toho dôvodu, že jedno CUDA jadro muselo spracovať už pomerne dlhé časti antidiagonál.

## Zdroje:
Inšpirácie, využité časti kódu a podobne:
* [README template](https://github.com/matiassingers/awesome-readme)
* [PEP 8 & PEP 257 validator](https://www.codewof.co.nz/style/python3/)
* [Conventional Commits guide](https://www.conventionalcommits.org/en/v1.0.0/)
* [Matplotlib grouped bar chart with labels](https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py)
* [Teória ohľadom LCS - externá prednáška](https://cse.buffalo.edu/faculty/miller/Courses/CSE633/Lavanya-Nadanasabapathi-Spring-2022.pdf)
* [Teória ohľadom LCS - prednáška PPDS](https://elearn.elf.stuba.sk/moodle/pluginfile.php/77449/mod_resource/content/1/Prednaska_12.pdf)
* [LCS online 'kalkulátor'](https://www.cs.usfca.edu/~galles/visualization/DPLCS.html)
* [CUDA Warmup](https://shorturl.at/eklAF)






