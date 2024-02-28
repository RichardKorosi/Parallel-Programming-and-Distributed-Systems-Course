"""This file is implementation of the third assignment of the PPDS."""

__author__ = "Richard Körösi"

from colorama import Fore, Style
from fei.ppds import Thread, Semaphore, print, Mutex
from time import sleep

no_passengers = 50
train_capacity = 30


class Shared:
    """This class represents shared data."""

    def __init__(self):
        """Initialize shared data."""
        self.mutex = Mutex()
        self.passengers_in_train = 0

        self.boarding_queue = Semaphore(0)
        self.boarded = Semaphore(0)

        self.unboarding_queue = Semaphore(0)
        self.unboarded = Semaphore(0)


def main():
    shared = Shared()
    all_threads = []
    for i in range(no_passengers):
        all_threads.append(Thread(passengers_loop, shared, f"Passenger({i})"))
    all_threads.append(Thread(train_loop, shared, "Train"))
    for i in all_threads:
        i.join()


def train_loop(shared):
    load_train()
    shared.boarding_queue.signal()


def boarding():
    pass


def unboarding():
    pass


def load_train():
    pass


def unload_train():
    pass


def passengers_loop():
    pass


def board_barrier(shared):
    shared.mutex.lock()
    shared.passengers_in_train += 1
    if shared.passengers_in_train == no_passengers:
        shared.passengers_in_train = 0
        shared.boarding_queue.signal(no_passengers)
    shared.mutex.unlock()
    shared.boarding_queue.wait()


def unboard_barrier(shared):
    shared.mutex.lock()
    shared.passengers_in_train -= 1
    if shared.passengers_in_train == 0:
        shared.passengers_in_train = 0
        shared.unboarding_queue.signal(no_passengers)
    shared.mutex.unlock()
    shared.unboarding_queue.wait()


if __name__ == '__main__':
    main()
