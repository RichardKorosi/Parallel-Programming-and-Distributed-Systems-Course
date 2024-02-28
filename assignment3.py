"""This file is implementation of the third assignment of the PPDS."""

__author__ = "Richard Körösi"


from colorama import Fore, Style
from fei.ppds import Thread, Semaphore, print, Mutex

no_passengers = 7
train_capacity = 4


class Shared:
    """This class represents shared data."""

    def __init__(self):
        """Initialize shared data."""
        self.mutex = Mutex()

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

    def wait(self, signal_to_train):
        self.mutex.lock()
        self.counter += 1
        if self.counter == self.n:
            self.counter = 0
            self.barrier.signal(self.n)
            signal_to_train.signal()
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


def train_loop(shared, tid):
    while True:
        load(tid)
        shared.boarding_queue.signal(train_capacity)
        shared.boarded.wait()
        run(tid)
        unload(tid)
        shared.unboarding_queue.signal(train_capacity)
        shared.unboarded.wait()


def passengers_loop(shared, tid):
    while True:
        shared.boarding_queue.wait()
        board(tid)
        shared.boarding_barrier.wait(shared.boarded)
        shared.unboarding_queue.wait()
        unboard(tid)
        shared.unboarding_barrier.wait(shared.unboarded)


def board(passenger):
    print(Fore.LIGHTBLUE_EX + f"{passenger} is boarding." + Style.RESET_ALL)


def unboard(passenger):
    print(Fore.LIGHTRED_EX + f"{passenger} is unboarding." + Style.RESET_ALL)


def load(train):
    print(Fore.LIGHTMAGENTA_EX + f"{train} is loading passengers.")


def run(train):
    print(Fore.LIGHTYELLOW_EX + f"{train} is running.")


def unload(train):
    print(Fore.LIGHTMAGENTA_EX + f"{train} is unloading passengers.")


if __name__ == '__main__':
    main()
