import heapq

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

data = load_file("m30.txt");
num_of_processors = data[0]
num_of_tasks = data[1]
tasks_times = data[2]
tasks_times.sort(reverse=True)
processors = [0] * num_of_processors

for index, task in enumerate(tasks_times):
    min_time_processor = heapq.heappop(processors)
    heapq.heappush(processors, min_time_processor + task)

print(max(processors))


 