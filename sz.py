import time
import math
import warnings
import string

import numpy as np
import matplotlib.pyplot as plt

from mpi4py import MPI
from numba import cuda, core
from numba.core.errors import NumbaPerformanceWarning

warnings.filterwarnings("ignore", category=NumbaPerformanceWarning)

MASTER = 0
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
nproc = comm.Get_size()


@cuda.jit
def cuda_kernel(dp, col_string, row_string, start_col, start_row, elements_for_thread):
    pos = cuda.grid(1)
    col = start_col - pos * elements_for_thread
    row = start_row + pos * elements_for_thread
    for i in range(elements_for_thread):
        if col < 1 or row > len(dp[0]):
            break
        if col_string[col - 1] == row_string[row - 1] and col_string[col - 1] != 42:
            dp[col, row] = dp[col - 1, row - 1] + 1
        else:
            dp[col, row] = max(dp[col - 1, row], dp[col, row - 1])
        col -= 1
        row += 1


def main():
    source1 = ["**textje********skoro***citatelny******unich" * i for i in [1, 10]]
    source2 = ["text*v*tejtoknihe****ma*po***usc*****koniec**robot*rozum" * i for i in [1, 10]]
    source3 = ["f*te**xt**sa*je***sko*rio**tu*" * i for i in [1, 10]]

    experiment_parallel = []
    experiment_sequence = []

    for x in range(len(source1)):
        list_of_jobs = [(source1[x], source2[x]),
                        (source1[x], source3[x]),
                        (source2[x], source3[x])]

        if rank == MASTER:
            times = []

        for i in range(1 + 1):
            if rank == MASTER:
                time_start = time.perf_counter()
            parallel_experiment(list_of_jobs)
            if rank == MASTER:
                times.append(time.perf_counter() - time_start)

        if rank == MASTER:
            avg_time = sum(times[1:]) / (len(times) - 1)
            print(avg_time)
            dimensions = f"{len(source1[x])}x{len(source2[x])}x{len(source3[x])}"
            experiment_parallel.append({"dimensions": dimensions, "time": avg_time})

        if rank == MASTER:
            times = []
            for i in range(1 + 1):
                time_start = time.perf_counter()
                sequence_experiment(list_of_jobs)
                times.append(time.perf_counter() - time_start)

            avg_time = sum(times[1:]) / (len(times) - 1)
            print(avg_time)
            dimensions = f"{len(source1[x])}x{len(source2[x])}x{len(source3[x])}"
            experiment_sequence.append({"dimensions": dimensions, "time": avg_time})

    if rank == MASTER:
        create_graph(experiment_parallel, experiment_sequence)


def cuda_lcs(s1, s2):
    col_string = s1 if len(s1) < len(s2) else s2
    row_string = s2 if len(s1) < len(s2) else s1
    cuda_cores = 7168

    col_string = list(col_string.encode('utf-8'))
    row_string = list(row_string.encode('utf-8'))
    dp = np.zeros((len(col_string) + 1, len(row_string) + 1), dtype=np.int32)

    dp_cuda = cuda.to_device(dp)
    col_string_cuda = cuda.to_device(col_string)
    row_string_cuda = cuda.to_device(row_string)

    no_anti_diagonal = len(col_string) + len(row_string) - 1

    threads_per_block = 256
    blocks_per_grid = math.floor(cuda_cores / (threads_per_block * 3))
    elements_for_thread = 20
    # print("CUDA Cores available for one MPI process:", threads_per_block * blocks_per_grid)

    for i in range(1, no_anti_diagonal + 1):
        col = min(i, len(col_string))
        row = i - col + 1

        (cuda_kernel[blocks_per_grid, threads_per_block]
         (dp_cuda, col_string_cuda, row_string_cuda, col, row, elements_for_thread))

    dp_result = dp_cuda.copy_to_host()
    col_string = bytes(col_string).decode('utf-8')
    row_string = bytes(row_string).decode('utf-8')

    result = get_result(dp_result, col_string, row_string)
    return result


def get_result(dp, row_string, col_string):
    row = len(row_string)
    col = len(col_string)
    result = ""
    while row > 0 and col > 0:
        if dp[row, col - 1] > dp[row - 1, col]:
            col -= 1

        elif dp[row, col - 1] < dp[row - 1, col]:
            row -= 1

        elif dp[row, col - 1] == dp[row - 1, col]:
            if dp[row, col] == dp[row - 1, col]:
                row -= 1
            else:
                result = row_string[row - 1] + result
                row -= 1
                col -= 1

    return result, len(result)


def sequence_lcs(s1, s2):
    col_string = s1 if len(s1) < len(s2) else s2
    row_string = s2 if len(s1) < len(s2) else s1

    dp = np.zeros((len(col_string) + 1, len(row_string) + 1), dtype=np.int32)

    for i in range(1, len(col_string) + 1):
        for j in range(1, len(row_string) + 1):
            if col_string[i - 1] == row_string[j - 1] and col_string[i - 1] != "*":
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    result = get_result(dp, col_string, row_string)

    return result


def sequence_experiment(list_of_jobs):
    final_result = []
    for i in range(3):
        result = sequence_lcs(list_of_jobs[i][0], list_of_jobs[i][1])
        final_result.append(result)
    # print("Max Length:", min(final_result, key=lambda x: x[1]))


def parallel_experiment(list_of_jobs):
    if rank == MASTER:
        final_result = []

    for i in range(3):
        if rank == i:
            result = cuda_lcs(list_of_jobs[i][0], list_of_jobs[i][1])

            if rank == MASTER:
                final_result.append(result)
                for j in range(1, nproc):
                    result = comm.recv(source=j)
                    final_result.append(result)
            else:
                comm.send(result, dest=MASTER)

    # if rank == MASTER:
    #     print("Max Length:", min(final_result, key=lambda x: x[1]))


def create_graph(experiment_parallel, experiment_sequence):
    dimensions = [result["dimensions"] for result in experiment_parallel]
    time_para = [result["time"] for result in experiment_parallel]
    time_sequence = [result["time"] for result in experiment_sequence]

    x = np.arange(len(dimensions))
    width = 0.35

    fig, ax = plt.subplots()

    rects1 = ax.bar(x - width / 2, time_para, width, label='Parallel', color="r")
    rects2 = ax.bar(x + width / 2, time_sequence, width, label='Series', color="g")

    ax.set_xlabel("Length of three strings")
    ax.set_ylabel("Time [s]")
    ax.set_title("Comparison of Parallel and Sequence Experiments")
    ax.set_xticks(x)
    ax.set_xticklabels(dimensions)
    ax.legend()

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    ax.legend()
    plt.show()


if __name__ == '__main__':
    main()
