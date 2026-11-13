import heapq
import random
from plot import draw_gaant_pcmax, build_schedule_dictionary
import time
import math
from taboo.taboo import tabu_search

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


def find_pc_max(tasks: list, num_of_processors: int):
    tasks.sort(reverse=True)
    sorted_indices = sorted(range(len(tasks)), key=lambda i: tasks[i], reverse=True)
    processors = [(0, i) for i in range(num_of_processors)]
    heapq.heapify(processors)

    assignment = [0] * len(tasks)
    loads = [0] * num_of_processors

    for index in sorted_indices:
        min_time_processor, proc_id = heapq.heappop(processors)
        assignment[index] = proc_id
        loads[proc_id] += tasks[index]
        heapq.heappush(processors, (min_time_processor + tasks[index], proc_id))

    schedule = build_schedule_dictionary(tasks, assignment, len(processors))
    draw_gaant_pcmax(schedule, "plots/LPT.png")
    return assignment, loads


def tabu_search_pcmax(tasks: list, num_of_processors: int, time_limit: float = 175.0, tabu_tenure: int = 15, draw_chart: bool = True) -> int:
    start_time = time.time()

    n = len(tasks)

    if n == 0 or num_of_processors == 0:
        return 0
    if num_of_processors == 1:
        return sum(tasks)

    #current_assignment - index is the number of a task, value is the number of processor
    #current_loads - sum of all tasks that are now on each processor

    current_assignment, current_loads = find_pc_max(tasks, num_of_processors)

    best_assignment = list(current_assignment)
    best_cmax = max(current_loads)

    tabu_list = {}
    iteration = 0

    while time.time() - start_time < time_limit:
        iteration += 1
        current_cmax = max(current_loads)

        # Longest processing processor
        crit_proc = current_loads.index(current_cmax)

        best_move = None
        best_neighbor_cmax = float('inf')

        for task_index in range(n):
            if current_assignment[task_index] != crit_proc:
                continue

            task_time = tasks[task_index]
            for target_proc in range(num_of_processors):
                if target_proc == crit_proc:
                    continue

                new_loads = list(current_loads)
                new_loads[crit_proc] -= task_time
                new_loads[target_proc] += task_time
                new_cmax = max(new_loads)

                is_tabu = tabu_list.get((task_index, target_proc), 0) > iteration
                if is_tabu and new_cmax >= best_cmax:
                    continue

                if new_cmax < best_neighbor_cmax:
                    best_neighbor_cmax = new_cmax
                    best_move = (task_index, crit_proc, target_proc)
        if best_move is None:
            #break
            tabu_list.clear()
            continue

        task_index, from_proc, to_proc = best_move

        current_assignment[task_index] = to_proc
        current_loads[from_proc] -= tasks[task_index]
        current_loads[to_proc] += tasks[task_index]

        tabu_list[(task_index, from_proc)] = iteration + tabu_tenure

        if best_neighbor_cmax < best_cmax:
            best_cmax = best_neighbor_cmax
            best_assignment = list(current_assignment)

    if draw_chart:
        schedule = build_schedule_dictionary(tasks, best_assignment, num_of_processors)
        draw_gaant_pcmax(schedule, "plots/TABU.png", best_cmax)

    print(f"Found Cmax: {best_cmax}")
    
    return best_cmax
    


#generate_instance("instances/random_instance3.txt",3, 3, 10,10,1,50)

data = load_file("instances/m50n1000.txt");
num_of_processors = data[0]
num_of_tasks = data[1]
tasks_times = data[2]

pc_max_lpt, pc_max_lpt_loads = find_pc_max(tasks_times, num_of_processors)
max_lpt = max(pc_max_lpt_loads)

print(f"PCMax z czystym LPT: {max_lpt}")

pcmax = tabu_search_pcmax(tasks_times, num_of_processors, time_limit=180)
print(f"PC Max z tabu search (1): {pcmax}")

#best_sol, best_val = tabu_search(num_of_processors, tasks_times)

#print(f"PC Max z tabu search (2): {best_val}")


 #random_instance1 = 121
 #random_instance2 = 666

 # Ograniczenie: max 3 minuty na instancję (warunek stopu tylko na zaliczeniu i wpisie do rankingu)

#  m25.txt:
#  LPT: 3462
#  TABU (180s): 3462
# 
#  m25.txt:
#  LPT: 298
#  TABU (10s): 298
#
#  m10n200.txt:
#  LPT: 11024
#  TABU (180s):  11003
#   
#   m50n200.txt:
#   LPT: 992
#   TABU (180s): 992
#
#   m50n100.txt:
#   LPT: 9779
#   TABU(180s): 9777