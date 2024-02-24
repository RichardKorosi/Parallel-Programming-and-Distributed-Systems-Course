"""This file is implementation of the second assignment of the PPDS."""

__author__ = "Richard Körösi"

from colorama import Fore, Back, Style
from fei.ppds import Thread, Semaphore, print, Mutex
from time import sleep

savages = 5
pot_capacity = 3


class Shared:
    """This class represents shared data."""

    def __init__(self):
        """Initialize shared data."""
        self.mutex = Mutex()
        self.goulash_portions = pot_capacity
        self.waiting_savages = 0
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
    cook = Thread(cook_goulash, shared, "Cook")
    cook.join()


def daily_eating(shared, savage_name):
    # while True:
    waiting_room_barrier(shared, savage_name)
    sleep(1)
    dinner_table_barrier(shared, savage_name)
    sleep(1)


def waiting_room_barrier(shared, savage_name):
    shared.mutex.lock()
    shared.waiting_savages += 1
    print(f"{Fore.LIGHTMAGENTA_EX}{savage_name} is waiting for others. ({shared.waiting_savages}/{savages})")
    if shared.waiting_savages == savages:
        shared.waiting_savages = 0
        shared.waiting_room.signal(savages)
    shared.mutex.unlock()
    shared.waiting_room.wait()


def dinner_table_barrier(shared, savage_name):
    shared.mutex.lock()
    shared.waiting_savages += 1
    if shared.waiting_savages == savages:
        shared.waiting_savages = 0
        shared.dinner_table.signal(savages)
    shared.mutex.unlock()
    shared.dinner_table.wait()
    print(f"{Fore.YELLOW}{savage_name}: We are all here, let's eat!")


def cook_goulash(shared, cook_name):
    shared.empty_pot.wait()
    while shared.goulash_portions < pot_capacity:
        shared.goulash_portions += 1
        print(f"{Fore.LIGHTBLUE_EX}{cook_name} is cooking.({shared.goulash_portions}/{pot_capacity}).")
    print(f"{Fore.LIGHTBLUE_EX}{cook_name} has cooked full pot of goulash.")
    shared.full_pot.signal()
    shared.empty_pot.wait()


if __name__ == '__main__':
    main()
