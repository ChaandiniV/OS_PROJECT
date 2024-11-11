import matplotlib.pyplot as plt
import random

# Process class to store details of each process
class Process:
    def _init_(self, pid, burst_time, priority=0, io_wait=0):
        self.pid = pid
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.io_wait = io_wait  # Simulating I/O wait time
        self.finished = False
        self.start_time = None
        self.end_time = None

# Multilevel Feedback Queue Scheduling
def mlfq_scheduler(processes, quantum):
    queues = [[] for _ in range(3)]
    for process in processes:
        queues[0].append(process)

    time = 0
    schedule = []
    cpu_time = 0
    io_time = 0

    while any(process.remaining_time > 0 for process in processes):
        for i, queue in enumerate(queues):
            for process in queue:
                if process.remaining_time > 0:
                    if process.start_time is None:
                        process.start_time = time

                    exec_time = min(process.remaining_time, quantum)
                    start_time = time
                    process.remaining_time -= exec_time
                    time += exec_time
                    end_time = time
                    schedule.append((process.pid, start_time, end_time, "CPU"))
                    cpu_time += exec_time

                    # Simulate I/O wait time after CPU burst
                    io_start = time
                    io_end = io_start + process.io_wait
                    time += process.io_wait
                    schedule.append((process.pid, io_start, io_end, "I/O"))
                    io_time += process.io_wait

                    if process.remaining_time > 0 and i < len(queues) - 1:
                        queues[i + 1].append(process)
                    process.finished = process.remaining_time == 0
                    if process.finished:
                        queue.remove(process)
                        process.end_time = time
    return schedule, cpu_time, io_time, processes

# Lottery Scheduling
def lottery_scheduler(processes, total_tickets=100):
    schedule = []
    time = 0
    cpu_time = 0
    io_time = 0
    ticket_distribution = {p.pid: random.randint(1, total_tickets) for p in processes}

    while any(p.remaining_time > 0 for p in processes):
        total_weight = sum(ticket_distribution[p.pid] for p in processes if p.remaining_time > 0)
        winner_ticket = random.randint(1, total_weight)
        cumulative = 0
        winner_process = None
        for p in processes:
            if p.remaining_time > 0:
                cumulative += ticket_distribution[p.pid]
                if cumulative >= winner_ticket:
                    winner_process = p
                    break
        if winner_process:
            if winner_process.start_time is None:
                winner_process.start_time = time

            start_time = time
            exec_time = min(winner_process.remaining_time, 1)
            winner_process.remaining_time -= exec_time
            time += exec_time
            end_time = time
            schedule.append((winner_process.pid, start_time, end_time, "CPU"))
            cpu_time += exec_time

            # Simulate I/O wait time after CPU burst
            io_start = time
            io_end = io_start + winner_process.io_wait
            time += winner_process.io_wait
            schedule.append((winner_process.pid, io_start, io_end, "I/O"))
            io_time += winner_process.io_wait

            if winner_process.remaining_time == 0:
                winner_process.end_time = time
    return schedule, cpu_time, io_time, processes

# Calculate CPU Utilization, I/O Utilization, and Average Turnaround Time
def calculate_metrics(processes, total_time, cpu_time, io_time):
    cpu_utilization = (cpu_time / total_time) * 100
    io_utilization = (io_time / total_time) * 100
    turnaround_times = [p.end_time - p.start_time for p in processes if p.end_time is not None]
    avg_turnaround_time = sum(turnaround_times) / len(turnaround_times)
    return cpu_utilization, io_utilization, avg_turnaround_time

# Gantt Chart Visualization
def gantt_chart(schedule, title="Gantt Chart"):
    fig, ax = plt.subplots(figsize=(12, 6))
    colors = {"CPU": "tab:blue", "I/O": "tab:orange"}

    for pid, start, end, res_type in schedule:
        ax.barh(pid, end - start, left=start, color=colors[res_type], edgecolor='black', label=res_type if res_type not in ax.get_legend_handles_labels()[1] else "")
        ax.text(start + (end - start) / 2, pid, f"P{pid}", ha='center', va='center', color='white')

    ax.set_xlabel("Time")
    ax.set_ylabel("Process ID")
    ax.set_title(title)
    ax.legend()
    ax.grid(True)
    plt.show()

# Bar Chart for Metrics Comparison
def plot_metrics(mlfq_metrics, lottery_metrics):
    labels = ['CPU Utilization (%)', 'I/O Utilization (%)', 'Avg Turnaround Time']
    mlfq_values = mlfq_metrics
    lottery_values = lottery_metrics

    x = range(len(labels))
    width = 0.35

    fig, ax = plt.subplots()
    ax.bar(x, mlfq_values, width, label='MLFQ')
    ax.bar([i + width for i in x], lottery_values, width, label='Lottery')

    ax.set_ylabel("Metrics")
    ax.set_title("Scheduling Algorithm Comparison")
    ax.set_xticks([i + width / 2 for i in x])
    ax.set_xticklabels(labels)
    ax.legend()
    plt.show()

# Example usage
if _name_ == "_main_":
    # Sample processes with random burst and I/O wait times for demonstration
    processes = [Process(pid=i, burst_time=random.randint(5, 15), io_wait=random.randint(1, 3)) for i in range(15)]

    # Run MLFQ Scheduling
    mlfq_schedule, mlfq_cpu, mlfq_io, mlfq_processes = mlfq_scheduler(processes, quantum=4)
    total_time_mlfq = mlfq_schedule[-1][2]  # Last end time in schedule
    mlfq_metrics = calculate_metrics(mlfq_processes, total_time_mlfq, mlfq_cpu, mlfq_io)
    gantt_chart(mlfq_schedule, "MLFQ Scheduling Gantt Chart")

    # Reset processes for a fresh start
    for process in processes:
        process.remaining_time = process.burst_time
        process.start_time = None
        process.end_time = None

    # Run Lottery Scheduling
    lottery_schedule, lottery_cpu, lottery_io, lottery_processes = lottery_scheduler(processes)
    total_time_lottery = lottery_schedule[-1][2]  # Last end time in schedule
    lottery_metrics = calculate_metrics(lottery_processes, total_time_lottery, lottery_cpu, lottery_io)
    gantt_chart(lottery_schedule, "Lottery Scheduling Gantt Chart")

    # Plot Metrics Comparison
    plot_metrics(mlfq_metrics, lottery_metrics)
