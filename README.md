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

## Zdroje:
Inšpirácie, využité časti kódu a podobne:
* [README template](https://github.com/matiassingers/awesome-readme)
* [PEP 8 & PEP 257 validator](https://www.codewof.co.nz/style/python3/)
* [Conventional Commits guide](https://www.conventionalcommits.org/en/v1.0.0/)
* [Skripty a teória z predmetu](https://elearn.elf.stuba.sk/moodle/course/view.php?id=699)
* [Využité časti kódu z cvičení](https://shorturl.at/PxxIS)
* [Progress bar](https://shorturl.at/4a9AD)
* [ChatGPT](https://chatgpt.com)
* [Github copilot](https://github.com/features/copilot)
