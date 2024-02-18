"""This file is implementation of the first assignment of the PPDS."""

__author__ = "Richard Körösi"

from fei.ppds import Thread, Semaphore, print
from time import sleep


class Shared:
    """This class represents shared data."""

    def __init__(self):
        """Initialize shared data."""
        self.semaphore = Semaphore(0)


def main():
    """Create two threads and start them.

    More specifically, this example demonstrates the case in which
    one thread has to wait for another thread to finish its
    tasks before it can continue with its own tasks.
    """
    shared = Shared()
    thread1 = Thread(routine_jano, shared, "Jano")
    thread2 = Thread(routine_fero, shared, "Fero")
    thread1.join()
    thread2.join()


def routine_jano(shared, tid):
    """Execute the routine of thread Jano.

    Keyword arguments:
    shared -- shared data between threads
    tid -- thread identifier
    """
    sleeping(tid)
    hygiene(tid)
    eating(tid)
#   CALL


def routine_fero(shared, tid):
    """Execute the routine of thread Fero.

    Keyword arguments:
    shared -- shared data between threads
    tid -- thread identifier
    """
    sleeping(tid)
    hygiene(tid)
#   RECEIVE
    eating(tid)


def sleeping(tid):
    """Execute sleeping activity of the thread.

    This function prints a message that the thread is sleeping
    and then waits for a while before printing a message that the thread
    is awake.

    Keyword arguments:
    tid -- thread identifier
    """
    print(f"{tid} is sleeping.")
    sleep(1)
    print(f"{tid} is awake.")


def hygiene(tid):
    """Execute hygiene activity of the thread.

    This function prints a message that the thread is taking a shower
    and then waits for a while before printing a message that the thread
    is clean.

    Keyword arguments:
    tid -- thread identifier
    """
    print(f"{tid} is taking a shower.")
    sleep(1)
    print(f"{tid} is clean.")


def eating(tid):
    """Execute eating activity of the thread.

    This function prints a message that the thread is eating
    and then waits for a while before printing a message that the thread
    has eaten.

    Keyword arguments:
    tid -- thread identifier
    """
    print(f"{tid} is eating.")
    sleep(1)
    print(f"{tid} has eaten.")


if __name__ == '__main__':
    main()
