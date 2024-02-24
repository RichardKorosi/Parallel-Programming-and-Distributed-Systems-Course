"""This file is implementation of the second assignment of the PPDS."""

__author__ = "Richard Körösi"

from colorama import Fore, Style
from fei.ppds import Thread, Semaphore, print, Mutex
from time import sleep

savages = 7
pot_capacity = 5


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
    cook = Thread(cook_goulash, shared, "Cook")
    for i in range(savages):
        savage_threads[i].join()
    cook.join()


def daily_eating(shared, savage_name):
    while True:
        waiting_room_barrier(shared, savage_name)
        sleep(0.5)
        dinner_table_barrier(shared, savage_name)
        sleep(0.5)
        savage_getting_goulash(shared, savage_name)
        sleep(0.5)
        savage_eating(shared, savage_name)
        sleep(0.5)


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


def savage_getting_goulash(shared, savage_name):
    shared.mutex.lock()
    print(f"{Fore.GREEN}{savage_name}: I can see {shared.goulash_portions} portion(s) in the pot.")
    if shared.goulash_portions == 0:
        print(f"{Fore.RED}{savage_name} is telling the cook to cook.")
        shared.empty_pot.signal()
        shared.full_pot.wait()
    print(f"{Fore.GREEN}{savage_name} has taken 1 portion.")
    shared.goulash_portions -= 1
    shared.mutex.unlock()


def savage_eating(shared, savage_name):
    print(f"{Fore.LIGHTBLUE_EX}{savage_name} is eating." + Style.RESET_ALL)


def cook_goulash(shared, cook_name):
    while True:
        shared.empty_pot.wait()
        while shared.goulash_portions < pot_capacity:
            shared.goulash_portions += 1
            print(f"{Fore.LIGHTCYAN_EX}{cook_name} is cooking.({shared.goulash_portions}/{pot_capacity}).")
        print(f"{Fore.RED}{cook_name} has cooked full pot of goulash.")
        shared.full_pot.signal()


if __name__ == '__main__':
    main()
