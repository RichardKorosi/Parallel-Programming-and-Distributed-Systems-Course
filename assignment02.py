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
    """Create certain number of savages threads and cook thread and start them.

    More specifically, this example demonstrates the case in which
    one group of threads (savages) are always eating together and
    wait for each-other every day, when pot is empty savages wait
    for the cook to cook until the pot is full.
    """
    shared = Shared()
    all_threads = []
    for i in range(savages):
        all_threads.append(Thread(daily_eating, shared, f"Savage({i})"))
    all_threads.append(Thread(cook_goulash, shared, "Cook"))
    for i in all_threads:
        i.join()


def daily_eating(shared, savage_name):
    """Execute the daily eating routine of the savages threads.

    More specifically, this function represents two barriers that
    synchronize the savages, activity of savages taking goulash
    from the pot (there can only be one savage at the pot at a same time)
    and eating (eating is concurrent).

    Keyword arguments:
    shared -- shared data between threads
    savage_name -- name of the thread (thread identifier)
    """
    while True:
        waiting_room_barrier(shared, savage_name)
        sleep(0.5)
        dinner_table_barrier(shared, savage_name)
        savage_getting_goulash(shared, savage_name)
        savage_eating(savage_name)


def waiting_room_barrier(shared, savage_name):
    """Synchronize savages before eating using barrier.

    More specifically, this function represents a barrier that synchronize
    the savages before eating. Last savage that arrives to the barrier signals
    the barrier and all savages can continue. The last savage also resets
    the barrier for the next day (iteration in the loop).

    Keyword arguments:
    shared -- shared data between threads
    savage_name -- name of the thread (thread identifier)
    """
    shared.mutex.lock()
    shared.waiting_savages += 1
    print(f"{Fore.LIGHTMAGENTA_EX}{savage_name} is waiting for others. "
          f"({shared.waiting_savages}/{savages})")
    if shared.waiting_savages == savages:
        shared.waiting_savages = 0
        shared.waiting_room.signal(savages)
    shared.mutex.unlock()
    shared.waiting_room.wait()


def dinner_table_barrier(shared, savage_name):
    """Prevent savage from eating twice in a day, sync savages in second barrier.

    More specifically, this function represents a barrier that prevents
    savage finish whole routine before all savages even arrive
    to the dinner table. That would mean that savage could eat twice a day
    and some savages would not eat at all. Savages sync here after the last
    savage "closes" the waiting room barrier. Last savage that arrives
    to the barrier signals the barrier and all savages can continue.
    The last savage also resets the barrier for the next day
    (iteration in the loop).

    Keyword arguments:
    shared -- shared data between threads
    savage_name -- name of the thread (thread identifier)
    """
    shared.mutex.lock()
    shared.waiting_savages += 1
    if shared.waiting_savages == savages:
        shared.waiting_savages = 0
        print(f"{Fore.YELLOW}{savage_name}: We are all here, let's eat!")
        shared.dinner_table.signal(savages)
    shared.mutex.unlock()
    shared.dinner_table.wait()


def savage_getting_goulash(shared, savage_name):
    """Lock the pot and take one portion, if the pot is empty signal the cook.

    More specifically, this function represents the activity of savages taking
    goulash from the pot (there can only be one savage at the pot at a same
    time). Savage locks the pot and looks if there is any goulash in the pot.
    If the pot is empty, savage signals the cook to cook and waits for the pot
    to be full. If the pot is not empty, savage takes one portion of goulash
    and goes to eat (and of unlocks the pot).

    Keyword arguments:
    shared -- shared data between threads
    savage_name -- name of the thread (thread identifier)
    """
    shared.mutex.lock()
    print(f"{Fore.GREEN}{savage_name}: I can see {shared.goulash_portions} "
          f"portion(s) in the pot.")
    if shared.goulash_portions == 0:
        print(f"{Fore.RED}{savage_name} is telling the cook to cook.")
        shared.empty_pot.signal()
        shared.full_pot.wait()
    print(f"{Fore.GREEN}{savage_name} has taken 1 portion.")
    shared.goulash_portions -= 1
    shared.mutex.unlock()


def savage_eating(savage_name):
    """Simulate the activity of eating.

    More specifically, this function represents the activity of eating.
    This function is executed concurrently by savages.

    Keyword arguments:
    savage_name -- name of the thread (thread identifier)
    """
    print(f"{Fore.LIGHTBLUE_EX}{savage_name} is eating." + Style.RESET_ALL)


def cook_goulash(shared, cook_name):
    """Simulate the cook activity.

    More specifically, this function represents the activity of the cook.
    Cook waits for the signal from the savages that the pot is empty
    and then cooks the goulash until the pot is full. After that, cook signals
    the savage that came to the pot to take the goulash portion and
    then waits for the another signal from the savages that the pot is empty.

    Keyword arguments:
    shared -- shared data between threads
    cook_name -- name of the thread (thread identifier)
    """
    while True:
        shared.empty_pot.wait()
        while shared.goulash_portions < pot_capacity:
            shared.goulash_portions += 1
            print(f"{Fore.LIGHTCYAN_EX}{cook_name} is cooking."
                  f"({shared.goulash_portions}/{pot_capacity}).")
        print(f"{Fore.RED}{cook_name} has cooked full pot of goulash.")
        shared.full_pot.signal()


if __name__ == '__main__':
    main()
