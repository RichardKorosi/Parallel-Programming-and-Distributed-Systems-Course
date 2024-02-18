from fei.ppds import Thread, Semaphore, print
from time import sleep


class Shared:
    def __init__(self):
        self.semaphore = Semaphore(0)


def main():
    shared = Shared()
    thread1 = Thread(routine_jano, shared, "Jano")
    thread2 = Thread(routine_fero, shared, "Fero")
    thread1.join()
    thread2.join()


def routine_jano(shared, tid):
    sleeping(tid)


def routine_fero(shared, tid):
    sleeping(tid)


def sleeping(tid):
    print(f"{tid} is sleeping.")
    sleep(1)
    print(f"{tid} is awake.")


if __name__ == '__main__':
    main()
