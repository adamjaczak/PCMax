from core import find_pc_max, tabu_search_pcmax_parallel
from tools import make_file_logger, load_file

file = "m50n1000.txt"
filepath = f"instances/{file}"
filepath_to_log_file = f"instances/logs/{file}"
log_to_file = make_file_logger(filepath_to_log_file, also_print=True)


if __name__ == "__main__":
    
    
    log_to_file(f"=== Start testu: {filepath} ===")
    num_processors, num_tasks, tasks_times = load_file(filepath)

    _, lpt_loads = find_pc_max(
        tasks_times,
        num_processors,
        draw_chart=True,
        output_path="plots/LPT.png",
    )
    max_lpt = max(lpt_loads)
    print(f"PCMax z czystym LPT: {max_lpt}")

    pcmax, iters = tabu_search_pcmax_parallel(
        tasks_times,
        num_processors,
        time_limit=180,
        max_workers=4,
        base_seed=42,
        draw_chart=False,
        log_fn=log_to_file,
    )
    print(f"PCMax (wieloprocesowo) z tabu search: {pcmax} (iteracji łącznie: {iters})")