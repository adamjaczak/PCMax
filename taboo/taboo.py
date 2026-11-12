import random

def load_file(path: str):
    with open(path, 'r', encoding='utf-8') as file:
        num_of_processors = int(file.readline().strip())
        num_of_tasks = int(file.readline().strip())
        tasks_times = [int(line.strip()) for line in file if line.strip().isdigit()]
    return num_of_processors, num_of_tasks, tasks_times

def calculate_makespan(solution, tasks_times, num_of_processors):
    processor_loads = [0] * num_of_processors
    for task_idx, proc_idx in enumerate(solution):
        processor_loads[proc_idx] += tasks_times[task_idx]
    return max(processor_loads)

def tabu_search(num_of_processors, tasks_times, max_iterations=300, tabu_tenure=15):
    num_of_tasks = len(tasks_times)
    
    current_solution = [random.randint(0, num_of_processors - 1) for _ in range(num_of_tasks)]
    best_solution = list(current_solution)
    
    best_makespan = calculate_makespan(best_solution, tasks_times, num_of_processors)
    current_makespan = best_makespan
    
    tabu_list = {}
    
    for iteration in range(max_iterations):
        best_neighbor = None
        best_neighbor_makespan = float('inf')
        best_move = None
        
        for task_idx in range(num_of_tasks):
            current_proc = current_solution[task_idx]
            for target_proc in range(num_of_processors):
                if target_proc == current_proc:
                    continue
                
                move = (task_idx, target_proc)
                is_tabu = move in tabu_list and tabu_list[move] > iteration
                
                current_solution[task_idx] = target_proc
                neighbor_makespan = calculate_makespan(current_solution, tasks_times, num_of_processors)
                current_solution[task_idx] = current_proc
                
                if (not is_tabu or neighbor_makespan < best_makespan) and neighbor_makespan < best_neighbor_makespan:
                    best_neighbor_makespan = neighbor_makespan
                    best_neighbor = target_proc
                    best_move = (task_idx, target_proc)
        
        if not best_move:
            break
            
        task_to_move, new_proc = best_move
        current_solution[task_to_move] = new_proc
        current_makespan = best_neighbor_makespan
        
        tabu_list[best_move] = iteration + tabu_tenure
        
        if current_makespan < best_makespan:
            best_solution = list(current_solution)
            best_makespan = current_makespan
            
    return best_solution, best_makespan

if __name__ == "__main__":
    file_path = "m30.txt"
    try:
        procs, tasks_cnt, times = load_file(file_path)
        print(f"Wczytano: {procs} procesorów, {tasks_cnt} zadań.")
        
        best_sol, best_val = tabu_search(procs, times, max_iterations=400, tabu_tenure=20)
        
        print(f"Najlepszy znaleziony makespan (Tabu Search): {best_val}")
        print(f"Przydział zadań do procesorów: {best_sol}")
    except FileNotFoundError:
        print(f"Nie znaleziono pliku {file_path}.")