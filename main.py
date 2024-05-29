from tqdm import tqdm
import asyncio
import aiohttp
import time


async def task(name, work_queue):
    async with aiohttp.ClientSession() as session:
        while not work_queue.empty():
            url = await work_queue.get()
            print(f'Task {name} getting url: {url}')
            time_start = time.perf_counter()
            async with session.get(url) as response:
                await response.text()
            elapsed = time.perf_counter() - time_start
            print(f'Task {name} elapsed time: {elapsed:.1f}')


async def main():
    work_queue = asyncio.Queue()
    urls = [
        'http://google.com',
        'http://flickr.com',
        'https://microsoft.com',
        'http://facebook.com',
        'http://stuba.sk',
        'http://uim.fei.stuba.sk',
    ]

    for url in urls:
        await work_queue.put(url)

    time_start = time.perf_counter()

    a = asyncio.gather(
        task('One', work_queue),
        task('Two', work_queue),
        task('Three', work_queue),
    )
    await a
    elapsed = time.perf_counter() - time_start
    print(f'\n Total elapsed time: {elapsed:.1f}')


if __name__ == '__main__':
    asyncio.run(main())
