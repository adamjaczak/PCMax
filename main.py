import heapq
import random
from plot import draw_gaant_pcmax

num_of_processors = 0
num_of_tasks = 0
tasks_times = []

def load_file(path: str) -> list:
    try:
        with open(path, 'r') as file:
            num_of_processors = int(file.readline())
            num_of_tasks = int(file.readline())
            tasks_times = [int(line.strip()) for line in file.readlines()]
    except FileNotFoundError:
        print("Nie znaleziono pliku.")

    # zwraca wartość w formie listy [liczba procesorów, liczba zadań, [proces_1, proces_2, ...., proces_n]]
    return [num_of_processors, num_of_tasks, tasks_times]

def generate_instance(filepath="random_instance.txt", min_processors=2, max_processors=50, min_tasks=10, max_tasks=200, min_time=1, max_time=100):
    num_processors = random.randint(min_processors, max_processors)
    num_tasks = random.randint(min_tasks, max_tasks)
    with open(filepath, 'w') as file:
        file.write(f"{num_processors}\n")
        file.write(f"{num_tasks}\n")

        for _ in range(num_tasks):
            task_time = random.randint(min_time, max_time)
            file.write(f"{task_time}\n")


def find_pc_max(tasks: list, num_of_processors: int, draw_chart: bool = True) -> int:
    tasks.sort(reverse=True)
    processors = [(0, i) for i in range(num_of_processors)]
    heapq.heapify(processors)

    schedule = {f"P{i}": [] for i in range(num_of_processors)}

    for index, task in enumerate(tasks):
        min_time_processor, proc_id = heapq.heappop(processors)
        schedule[f"P{proc_id}"].append((index + 1, min_time_processor, task))
        heapq.heappush(processors, (min_time_processor + task, proc_id))

    pcmax = max(time for time, _ in processors)

    if draw_chart:
        draw_gaant_pcmax(schedule,"chart.png",pcmax)

    return pcmax


generate_instance("random_instance2.txt",3, 3, 10,10,1,50)

data = load_file("random_instance2.txt");
num_of_processors = data[0]
num_of_tasks = data[1]
tasks_times = data[2]

pcmax = find_pc_max(tasks_times, num_of_processors)
print(pcmax)


 #random_instance1 = 121
 #random_instance2 = 666

 # Ograniczenie: max 3 minuty na instancję (warunek stopu tylko na zaliczeniu i wpisie do rankingu)