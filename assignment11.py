from typing import Callable
import random
import string
from time import sleep
from colorama import Fore

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
        self.jobs = []
        print(f'{Fore.RED}----Scheduler is ready!----')

    def add_job(self, it):
       self.jobs.append(it)

    def start(self):
        while True:
            data = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3)) + random.choice(['!', '?', '.'])
            sleep(0.2)

            print(f'{Fore.WHITE}' + '-'*50)
            for job in self.jobs[:]:
                try:
                    current_job = job
                    job.send(data)
                except StopIteration:
                    self.jobs.remove(current_job)
                    print(f'{Fore.RED}----Coprogram {current_job.__name__} has finished!----')
                    continue
            if not self.jobs:
                print(f'{Fore.WHITE}' + '-'*50)
                break

@consumer
def two_strings_fight():
    while True:
        text1 = yield
        sum1 = sum(ord(c) for c in text1)
        print(f'{Fore.LIGHTCYAN_EX}T1: First contestant is: {text1}')

        text2 = yield
        sum2 = sum(ord(c) for c in text2)
        print(f'{Fore.LIGHTCYAN_EX}T1: Second contestant is: {text2}')

        if sum1 > sum2:
            print(f'{Fore.LIGHTCYAN_EX}T1: Contestant one won! {text1} [{sum1}] vs {text2} [{sum2}]')
        elif sum1 == sum2:
            print(f'{Fore.LIGHTCYAN_EX}T1: It is a draw! {text1} [{sum1}] vs {text2} [{sum2}]')
        else:
            print(f'{Fore.LIGHTCYAN_EX}T1: Contestant two won! {text1} [{sum1}] vs {text2} [{sum2}]')
            break
        

@consumer
def get_type():
    x = 0
    while x < 10:
        text = yield
        if "!" in text:
            print(f'{Fore.LIGHTGREEN_EX}T2: This is an order! {text} ({x+1}/10)')
        elif "?" in text:
            print(f'{Fore.LIGHTGREEN_EX}T2: This is a question! {text} ({x+1}/10)')
        elif "." in text:
            print(f'{Fore.LIGHTGREEN_EX}T2: This is a statement! {text} ({x+1}/10)')
        x += 1

@consumer
def digits_vs_chars():
    while True:
        text = yield
        digits = sum(c.isdigit() for c in text)
        chars = sum(c.isalpha() for c in text)
        if digits > chars:
            print(f'{Fore.LIGHTMAGENTA_EX}T3: Digits won! {text}')
            break
        elif digits == chars:
            print(f'{Fore.LIGHTMAGENTA_EX}T3: It is a draw! {text}')
        else:
            print(f'{Fore.LIGHTMAGENTA_EX}T3: Characters won! {text}')



def main():
    scheduler = Scheduler()
    job1 = two_strings_fight()
    job2 = get_type()
    job3 = digits_vs_chars()
    scheduler.add_job(job1)
    scheduler.add_job(job2)
    scheduler.add_job(job3)
    scheduler.start()

if __name__ == "__main__":
    main()