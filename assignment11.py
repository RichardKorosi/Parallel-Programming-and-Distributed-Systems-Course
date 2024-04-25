from typing import Callable
import random
import string

def consumer(func: Callable) -> Callable:
    def wrapper(*args, **kw):
        it = func(*args, **kw)
        next(it)
        return it

    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper


class Scheduler:
    def __init__(self):
        self.jobs = [find_a("a"), get_type()]
        print('Scheduler is ready!')

    def _add_job(self, it):
        it.send(''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + random.choice(['!', '?', '.', ' ']))

    def start(self):
        try:
            while True:
                for job in self.jobs:
                    self._add_job(job)
                print('---')
        except StopIteration:
            print('Scheduler is done!')

@consumer
def find_a(substring: str):
    while True:
        text = yield
        if substring in text:
            print(f'T1: I found a {substring}!', text)
        else:
            print(f'T1: I did not find a {substring}!', text)

@consumer
def get_type():
    x = 0
    while x < 10:
        text = yield
        if "!" in text:
            print(f'T2: This is order text! {text} ({x+1}/10)')
        elif "?" in text:
            print(f'T2: This is question text! {text} ({x+1}/10)')
        elif "." in text:
            print(f'T2: This is statement text! {text} ({x+1}/10)')
        else:
            print(f'T2: This is unknown text! {text} ({x+1}/10)')
        x += 1


def main():
    scheduler = Scheduler()
    scheduler.start()

if __name__ == "__main__":
    main()