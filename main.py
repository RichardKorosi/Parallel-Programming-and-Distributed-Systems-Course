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
                        desc=f'Task {name} downloading: {url}',
                        unit='B',
                        unit_scale=True,
                ) as pbar:
                    chunk_size = total_size // 100
                    async for chunk in response.content.iter_chunked(chunk_size):
                        f.write(chunk)
                        pbar.update(len(chunk))
                        await asyncio.sleep(0.05)



async def main():
    work_queue = asyncio.Queue()

    urls = [
        'https://ploszek.com/ppds/2024-11.async.pdf',
        'https://ploszek.com/ppds/2024-12.async2.pdf',
        'https://ploszek.com/ppds/2024-05.1.Paralelne_vypocty_2.pdf',
    ]

    for url in urls:
        await work_queue.put(url)

    a = asyncio.gather(
        task('One', work_queue),
        task('Two', work_queue),
        task('Three', work_queue)
    )
    await a


if __name__ == '__main__':
    asyncio.run(main())
