from core import find_pc_max,tabu_search_pcmax
from tools import make_file_logger, load_file


filepath = "instances/m50n1000.txt"
log_to_file = make_file_logger(f"{filepath}_logs.txt", also_print=True)


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

    pcmax, iters = tabu_search_pcmax(
        tasks_times,
        num_processors,
        log_fn=log_to_file,
        time_limit=30,
        tabu_tenure=15,
        draw_chart=True,
        seed=42,
    )
    print(f"PCMax z tabu search: {pcmax} (iteracji: {iters})")