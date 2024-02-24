"""This file is implementation of the second assignment of the PPDS."""

__author__ = "Richard Körösi"

from colorama import Fore
from fei.ppds import Thread, Semaphore, print, Mutex
from time import sleep

savages = 5
pot_capacity = 7


class Shared:
    """This class represents shared data."""

    def __init__(self):
        """Initialize shared data."""
        self.mutex = Mutex()
        self.goulash_portions = 0
        self.full_pot = Semaphore(0)
        self.empty_pot = Semaphore(0)

        self.waiting_room = Semaphore(0)
        self.dinner_table = Semaphore(0)


def main():
    shared = Shared()
    savage_threads = []
    for i in range(savages):
        savage_threads.append(Thread(daily_eating, shared, f"Savage({i})"))
    for i in range(savages):
        savage_threads[i].join()


def daily_eating(shared, savage_name):
    print(f"{Fore.RED}{savage_name} is hungry.")


if __name__ == '__main__':
    main()
