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
        self.boarding_barrier = Barrier(train_capacity)
        self.boarded = Semaphore(0)

        self.unboarding_queue = Semaphore(0)
        self.unboarding_barrier = Barrier(train_capacity)
        self.unboarded = Semaphore(0)


class Barrier:
    def __init__(self, n):
        self.n = n
        self.counter = 0
        self.mutex = Mutex()
        self.barrier = Semaphore(0)

    def wait(self):
        self.mutex.lock()
        self.counter += 1
        if self.counter == train_capacity:
            self.counter = 0
            self.barrier.signal(self.n)
        self.mutex.unlock()
        self.barrier.wait()


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


if __name__ == '__main__':
    main()
