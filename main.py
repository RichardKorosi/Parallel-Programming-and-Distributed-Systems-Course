from tqdm import tqdm
import asyncio
import aiohttp
import os


async def task(name, work_queue):
    async with aiohttp.ClientSession() as session:
        while not work_queue.empty():
            url = await work_queue.get()
            async with session.get(url) as response:
                total_size = int(response.headers.get('content-length', 0))
                filename = os.path.basename(url)

                with open(filename, 'wb') as f, tqdm(
                        total=total_size,
                        unit='B',
                        unit_scale=True,
                        desc=f'Task {name} getting url: {url}'
                ) as pbar:
                    chunk_size = 1024  # 1 KB
                    async for chunk in response.content.iter_chunked(chunk_size):
                        f.write(chunk)
                        pbar.update(len(chunk))


async def main():
    work_queue = asyncio.Queue()
    urls = [
        'https://ploszek.com/ppds/2024-11.async.pdf',
        'https://ploszek.com/ppds/2024-05.1.Paralelne_vypocty_2.pdf',
        'https://ploszek.com/ppds/2024-12.async2.pdf',
    ]

    for url in urls:
        await work_queue.put(url)

    a = asyncio.gather(
        task('One', work_queue),
        task('Two', work_queue),
        task('Three', work_queue),
    )
    await a


if __name__ == '__main__':
    asyncio.run(main())
