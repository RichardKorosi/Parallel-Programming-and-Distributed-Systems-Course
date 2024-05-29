"""This file is implementation of the 'twelfth' assignment of the PPDS.

The solution of this assignment was inspired by the following source(s):
PPDS course code examples: https://shorturl.at/PxxIS
Rich progress bar: https://shorturl.at/4a9AD

More info about the assignment can be found in the README.md document.
"""

import asyncio
import aiohttp
import os
from rich.progress import Progress


async def task(name, work_queue, progress):
    """Download files from the URLs in the work queue.

    More specifically, this function downloads the files
    from the URLs in the work queue.
    The progress bar is updated during the download process.

    Keyword arguments:
    name -- the name of the task
    work_queue -- the work queue with the URLs
    progress -- the progress bar
    """
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
                        progress.update(task_id, advance=len(chunk),
                                        description=f"Task "
                                                    f"{name} downloading: "
                                                    f"{url} ({downloaded_size}"
                                                    f"/{total_size} bytes)")


async def main():
    """Execute the main program.

    More specifically, this function creates a work
    queue and fills it with the URLs. Then it starts three
    tasks that download the files from the URLs in the work
    queue.
    """
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


if __name__ == '__main__':
    asyncio.run(main())
