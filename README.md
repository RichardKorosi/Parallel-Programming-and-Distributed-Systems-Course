# Korosi-111313-PPDS2024-Zadanie-05
## Úlohy zadania:
1) Implementujte algoritmus samplesort pre Numba CUDA.
2) Porovnajte paralelný samplesort so sériovým triediacim algoritmom na troch rádovo odlišných vstupoch.
3) Dokumentácia: vysvetlite implementáciu a zdôvodnite vybrané hodnoty pre počet blokov a počet vlákien.

## Implementácia:
Nasledovná časť implementácie sa sústredí na jednu iteráciu vykonávanú v programe (pre pole `array`). Implementácia algoritmu samplesort bola inšpirovaná pseudokódom poskytnutom na Wikipedii (viď. zdroje).
### Vytvorenie splitterov a bucketov:
```python
no_splitters = min(56-1, array.shape[0])
splitters = np.random.choice(array, no_splitters, replace=False)
splitters = np.sort(splitters)
buckets = create_buckets(array, splitters)
```
Počet splitterov a teda aj bucketov záleží od  schopností GPU (počet jadier) a veľkosti vstupného poľa (počet bucektov je vždy o 1 vyšší ako počet splitterov). Splittre sa vyberajú ako náhodné elementy z pola, ktoré chceme zoradiť. Po zoradení vybratých splitterov sa začnú vytvárať buckety.
#### Experimenty pre získanie optimálneho počtu splitterov/bucketov:
Prvým krokom bolo zistiť počet CUDA jadier GPU. Experimenty boli vykonávané na grafickej karte `NVDIA GeForce RTX 4070 SUPER` s 7168 CUDA jadrami. Pri experimentoch sa porovnávala časová efektivita voči sériovému triediacemu algoritmu, z 10 behov experimentov sa vytvoril priemerný čas.
```py
#Nastavenie:
no_splitters = min(cuda_cores - 1, array.shape[0] - 1)
#Vysledok (ak dict. nema 'no_buckets' jedna sa o seriove riesenie):
{'array_len': 10, 'no_buckets': 10, 'time': 0.004291010003362317}        
{'array_len': 100, 'no_buckets': 100, 'time': 0.04041334000212373}       
{'array_len': 1000, 'no_buckets': 1000, 'time': 0.3578030999953626}      
{'array_len': 10000, 'no_buckets': 7168, 'time': 2.6178648599990995}     
{'array_len': 10, 'time': 9.470000804867595e-06}
{'array_len': 100, 'time': 0.0008480100004817359}
{'array_len': 1000, 'time': 0.08627961999736726}
{'array_len': 10000, 'time': 8.752622479999264}
```
Vyššie zobrazené riešenie už na prvý pohľad vyzerá neoptimálne. Toto riešenie využíva na menších poliach na každý jeden prvok pola jeden bucket a teda jadrá ani nemajú čo triediť a tým pádom toto riešenie akurát stráca čas zbytočným posielaním dát bucketov do/z GPU. Taktiež si môžeme všimnúť, že daná implementácia je efektívnejšia než klasický sériový sort až pri väčších poliach, kde už neplatí `1 jadro = 1 bucket`.
```py
#Nastavenie:
no_splitters = min(cuda_cores // 4, array.shape[0] // 4)
#Vysledok:
{'array_len': 10, 'no_buckets': 3, 'time': 0.009432820002257359}
{'array_len': 100, 'no_buckets': 26, 'time': 0.010621439998794812}       
{'array_len': 1000, 'no_buckets': 251, 'time': 0.09887496000010287}      
{'array_len': 10000, 'no_buckets': 1793, 'time': 0.663486819996615}      
```
Tento experiment bol efektívnejší ako predošlý, ale stále pomerne neefektívny. Ako príklad slúži hneď prvé pole, ktoré sa zbytočne rozdelí až na tri buckety, pritom na takto jednoduchý sort by stačilo využiť jedno CUDA jadro.
```py
#Nastavenie
no_splitters = min(cuda_cores // 100, array.shape[0] // 100)
#Vysledok:
{'array_len': 10, 'no_buckets': 1, 'time': 0.0005901999975321814}
{'array_len': 100, 'no_buckets': 2, 'time': 0.0009817999962251633}
{'array_len': 1000, 'no_buckets': 11, 'time': 0.005294699993100949}
{'array_len': 10000, 'no_buckets': 72, 'time': 0.026504499997827224}
{'array_len': 100000, 'no_buckets': 72, 'time': 0.9641740999941248}   
```
Toto riešnie na prvý pohľad vyzerá už efektívne a správne, ale pri väčšsom zamyslení si môžeme všimnúť fakt, že od dĺžky pola 10000 sa už bude stále využívať len 72 bucketov a tým pádom pri obrovských poliach by už bol tento počet nedostačujúci.
```py
#Nastavenie:
no_splitters = int(array.shape[0] // math.sqrt(cuda_cores))
if no_splitters >= cuda_cores:
    no_splitters = cuda_cores - 1
#Vysledok:
{'array_len': 10, 'no_buckets': 1, 'time': 0.0005918999959249049}
{'array_len': 100, 'no_buckets': 2, 'time': 0.0010583999974187464}
{'array_len': 1000, 'no_buckets': 12, 'time': 0.004690500005381182}
{'array_len': 10000, 'no_buckets': 119, 'time': 0.0439030000125058}
{'array_len': 100000, 'no_buckets': 1182, 'time': 0.4538427999941632}
```
Snahou teda bolo vytvoriť vzorec, ktorý by pri malých poliach vytváral čo najmenej bucketov, ale aby pri veľkých poliach neostal pri príliš málo bucketoch. Momentálne riešenie rozdeluje buckety na základe vzorca `dlzka_pola // odmocnina(pocet_cuda_jadier)`. V priemere dĺžka bucketu je okolo 84, kde ešte nedokonalosti využitého bubble sortu nie sú tak značné a na zoradenie takéhoto bucketu postačí jedno CUDA jadro. Ešte bolo treba ošetriť možnosť kebyže pole je až tak veľké, že by výsledok vyšiel väčší ako počet CUDA jadier.

#### Tvorba bucketov:
```python
def create_buckets(array, splitters):
    no_buckets = len(splitters) + 1
    buckets = [np.empty(0, dtype=np.float32) for _ in range(no_buckets)]

    for element in array:
        b_i = 0
        for splitter in splitters:
            if element < splitter:
                buckets[b_i] = np.append(buckets[b_i], element)
                break
            b_i += 1
        else:
            buckets[b_i] = np.append(buckets[b_i], element)

    return buckets
```
Funkcia `create_buckets()` vytvorí o jeden bucket viac ako je splitterov. Buckty sa napĺňajú dátami z poľa, ktoré sa má zoradiť. Princíp fungovania napľňovania bucketov je nasledovný:
1) Prvý bucket obsahuje všetky prvky, ktoré sú menšie ako prvý splitter.
2) Druhý bucket obsahuje všetky prvky, ktoré sú menšie ako druhý splitter atď. 
3) Posledný bucket obsahuje všetky prvky, ktoré sú väčšie ako posledný splitter.

Princíp fungovania for...else v algoritme je taký, že ak nastane v loope `break`, tak sa else vetva algoritmu nevykoná. Tým pádom vieme zabezpečiť, že ak je element väčší ako všetky splittre (prejde bez prerušenia celý loop), tak sa dostane do else vetvy, v ktorej sa napĺňa posledný bucket (princíp fungovania viď. zdroje). 

Keďže sa buckety napĺňajú postupne z poľa `array`, tak pokiaľ pole `array` nebolo zoradené (čo predpokladáme, že nebolo), tak ani buckety nebudú zoradené. Zoraďovanie jednotlivých bucketov sa v tejto implementáciu už vykonáva paralelne (viď. ďalšie kapitoly v dokumentácii).
### Streamy:
Riešenie problému bolo implementované za pomoci streamov/prúdov, prúdy sú fronty operácií GPU, ktoré sa vykonávajú v určitom poradí. Streamy využívajú schopnosť GPU prekrývať vykonávanie jadra s operáciami kopírovania pamäte. Každý prúd predstavuje nezávislé vykonávanie príkazov voči ostatným prúdom a teda sa môžu vykonávať konkuretne/asynchrónne. Implementácia funguje na princípe, že každý bucket má vlastný stream (info o streamoch viď. zdroje). Po tejto 'inicializácii' prúdov sa posielajú dáta bucketov do GPU. Následne sa zavolá `my_kernel` s jedným vláknom (blocksPerGrid aj threadsPerBlock = 1). V `my_kernel` sa dané buckety zosortujú a následne sa v poslednom loope získa výsledok poskladaním už zosortovaných bucketov.
```python
streams = [cuda.stream() for _ in range(len(buckets))]

for bucket, stream in zip(buckets, streams):
    buckets_gpu.append(cuda.to_device(bucket, stream=stream))

for bucket, stream in zip(buckets_gpu, streams):
    my_kernel[1, 1, stream](bucket)

for bucket, stream in zip(buckets_gpu, streams):
    result = np.append(result, bucket.copy_to_host(stream=stream))
```
### Sortovanie na GPU:
Zoraďovanie prvkov v bucketoch na GPU sa vykonáva už sériovo (každý bucket je zoraďovaný práve jedným jadrom). Zoraďovací algoritmus je klasický bubble sort. Keďže sa v tejto implementácii už na GPU buckety sortujú sériovo, tak nie je potrebné volať `my_kernel` s `threadsPerBlock` a `blocksPerGrid` s väčšou hodnotou ako 1.
```python
@cuda.jit
def my_kernel(bucket):
    for i in range(bucket.size):
    swapped = False
    for j in range(bucket.size - i - 1):
        if bucket[j] > bucket[j + 1]:
            bucket[j], bucket[j + 1] = bucket[j + 1], bucket[j]
            swapped = True
    if not swapped:
        break
```
### Zhodnotenie a postrehy z implementácie:
Nevýhodou tejto implementácie, je fakt, že sa využíva na sortovanie konkrétneho bucketu len 1 jadro. Keďže základnou vykonávaciou jednotkou je warp, ktorý obsahuje 32 jadier. To znamená, že pracuje v danom warpe len jedno jadro a zvyšok ostáva nevyužitý. Výhodou tohto riešenia však bola jednoduchá implementácia a pri experimentoch (kapitola nižšie) dokázala byť znateľne rýchlejšia ako čisto sériové sortovanie poľa. 
## Porovnanie paralelného a sériového riešenia:














## Zdroje:
Inšpirácie, využité časti kódu a podobne:
* [README template](https://github.com/matiassingers/awesome-readme)
* [PEP 8 & PEP 257 validator](https://www.codewof.co.nz/style/python3/)
* [Conventional Commits guide](https://www.conventionalcommits.org/en/v1.0.0/)
* [Teória o CUDA streamoch](https://turing.une.edu.au/~cosc330/lectures/display_notes.php?lecture=22)
* [Matplotlib grouped bar chart with labels](https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py)
* [Algoritmus Samplesort - Wikipedia](https://en.wikipedia.org/wiki/Samplesort)
* [Algoritmus Bubblesort - GeeksForGeeks](https://www.geeksforgeeks.org/bubble-sort/)
* [Algoritmus for...else - W3Schools](https://www.w3schools.com/python/gloss_python_for_else.asp)
* [Využité poskytnuté skripty z cvičení](https://github.com/tj314/ppds-seminars/tree/ppds2024/seminar8)
* [Teoretické časti boli vysvetlené na základe vedomostí získaných na prednáške a seminári na predmete PPDS](https://uim.fei.stuba.sk/predmet/i-ppds/)

