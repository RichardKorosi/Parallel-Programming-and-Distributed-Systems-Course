"""This file is implementation of the 'eleventh' assignment of the PPDS."""

__author__ = "Richard Körösi"

from typing import Callable
import random
import string
from time import sleep
from colorama import Fore


def consumer(func: Callable) -> Callable:
    """Create decorator for the consumer functions."""

    def wrapper(*args, **kw):
        it = func(*args, **kw)
        next(it)
        return it

    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper


class Scheduler:
    """Scheduler class for the coroutines."""

    def __init__(self):
        """Initialize the scheduler.

        Create an empty list for the coroutines.
        And inform the user that the scheduler is ready.
        """
        self.jobs = []
        print(f'{Fore.RED}----Scheduler is ready!----')

    def add_job(self, it):
        """Add coroutine to the scheduler.

        Keyword arguments:
        it -- coroutine to be added
        """
        self.jobs.append(it)

    def start(self):
        """Start the scheduler.

        More specifically, it generates random data and sends it to the
        coroutines in the infinite loop. When all coroutines are finished,
        the scheduler stops.
        """
        while True:
            rand = random.choices(string.ascii_lowercase + string.digits, k=10)
            data = ''.join(rand)
            data += random.choice(['!', '?', '.'])
            sleep(0.2)

            print(f'{Fore.WHITE}' + '-' * 50)
            for job in self.jobs[:]:
                try:
                    current_job = job
                    job.send(data)
                except StopIteration:
                    self.jobs.remove(current_job)
                    print(f'{Fore.RED}----Coprogram {current_job.__name__}'
                          f'has finished!----')
            if not self.jobs:
                print(f'{Fore.WHITE}' + '-' * 50)
                break


@consumer
def two_strings_fight():
    """Compare two strings based on their ASCII values.

    More specifically, after the second yield function compares
    the two strings based on their ASCII values and prints the result.
    If second string wins, the coroutine finishes.
    """
    while True:
        text1 = yield
        sum1 = sum(ord(c) for c in text1)
        print(f'{Fore.LIGHTCYAN_EX}Job1: First contestant is: {text1}')

        text2 = yield
        sum2 = sum(ord(c) for c in text2)
        print(f'{Fore.LIGHTCYAN_EX}Job1: Second contestant is: {text2}')

        if sum1 > sum2:
            print(f'{Fore.LIGHTCYAN_EX}Job1: Contestant one won! '
                  f'{text1} [{sum1}] vs {text2} [{sum2}]')
        elif sum1 == sum2:
            print(f'{Fore.LIGHTCYAN_EX}Job1: It is a draw! '
                  f'{text1} [{sum1}] vs {text2} [{sum2}]')
        else:
            print(f'{Fore.LIGHTCYAN_EX}Job1: Contestant two won! '
                  f'{text1} [{sum1}] vs {text2} [{sum2}]')
            break


@consumer
def get_type():
    """Determine the type of the sentence.

    More specifically, this function determines the type of the
    sentence based on the last character of the sentence.
    After 10th sentence, the coroutine finishes.
    """
    x = 0
    while x < 10:
        text = yield
        if "!" in text:
            print(f'{Fore.LIGHTGREEN_EX}Job2: This is an order! '
                  f'{text} ({x + 1}/10)')
        elif "?" in text:
            print(f'{Fore.LIGHTGREEN_EX}Job2: This is a question! '
                  f'{text} ({x + 1}/10)')
        elif "." in text:
            print(f'{Fore.LIGHTGREEN_EX}Job2: This is a statement! '
                  f'{text} ({x + 1}/10)')
        x += 1


@consumer
def digits_vs_chars():
    """Compare the number of digits and characters in the sentence.

    More specifically, this function compares amount of digits and
    characters in the sentence. If digits win, the coroutine finishes.
    """
    while True:
        text = yield
        digits = sum(c.isdigit() for c in text)
        chars = sum(c.isalpha() for c in text)
        if digits > chars:
            print(f'{Fore.LIGHTMAGENTA_EX}Job3: Digits won! {text}')
            break
        elif digits == chars:
            print(f'{Fore.LIGHTMAGENTA_EX}Job3: It is a draw! {text}')
        else:
            print(f'{Fore.LIGHTMAGENTA_EX}Job3: Characters won! {text}')


def main():
    """Create and start the scheduler in the main function."""
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
