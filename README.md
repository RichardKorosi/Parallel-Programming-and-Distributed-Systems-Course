# Korosi-111313-PPDS2024-Zadanie-12
## Úlohy zadania:
Cieľom zadania je vytvoriť asynchrónnu aplikáciu, ktorá bude schopná sťahovať súbory cez
protokol HTTP(S) a zobrazovať priebežný stav sťahovania vo forme vizuálneho progress baru.
Aplikácia by mala byť schopná sťahovať niekoľko súborov naraz. V implementácii musí byť
ukážka sťahovania aspoň dvoch súborov.
1) Jeden progress bar ukazuje priebeh sťahovania jedného súboru.
2) Vo výstupe aplikácie je pri progress bare vypísaná adresa súboru (odkiaľ sa sťahuje).
3) Súbor bude stiahnutý na disk.

## Implementácia:
Časti implementácie boli inšpirované a prebrané z poskytnutých kódov z cvičení (viď. zdroje).

### Main
V main funkcii sa najprv vytvorí asynchrónna rada a následne sa do nej vložia URL adresy.
Následne sa pomocou `asyncio.gather` zavolajú 3 `Task-y` s parametrami
1) Názov Task-u (One, Two, Three)
2) Asynchrónna rada s URL adresami
3) Inštancia triedy Progress (viď. zdroje `Progress bar`)
```py
async def main():
    work_queue = asyncio.Queue()
    urls = [
        'https://ploszek.com/ppds/2024-04.Paralelne_vypocty_1.pdf',
        'https://ploszek.com/ppds/2024-05.1.Paralelne_vypocty_2.pdf',
        'https://ploszek.com/ppds/2024-06.Paralelne_vypocty_3.pdf',
        'https://ploszek.com/ppds/2024-08.cuda.pdf',
        'https://ploszek.com/ppds/2024-11.async.pdf',
        'https://ploszek.com/ppds/2024-12.async2.pdf',
    ]
    for url in urls:
        await work_queue.put(url)
    with Progress() as progress:
        a = asyncio.gather(
            task('One', work_queue, progress),
            task('Two', work_queue, progress),
            task('Three', work_queue, progress)
        )
        await a
```

### Task
Funkcia task už slúži na asynchrónne sťahovanie súborov.
Funkcia najskôr vytvorí reláciu (triedu) `ClientSession` s názvom session. Následne vojde do cyklu, v ktorom iteruje cez asynchrónnu radu a v prípade, že nie je prázda zoberie si z nej URL.
`Await` pri získavaní URL zabezpečí, že funkcia začne (asynchrónne) čakať na dostupnosť položky v rade a teda ostatné asynchrónne funkcie môžu zatiaľ pokračovať.
Po získaní URL spraví funkcia asynchrónnu `GET` požiadavku na danú URL adresu, odpoveď si uloží do triedy `ClientObject`, v našom prípade s názvom `response` (viď. zdroje `Asyncio Client Quickstart`).
Následne funkcia získa veľkosť sťahovaného súboru, jeho názov a pridá úlohu do sledovania a vráti jej ID (viď. zdroje `Progress bar`).

```py
async def task(name, work_queue, progress):
    async with aiohttp.ClientSession() as session:
        while not work_queue.empty():
            url = await work_queue.get()
            async with session.get(url) as response:
                total_size = int(response.headers.get('content-length', 0))
                filename = os.path.basename(url)
                task_id = progress.add_task(f"Task {name} downloading: "
                                            f"{url}", total=total_size, )
                with open(filename, 'wb') as file:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)
                        downloaded_size = os.path.getsize(filename)
                        progress.update(task_id, advance=len(chunk), description=f"Task "
                                                    f"{name} downloading: "
                                                    f"{url} ({downloaded_size}"
                                                    f"/{total_size} bytes)")

```
Následne otvorí súbor v režime na zápis a vojde do cyklu.
V cykle sa najskôr pokúsi prečítať časť dát (1024 bajtov, v prípade že ostáva menej bajtov prečíta ich všetky do konca). Ak sa funkcii nepodarí už prečítať žiadne dáta (je už na konci), tak sa cyklus preruší.
V opačnom prípade zapíše do súboru daný `chunk` dát a zaktualizuje aktuálnu veľkosť sťahovaného súboru a následne zaktualizuje aj samotný progress bar. Pri získavaní časti/chunk-u dát sa opäť volá aj `await`, to zapríčiní, že sa funkcia začne asynchrónne čakať kým neobdrží potrebné dáta (kým sa nestiahnu). Počas doby čakania teda neblokuje iné asynchrónne funkcie a teda umožňuje ich vykonávanie.


## Výsledok:
![ezgif-3-c9e5d7c30a](https://github.com/RichardKorosi/Korosi-111313-PPDS2024/assets/99643046/e0068409-e8b6-44cb-921c-850aa2eddbc8)


## Zdroje:
Inšpirácie, využité časti kódu a podobne:
* [README template](https://github.com/matiassingers/awesome-readme)
* [PEP 8 & PEP 257 validator](https://www.codewof.co.nz/style/python3/)
* [Conventional Commits guide](https://www.conventionalcommits.org/en/v1.0.0/)
* [Skripty a teória z predmetu](https://elearn.elf.stuba.sk/moodle/course/view.php?id=699)
* [Využité časti kódu z cvičení](https://shorturl.at/PxxIS)
* [Progress bar](https://shorturl.at/4a9AD)
* [Asyncio Client Quickstart](https://docs.aiohttp.org/en/stable/client_quickstart.html)
* [ChatGPT](https://chatgpt.com)
* [Github copilot](https://github.com/features/copilot)
