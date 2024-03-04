"""This file is implementation of the third assignment of the PPDS."""

__author__ = "Richard Körösi"


from colorama import Fore, Style
from fei.ppds import Thread, Semaphore, print, Mutex

no_passengers = 13
train_capacity = 6


class Shared:
    """This class represents shared data."""

    def __init__(self):
        """Initialize shared data."""

        self.boarding_queue = Semaphore(0)
        self.boarding_barrier = Barrier(train_capacity)
        self.boarded = Semaphore(0)

        self.unboarding_queue = Semaphore(0)
        self.unboarding_barrier = Barrier(train_capacity)
        self.unboarded = Semaphore(0)


class Barrier:
    """This class represents barrier."""

    def __init__(self, n):
        """Initialize barrier data."""
        self.n = n
        self.counter = 0
        self.mutex = Mutex()
        self.barrier = Semaphore(0)

    def wait(self, signal_to_train):
        """Wait for all threads to reach the barrier and then signal them to continue.

        More specifically, this function simulates the basic
        behavior of the barrier, with one exception.
        It not only signals all threads in the barrier to continue,
        but also signals the train to finish loading/unloading passengers.

        Keyword arguments:
        signal_to_train -- semaphore to signal train to stop
        loading/unloading passengers
        """
        self.mutex.lock()
        self.counter += 1
        if self.counter == self.n:
            self.counter = 0
            self.barrier.signal(self.n)
            signal_to_train.signal()
        self.mutex.unlock()
        self.barrier.wait()


def main():
    """Create certain number of passengers threads and train thread and start them.

    More specifically, this example demonstrates the case in which
    passengers are boarding and unboarding the train in the infinite loop.
    """
    shared = Shared()
    all_threads = []
    for i in range(no_passengers):
        all_threads.append(Thread(passengers_loop, shared, f"Passenger({i})"))
    all_threads.append(Thread(train_loop, shared, "Train"))
    for i in all_threads:
        i.join()


def train_loop(shared, tid):
    """Simulate train's behavior in the infinite loop.

    More specifically, this function simulates the following behavior:
    - train starts loading passengers (signals passengers to board)
    - train waits for all passengers to board (to full capacity)
    - train starts running
    - train stops and starts unboarding passengers
    (signals passengers to unboard)
    - train waits for all passengers to unboard (to empty capacity)
    - after all passengers unboarded, train starts loading passengers again


    Keyword arguments:
    shared -- shared data
    tid -- thread identifier
    """
    while True:
        load(tid)
        shared.boarding_queue.signal(train_capacity)
        shared.boarded.wait()
        run(tid)
        unload(tid)
        shared.unboarding_queue.signal(train_capacity)
        shared.unboarded.wait()


def passengers_loop(shared, tid):
    """Simulate passenger's behavior in the infinite loop.

    More specifically, this function simulates the following behavior:
    - passengers start waiting for the train to start loading
    (signal from semaphore in train_loop)
    - passengers board the train (and wait for train to be full),
    last passenger signals the train to start moving (signal in barrier)
    - passengers wait for the train to stop and start unboarding
    (signal from semaphore in train_loop)
    - passengers unboard the train (and wait for each other),
    last passenger signals the train to start loading (signal in barrier)

    Keyword arguments:
    shared -- shared data
    tid -- thread identifier
    """
    while True:
        print(Fore.LIGHTWHITE_EX + f"{tid} is waiting in queue.")
        shared.boarding_queue.wait()
        board(tid)
        shared.boarding_barrier.wait(shared.boarded)
        shared.unboarding_queue.wait()
        unboard(tid)
        shared.unboarding_barrier.wait(shared.unboarded)


def board(passenger):
    """Print message about passenger boarding.

    Keyword arguments:
    passenger -- name of the passenger (thread identifier)
    """
    print(Fore.LIGHTBLUE_EX + f"{passenger} is boarding." + Style.RESET_ALL)


def unboard(passenger):
    """Print message about passenger unboarding.

    Keyword arguments:
    passenger -- name of the passenger (thread identifier)
    """
    print(Fore.LIGHTRED_EX + f"{passenger} is unboarding." + Style.RESET_ALL)


def load(train):
    """Print message about train loading passengers.

    Keyword arguments:
    train -- name of the train (thread identifier)
    """
    print(Fore.LIGHTMAGENTA_EX + f"{train} is loading passengers.")


def run(train):
    """Print message about running train.

    Keyword arguments:
    train -- name of the train (thread identifier)
    """
    print(Fore.LIGHTYELLOW_EX + f"{train} is running.")


def unload(train):
    """Print message about train unloading passengers.

    Keyword arguments:
    train -- name of the train (thread identifier)
    """
    print(Fore.LIGHTMAGENTA_EX + f"{train} is unloading passengers.")


if __name__ == '__main__':
    main()
