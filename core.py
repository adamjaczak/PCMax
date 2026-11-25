import heapq
import random
import time
from plot import draw_gaant_pcmax, build_schedule_dictionary
import math

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

def _max_except_two(loads: list[int], index_a: int, index_b: int) -> int:
    best = 0
    for index, value in enumerate(loads):
        if index == index_a or index == index_b:
            continue
        if value > best:
            best = value

    return best

def tabu_search_pcmax(
    tasks: list[int],
    num_of_processors: int,
    log_fn,
    time_limit: float = 175.0,
    tabu_tenure: int = 15,
    max_swap_tasks_per_proc: int =15,
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

    lb = max(max(tasks), math.ceil(sum(tasks)/ num_of_processors))
    best_time = 0.0

    tabu_until: dict[tuple[int, int], int] = {}
    iteration = 0

    while time.time() - start_time < time_limit:
        iteration += 1
        current_cmax = max(current_loads)

        crit_candidates = [i for i, load in enumerate(current_loads) if load == current_cmax]
        crit_proc = rng.choice(crit_candidates)
        second_max = _second_largest_except(current_loads, crit_proc)

        best_relocate = None
        best_relocate_cmax = float("inf")

        crit_load_after_remove = current_loads[crit_proc]

        # Pętla relocate

        for task_index in range(n):
            if current_assignment[task_index] != crit_proc:
                continue

            task_time = tasks[task_index]
            rem_crit_load = crit_load_after_remove - task_time

            for target_proc in range(num_of_processors):
                if target_proc == crit_proc:
                    continue

                new_target_load = current_loads[target_proc] + task_time
                others_top = _max_except_two(current_loads, crit_proc, target_proc)
                new_cmax = max(others_top, rem_crit_load, new_target_load)

                is_tabu = tabu_until.get((task_index, target_proc), 0) > iteration
                if is_tabu and new_cmax >= best_cmax:
                    continue

                if new_cmax < best_relocate_cmax:
                    best_relocate_cmax = new_cmax
                    best_relocate = (task_index, crit_proc, target_proc)

        # Szukanie best swap

        proc_tasks: list[list[int]] = [[] for _ in range(num_of_processors)]
        for index, p in enumerate(current_assignment):
            proc_tasks[p].append(index)

        src_candidates = proc_tasks[crit_proc]
        if len(src_candidates) > max_swap_tasks_per_proc:
            src_candidates = rng.sample(src_candidates, max_swap_tasks_per_proc)

        best_swap = None
        best_swap_cmax = float("inf")
        crit_load = current_loads[crit_proc]

        for dst_proc in range(num_of_processors):
            if dst_proc == crit_proc:
                continue
            dst_candidates = proc_tasks[dst_proc]
            if not dst_candidates:
                continue
            if len(dst_candidates) > max_swap_tasks_per_proc:
                dst_candidates = rng.sample(dst_candidates, max_swap_tasks_per_proc)

            others_top = _max_except_two(current_loads, crit_proc, dst_proc)
            dst_load = current_loads[dst_proc]

            for t_src in src_candidates:
                time_src = tasks[t_src]
                for t_dst in dst_candidates:
                    time_dst = tasks[t_dst]
                    if time_src <= time_dst:
                        continue

                    new_crit = crit_load - time_src + time_dst
                    new_dst = dst_load - time_dst + time_src
                    new_cmax = max(others_top, new_crit, new_dst)

                    tabu_1 = tabu_until.get((t_src, dst_proc), 0) > iteration
                    tabu_2 = tabu_until.get((t_dst, crit_proc), 0) > iteration
                    if(tabu_1 or tabu_2) and new_cmax >= best_cmax:
                        continue

                    if new_cmax < best_swap_cmax:
                        best_swap_cmax = new_cmax
                        best_swap = (t_src, t_dst, crit_proc, dst_proc)

        use_swap = best_swap is not None and best_swap_cmax <= best_relocate_cmax
        chosen_cmax = best_swap_cmax if use_swap else best_relocate_cmax

        if chosen_cmax == float("inf"):
            tabu_until.clear()
            continue

        if use_swap:
            t_src, t_dst, src_proc, dst_proc = best_swap
            time_src = tasks[t_src]
            time_dst = tasks[t_dst]

            current_assignment[t_src] = dst_proc
            current_assignment[t_dst] = src_proc
            current_loads[src_proc] = current_loads[src_proc] - time_src + time_dst
            current_loads[dst_proc] = current_loads[dst_proc] - time_dst + time_src

            tabu_until[(t_src, src_proc)] = iteration + tabu_tenure
            tabu_until[(t_dst, dst_proc)] = iteration + tabu_tenure
        else:
            task_index, from_proc, to_proc = best_relocate
            task_time = tasks[task_index]

            current_assignment[task_index] = to_proc
            current_loads[from_proc] -= task_time
            current_loads[to_proc] += task_time

            tabu_until[(task_index, from_proc)] = iteration + tabu_tenure

        if chosen_cmax < best_cmax:
            best_cmax = chosen_cmax
            best_assignment = list(current_assignment)
            best_time = round(time.time() - start_time, 2)
            log_fn(f"t={best_time}s | iter={iteration} | new_best={best_cmax} (LB={lb})")

    if draw_chart:
        schedule = build_schedule_dictionary(tasks, best_assignment, num_of_processors)
        draw_gaant_pcmax(schedule, "plots/TABU.png", best_cmax)

    elapsed = max(time.time() - start_time, 1e-6)
    iter_per_sec = iteration / elapsed
    log_fn(
        f"[TABU] best={best_cmax} | LB={lb} \n best_at={best_time}s | iters={iteration} ({iter_per_sec:.1f} iter/s)"
    )
    return best_cmax, iteration