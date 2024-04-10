# Korosi-111313-PPDS2024-Zadanie-04
## Úlohy zadania
1) Implementujte algoritmus samplesort pre Numba CUDA.
2) Porovnajte paralelný samplesort so sériovým triediacim algoritmom na troch rádovo odlišných vstupoch.
3) Dokumentácia: vysvetlite implementáciu a zdôvodnite vybrané hodnoty pre počet blokov a počet vlákien.

## Implementácia
Nasledovná časť implementácie sa sústredí na jednu iteráciu vykonávanú v programe (pre pole `array`). Implementácia algoritmu samplesort bola inšpirovaná pseudokódom poskytnutom na Wikipedii (viď. zdroje).
### Vytvorenie splitterov a bucketov
```python
no_splitters = min(56-1, array.shape[0])
splitters = np.random.choice(array, no_splitters, replace=False)
splitters = np.sort(splitters)
buckets = create_buckets(array, splitters)
```
Počet splitterov a teda aj bucketov záleží od  schopností GPU (počet jadier) a veľkosti vstupného poľa. `TODO: XXX`. Splittre sa vyberajú ako náhodné elementy z pola, ktoré chceme zoradiť. Po zoradení vybratých splitterov sa začnú vytvárať buckety.
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

Keďže sa buckety napĺňajú postupne z poľa `array`, tak pokiaľ pole `array` nebolo zoradené (čo predpokladáme, že nebolo), tak ani buckety nebudú zoradené.
### Streamy
```python
streams = [cuda.stream() for _ in range(len(buckets))]

for bucket, stream in zip(buckets, streams):
    buckets_gpu.append(cuda.to_device(bucket, stream=stream))

for bucket, stream in zip(buckets_gpu, streams):
    my_kernel[1, 1, stream](bucket)

for bucket, stream in zip(buckets_gpu, streams):
    result = np.append(result, bucket.copy_to_host(stream=stream))
```
### Sortovanie na GPU
```python
@cuda.jit
def my_kernel(io_array):
    """Sort the array using bubble sort algorithm using GPU.

    Keyword arguments:
    io_array -- the array to be sorted
    """
    for i in range(io_array.size):
        for j in range(i + 1, io_array.size):
            if io_array[i] > io_array[j]:
                io_array[i], io_array[j] = io_array[j], io_array[i]
```
### Porovnanie paralelného a sériového riešenia













## Zdroje
Inšpirácie, využité časti kódu a podobne:
* [README template](https://github.com/matiassingers/awesome-readme)
* [PEP 8 & PEP 257 validator](https://www.codewof.co.nz/style/python3/)
* [Conventional Commits guide](https://www.conventionalcommits.org/en/v1.0.0/)
* [Matplotlib grouped bar chart with labels](https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py)
* [Algoritmus Samplesort - Wikipedia](https://en.wikipedia.org/wiki/Samplesort)
* [Využité poskytnuté skripty z cvičení](https://github.com/tj314/ppds-seminars/tree/ppds2024/seminar8)
* [Teoretické časti boli vysvetlené na základe vedomostí získaných na prednáške a seminári na predmete PPDS](https://uim.fei.stuba.sk/predmet/i-ppds/)

