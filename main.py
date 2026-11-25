import heapq
import random
import time
from plot import draw_gaant_pcmax, build_schedule_dictionary


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


def find_pc_max(
    tasks: list[int],
    num_of_processors: int,
    draw_chart: bool = False,
    output_path: str = "plots/LPT.png",
) -> tuple[list[int], list[int]]:
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

    if draw_chart:
        schedule = build_schedule_dictionary(tasks, assignment, num_of_processors)
        draw_gaant_pcmax(schedule, output_path, max(loads))

    return assignment, loads


def _second_largest_except(loads: list[int], skip_idx: int) -> int:
    second = -1
    for idx, val in enumerate(loads):
        if idx == skip_idx:
            continue
        if val > second:
            second = val
    return max(0, second)


def tabu_search_pcmax(
    tasks: list[int],
    num_of_processors: int,
    time_limit: float = 175.0,
    tabu_tenure: int = 15,
    draw_chart: bool = True,
    seed: int | None = None,
) -> tuple[int, int]:
    rng = random.Random(seed)
    start_time = time.time()
    n = len(tasks)

    if n == 0 or num_of_processors <= 0:
        return 0, 0
    if num_of_processors == 1:
        total = sum(tasks)
        return total, 0

    current_assignment, current_loads = find_pc_max(tasks, num_of_processors, draw_chart=False)
    best_assignment = list(current_assignment)
    best_cmax = max(current_loads)

    tabu_until: dict[tuple[int, int], int] = {}
    iteration = 0

    while time.time() - start_time < time_limit:
        iteration += 1
        current_cmax = max(current_loads)

        crit_candidates = [i for i, load in enumerate(current_loads) if load == current_cmax]
        crit_proc = rng.choice(crit_candidates)
        second_max = _second_largest_except(current_loads, crit_proc)

        best_move = None
        best_neighbor_cmax = float("inf")

        crit_load_after_remove = current_loads[crit_proc]

        for task_index in range(n):
            if current_assignment[task_index] != crit_proc:
                continue

            task_time = tasks[task_index]
            rem_crit_load = crit_load_after_remove - task_time

            for target_proc in range(num_of_processors):
                if target_proc == crit_proc:
                    continue

                new_target_load = current_loads[target_proc] + task_time

                # Maksimum obciążenia po przeniesieniu task_index z crit_proc na target_proc
                new_cmax = rem_crit_load if rem_crit_load > second_max else second_max
                if new_target_load > new_cmax:
                    new_cmax = new_target_load

                is_tabu = tabu_until.get((task_index, target_proc), 0) > iteration
                if is_tabu and new_cmax >= best_cmax:
                    continue

                if new_cmax < best_neighbor_cmax:
                    best_neighbor_cmax = new_cmax
                    best_move = (task_index, crit_proc, target_proc)

        if best_move is None:
            tabu_until.clear()
            continue

        task_index, from_proc, to_proc = best_move
        current_assignment[task_index] = to_proc
        current_loads[from_proc] -= tasks[task_index]
        current_loads[to_proc] += tasks[task_index]

        # Zakaz powrotu tego zadania na poprzedni procesor przez tabu_tenure iteracji
        tabu_until[(task_index, from_proc)] = iteration + tabu_tenure

        if best_neighbor_cmax < best_cmax:
            best_cmax = best_neighbor_cmax
            best_assignment = list(current_assignment)

    if draw_chart:
        schedule = build_schedule_dictionary(tasks, best_assignment, num_of_processors)
        draw_gaant_pcmax(schedule, "plots/TABU.png", best_cmax)

    return best_cmax, iteration


if __name__ == "__main__":
    num_processors, num_tasks, tasks_times = load_file("instances/m50n1000.txt")

    _, lpt_loads = find_pc_max(
        tasks_times,
        num_processors,
        draw_chart=True,
        output_path="plots/LPT.png",
    )
    max_lpt = max(lpt_loads)
    print(f"PCMax z czystym LPT: {max_lpt}")

    pcmax, iters = tabu_search_pcmax(
        tasks_times,
        num_processors,
        time_limit=180,
        tabu_tenure=15,
        draw_chart=True,
        seed=42,
    )
    print(f"PCMax z tabu search: {pcmax} (iteracji: {iters})")