import random
from datetime import datetime

def make_file_logger(filepath: str, also_print: bool = True):
    def logger(message: str) -> None:
        stamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{stamp}] {message}"
        if also_print:
            print(line)
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    return logger

def load_file(path: str) -> tuple[int, int, list[int]]:
    with open(path, "r") as file:
        num_of_processors = int(file.readline())
        num_of_tasks = int(file.readline())
        tasks_times = [int(line.strip()) for line in file if line.strip()]
    return num_of_processors, num_of_tasks, tasks_times


def generate_instance(
    filepath: str = "random_instance.txt",
    min_processors: int = 2,
    max_processors: int = 50,
    min_tasks: int = 10,
    max_tasks: int = 200,
    min_time: int = 1,
    max_time: int = 100,
) -> None:
    num_processors = random.randint(min_processors, max_processors)
    num_tasks = random.randint(min_tasks, max_tasks)
    with open(filepath, "w") as file:
        file.write(f"{num_processors}\n")
        file.write(f"{num_tasks}\n")
        for _ in range(num_tasks):
            file.write(f"{random.randint(min_time, max_time)}\n")
