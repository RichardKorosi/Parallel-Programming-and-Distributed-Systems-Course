from typing import Callable

def consumer(func: Callable) -> Callable:
    def wrapper(*args, **kw):
        it = func(*args, **kw)
        next(it)
        return it

    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper


class Scheduler:
    def __init__(self):
        print("Scheduler is created")
        self.tasks = []

    def _add_job(self, it):
        self.tasks.append(it)

    def start(self):
        data_to_task = ("Hello, Python!", "Hello World!")
        while self.tasks:
            task = self.tasks.pop(0)
            try:
                task.send(data_to_task)
            except StopIteration:
                pass

@consumer
def task1(substring: str):
    print('Please talk to me!')
    try:
        while True:
            text = yield
            if substring in text:
                print(f'Oh no: I found a {substring} again!')
            else:
                print(f'NICE: I did not find a {substring}!')
    except GeneratorExit:
        print('Ok, ok: I am quitting.')



def main():
    scheduler = Scheduler()
    scheduler._add_job(task1('Python'))
    scheduler.start()

if __name__ == "__main__":
    main()