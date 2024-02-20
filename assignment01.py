"""This file is implementation of the first assignment of the PPDS."""

__author__ = "Richard Körösi"

from colorama import Fore
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


def highlighted_print(message, activity):
    """Print a highlighted message of a given activity.

    The color of the message is based on the type of activity.
    Cyan color represents sleeping activity.
    Blue color represents hygiene activity.
    Magenta color represents eating activity.
    Red color represents calling and receiving activities.

    Keyword arguments:
    message -- message to be printed
    activity -- name of the activity
    """
    if activity == "sleeping":
        print(Fore.CYAN + message)
    elif activity == "hygiene":
        print(Fore.BLUE + message)
    elif activity == "eating":
        print(Fore.MAGENTA + message)
    else:
        print(Fore.RED + message)


def routine_jano(shared, tid):
    """Execute the routine of thread Jano.

    Keyword arguments:
    shared -- shared data between threads
    tid -- thread identifier
    """
    sleeping(tid)
    hygiene(tid)
    eating(tid)
    calling(shared, tid)


def routine_fero(shared, tid):
    """Execute the routine of thread Fero.

    Keyword arguments:
    shared -- shared data between threads
    tid -- thread identifier
    """
    sleeping(tid)
    hygiene(tid)
    receiving(shared, tid)
    eating(tid)


def sleeping(tid):
    """Execute sleeping activity of the thread.

    This function prints a message that the thread is sleeping
    and then waits for a while before printing a message that the thread
    has woken up.

    Keyword arguments:
    tid -- thread identifier
    """
    highlighted_print(f"{tid} is sleeping.", "sleeping")
    sleep(1)
    highlighted_print(f"{tid} has woken up.", "sleeping")


def hygiene(tid):
    """Execute hygiene activity of the thread.

    This function prints a message that the thread is taking a shower
    and then waits for a while before printing a message that the thread
    has finished showering.

    Keyword arguments:
    tid -- thread identifier
    """
    highlighted_print(f"{tid} is taking a shower.", "hygiene")
    sleep(1)
    highlighted_print(f"{tid} has finished showering.", "hygiene")


def eating(tid):
    """Execute eating activity of the thread.

    This function prints a message that the thread is eating
    and then waits for a while before printing a message that the thread
    has eaten.

    Keyword arguments:
    tid -- thread identifier
    """
    highlighted_print(f"{tid} is eating.", "eating")
    sleep(1)
    highlighted_print(f"{tid} has eaten.", "eating")


def calling(shared, tid):
    """Execute calling activity of the thread.

    This function prints a message that the thread has called
    and then signals the semaphore. This allows the other thread
    (that is waiting in the receiving() function) to continue with its tasks.

    Keyword arguments:
    shared -- shared data between threads
    tid -- thread identifier
    """
    highlighted_print(f"{tid} is calling.", "calling")
    sleep(1)
    shared.semaphore.signal()


def receiving(shared, tid):
    """Execute receiving activity of the thread.

    This function makes the thread wait (assuming that semaphore
    was initialized with value 0 and has not received any signals yet)
    for the semaphore to be signaled (signal is in calling() function)
    and after receiving the signal it prints a message
    indicating that the thread has received a call.

    Keyword arguments:
    shared -- shared data between threads
    tid -- thread identifier
    """
    shared.semaphore.wait()
    highlighted_print(f"{tid} has received a call.", "receiving")
    sleep(1)


if __name__ == '__main__':
    main()
