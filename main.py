import heapq
import random
from plot import draw_gaant_pcmax, build_schedule_dictionary
import time
import math

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
    return assignment, loads


def tabu_search_pcmax(tasks: list, num_of_processors: int, time_limit: float = 175.0, tabu_tenture: int = 15, draw_chart: bool = True) -> int:
    start_time = time.time()

    n = len(tasks)

    if n == 0 or num_of_processors == 0:
        return 0
    if num_of_processors == 1:
        return sum(tasks)

    # Najniższe możliwe rozwiązanie teoretyczne
    lowest_possible_outcome = max(max(tasks), math.ceil(sum(tasks) / num_of_processors))

    current_assignment, current_loads = find_pc_max(tasks, num_of_processors)
    best_assignment = list(current_assignment)
    best_cmax = max(current_loads)

    if best_cmax == lowest_possible_outcome:
        if draw_chart:
            schedule = build_schedule_dictionary(tasks, best_assignment, num_of_processors)
            draw_gaant_pcmax(schedule, "chart.png", best_cmax)
        return best_cmax

    tabu_list = {}
    iteration = 0
    no_improve_iterations = 0

    while time.time() - start_time < time_limit:
        iteration += 1
        current_cmax = max(current_loads)

        max_time_processor = current_loads.index(current_cmax)

        proc_tasks = [[] for _ in range(num_of_processors)]
        for t_index, p_id in enumerate(current_assignment):
            proc_tasks[p_id].append(t_index)

        best_move = None
        best_neighbour_cmax = float('inf')
        best_neighbour_sq_sum = float('inf')

        for t_index in proc_tasks[max_time_processor]:
            t_dur = tasks[t_index]
            for target_proc in range(num_of_processors):
                if target_proc == max_time_processor:
                    continue

                new_crit_load = current_loads[max_time_processor] - t_dur
                new_target_load = current_loads[target_proc] + t_dur

                if new_target_load > current_cmax and new_target_load >= best_neighbour_cmax:
                    continue

                other_max = max(
                    (load for p, load in enumerate(current_loads) if p != max_time_processor and p != target_proc), default=0
                )
                new_cmax = max(other_max, new_crit_load, new_target_load)

                is_tabu = tabu_list.get(('insert', t_index, target_proc), 0) > iteration

                if is_tabu and new_cmax >= best_cmax:
                    continue

                sq_sum = (
                    sum(l*l for p, l in enumerate(current_loads) if p != max_time_processor and p != target_proc) + new_crit_load ** 2 + new_target_load ** 2
                )

                if (new_cmax < best_neighbour_cmax) or (new_cmax == best_neighbour_cmax and sq_sum < best_neighbour_sq_sum):
                    best_neighbour_cmax = new_cmax
                    best_neighbour_sq_sum = sq_sum
                    best_move = ('insert', t_index, max_time_processor, target_proc)


        for t1 in proc_tasks[max_time_processor]:
            dur1 = tasks[t1]
            for other_proc in range(num_of_processors):
                if other_proc == max_time_processor:
                    continue
                for t2 in proc_tasks[other_proc]:
                    dur2 = tasks[t2]
                    if dur1 == dur2:
                        continue

                    new_crit_load = current_loads[max_time_processor] - dur1 + dur2
                    new_other_load = current_loads[other_proc] - dur2 + dur1

                    other_max = max(
                        (load for p, load in enumerate(current_loads) if p != max_time_processor and p != other_proc), default=0
                    )
                    new_cmax = max(other_max, new_crit_load, new_other_load)

                    move_key = ('swap', min(t1, t2), max(t1, t2))

                    is_tabu = tabu_list.get(move_key, 0) > iteration
                    if is_tabu and new_cmax >= best_cmax:
                        continue
                    sq_sum = (
                        sum(l*l for p, l in enumerate(current_loads) if p != max_time_processor and p != other_proc) + new_crit_load ** 2 + new_other_load ** 2
                    )
                    if (new_cmax < best_neighbour_cmax) or (new_cmax == best_neighbour_cmax and sq_sum < best_neighbour_sq_sum):
                        best_neighbour_cmax = new_cmax
                        best_neighbour_sq_sum = sq_sum
                        best_move = ('swap', t1, t2, max_time_processor, other_proc)

        if best_move is None:
            tabu_list.clear()
            t_rand = random.randrange(n)
            old_p = current_assignment[t_rand]
            new_p = random.randrange(num_of_processors)
            current_assignment[t_rand] = new_p
            current_loads[old_p] -= tasks[t_rand]
            current_loads[new_p] += tasks[t_rand]
            continue

        if best_move[0] == 'insert':
            _, t_idx, from_p, to_p = best_move
            current_assignment[t_idx] = to_p
            current_loads[from_p] -= tasks[t_idx]
            current_loads[to_p] += tasks[t_idx]

            tabu_list[('insert', t_idx, from_p)] = iteration + tabu_tenture + random.randint(0,5)
        elif best_move[0] == 'swap':
            _, t1, t2, p1, p2 = best_move
            current_assignment[t1] = p2
            current_assignment[t2] = p1
            current_loads[p1] = current_loads[p1] - tasks[t1] + tasks[t2]
            current_loads[p2] = current_loads[p2] - tasks[t2] + tasks[t1]
            move_key = ('swap', min(t1, t2), max(t1, t2))
            tabu_list[move_key] = iteration + tabu_tenture + random.randint(0,5)

        if best_neighbour_cmax < best_cmax:
            best_cmax = best_neighbour_cmax
            best_assignment = list(current_assignment)
            no_improve_iterations = 0

            if best_cmax == lowest_possible_outcome:
                break
        else:
            no_improve_iterations += 1

        if no_improve_iterations > 500:
            no_improve_iterations = 0
            tabu_list.clear()
            for _ in range(max(2, n // 20)):
                t_rand = random.randrange(n)
                old_p = current_assignment[t_rand]
                new_p = random.randrange(num_of_processors)
                current_assignment[t_rand] = new_p
                current_loads[old_p] -= tasks[t_rand]
                current_loads[new_p] += tasks[t_rand]

    if draw_chart:
        schedule = build_schedule_dictionary(tasks, best_assignment, num_of_processors)
        draw_gaant_pcmax(schedule, "chart2.png", best_cmax)

    return best_cmax


#generate_instance("random_instance2.txt",3, 3, 10,10,1,50)

data = load_file("random_instance2.txt");
num_of_processors = data[0]
num_of_tasks = data[1]
tasks_times = data[2]

pcmax = tabu_search_pcmax(tasks_times, num_of_processors, time_limit=60)
print(pcmax)


 #random_instance1 = 121
 #random_instance2 = 666

 # Ograniczenie: max 3 minuty na instancję (warunek stopu tylko na zaliczeniu i wpisie do rankingu)