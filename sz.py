"""This file is implementation of the FINAL assignment of the PPDS.

Sources used in the implementation:
- Theory about LCS:
    FEI STU PPDS Lecture: https://shorturl.at/uILNR
    University at Buffalo: https://shorturl.a
- CUDA warm-up:
    NVDIA Forum: https://shorturl.at/eklAF
- Matplotlib chart:
    Matplotlib documentation: https://shorturl.at/iuwA6

More info about the assignment can be found in the README.md document.
"""

__author__ = "Richard Körösi"

import time
import math
import warnings

import numpy as np
import matplotlib.pyplot as plt

from mpi4py import MPI
from numba import cuda
from numba.core.errors import NumbaPerformanceWarning

warnings.filterwarnings("ignore", category=NumbaPerformanceWarning)

MASTER = 0
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
nproc = comm.Get_size()


@cuda.jit
def cuda_kernel(dp, col_string, row_string, start_col,
                start_row, elements_for_thread):
    """Calculate one anti-diagonal of the DP matrix in LCS problem.

    More specifically, this function calculates the values
    of the DP matrix for one anti-diagonal.
    The anti-diagonal is defined by the starting column and row.

    Keyword arguments:
    dp -- the DP matrix
    col_string -- the string of the column
    row_string -- the string of the row
    start_col -- the starting column of the anti-diagonal
    start_row -- the starting row of the anti-diagonal
    elements_for_thread -- the number of elements to
                           calculate for one thread
    """
    pos = cuda.grid(1)
    col = start_col - pos * elements_for_thread
    row = start_row + pos * elements_for_thread
    for i in range(elements_for_thread):
        if col < 1 or row > len(dp[0]):
            break
        if (col_string[col - 1] == row_string[row - 1]
                and col_string[col - 1] != 42):
            dp[col, row] = dp[col - 1, row - 1] + 1
        else:
            dp[col, row] = max(dp[col - 1, row], dp[col, row - 1])
        col -= 1
        row += 1


def main():
    """Run the main function of the program.

    More specifically, this function runs the main
    function of the program. It runs the parallel and sequence
    experiments for the LCS problem of three strings.
    The results are then compared and a graph is created.
    """
    source1 = ["**textje********skoro***citatelny******unich"
               * i for i in [1, 5, 15, 25, 35, 45]]
    source2 = [("text*v*tejtoknihe****ma*po***usc*****"
                "koniec**robot*rozum")
               * i for i in [1, 5, 15, 25, 35, 45]]
    source3 = ["f*te**xt**sa*je***sko*rio**tu*"
               * i for i in [1, 5, 15, 25, 35, 45]]

    experiment_parallel = []
    experiment_sequence = []
    info_about_threads = {"threads": 0,
                          "blocks_per_grid": 0,
                          "threads_per_block": 0}

    for x in range(len(source1)):
        list_of_jobs = [(source1[x], source2[x]),
                        (source1[x], source3[x]),
                        (source2[x], source3[x])]

        if rank == MASTER:
            times = []

        for i in range(5 + 1):
            if rank == MASTER:
                time_start = time.perf_counter()
            parallel_experiment(list_of_jobs, info_about_threads)
            if rank == MASTER:
                times.append(time.perf_counter() - time_start)

        if rank == MASTER:
            avg_time = sum(times[1:]) / (len(times) - 1)
            dimensions = (f"{len(source1[x])}"
                          f"x{len(source2[x])}"
                          f"x{len(source3[x])}")
            experiment_parallel.append({
                "dimensions": dimensions,
                "time": avg_time})

        if rank == MASTER:
            times = []
            for i in range(5 + 1):
                time_start = time.perf_counter()
                sequence_experiment(list_of_jobs)
                times.append(time.perf_counter() - time_start)

            avg_time = sum(times[1:]) / (len(times) - 1)
            dimensions = (f"{len(source1[x])}"
                          f"x{len(source2[x])}x"
                          f"{len(source3[x])}")
            experiment_sequence.append({"dimensions": dimensions,
                                        "time": avg_time})

    if rank == MASTER:
        create_graph(experiment_parallel,
                     experiment_sequence,
                     info_about_threads)


def cuda_lcs(s1, s2, info_about_threads):
    """Calculate the LCS of two strings using CUDA.

    This function calculates the Longest Common Subsequence
    of two strings using the CUDA parallelization.
    And returns the result.

    Keyword arguments:
    s1 -- the first string
    s2 -- the second string
    info_about_threads -- the dictionary to store
                          information about threads
    """
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
    elements_for_thread = math.ceil(no_anti_diagonal /
                                    (blocks_per_grid * threads_per_block))
    info_about_threads["threads"] = threads_per_block * blocks_per_grid
    info_about_threads["blocks_per_grid"] = blocks_per_grid
    info_about_threads["threads_per_block"] = threads_per_block

    for i in range(1, no_anti_diagonal + 1):
        col = min(i, len(col_string))
        row = i - col + 1

        (cuda_kernel[blocks_per_grid, threads_per_block]
         (dp_cuda, col_string_cuda, row_string_cuda,
          col, row, elements_for_thread))

    dp_result = dp_cuda.copy_to_host()
    col_string = bytes(col_string).decode('utf-8')
    row_string = bytes(row_string).decode('utf-8')

    result = get_result(dp_result, col_string, row_string)
    return result


def get_result(dp, row_string, col_string):
    """Get the result of the LCS problem.

    More specifically, this function returns the longest
    common subsequence of two strings.
    The result is calculated from the DP matrix.

    Keyword arguments:
    dp -- the DP matrix
    row_string -- the string of the row
    col_string -- the string of the column
    """
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
    """Calculate the LCS of two strings.

    This function calculates the Longest Common Subsequence
    of two strings using the dynamic programming approach.
    And returns the result.

    Keyword arguments:
    s1 -- the first string
    s2 -- the second string
    """
    col_string = s1 if len(s1) < len(s2) else s2
    row_string = s2 if len(s1) < len(s2) else s1

    dp = np.zeros((len(col_string) + 1,
                   len(row_string) + 1), dtype=np.int32)

    for i in range(1, len(col_string) + 1):
        for j in range(1, len(row_string) + 1):
            if (col_string[i - 1] == row_string[j - 1]
                    and col_string[i - 1] != "*"):
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    result = get_result(dp, col_string, row_string)

    return result


def sequence_experiment(list_of_jobs):
    """Run the sequence experiment.

    More specifically, this function runs the sequence experiment
    for the Longest Common Subsequence problem of three strings.
    It runs 3 times and returns the results.

    Keyword arguments:
    list_of_jobs -- the list of jobs to run the experiment
    """
    final_result = []
    for i in range(3):
        result = sequence_lcs(list_of_jobs[i][0], list_of_jobs[i][1])
        final_result.append(result)


def parallel_experiment(list_of_jobs, info_about_threads):
    """Run the parallel experiment.

    More specifically, this function runs the parallel experiment
    for the Longest Common Subsequence problem of three strings.
    It runs 3 times and returns the results.
    The difference between this function and the
    sequence_experiment function is that this function uses the CUDA
    and MPI parallelization.
    3 processors are used to run the experiment and run the
    3 jobs in parallel.

    Keyword arguments:
    list_of_jobs -- the list of jobs to run the experiment
    info_about_threads -- the dictionary to store
                          information about threads
    """
    if rank == MASTER:
        final_result = []

    for i in range(3):
        if rank == i:
            result = cuda_lcs(list_of_jobs[i][0], list_of_jobs[i][1],
                              info_about_threads)

            if rank == MASTER:
                final_result.append(result)
                for j in range(1, nproc):
                    result = comm.recv(source=j)
                    final_result.append(result)
            else:
                comm.send(result, dest=MASTER)

    if rank == MASTER:
        min_result = min(final_result, key=lambda x: x[1])
        print("LCS:", min_result[1], end=" ")
        if len(min_result[0]) <= 30:
            print(min_result[0])
        else:
            print(min_result[0][:13] + '...' + min_result[0][-13:])


def create_graph(experiment_parallel, experiment_sequence,
                 info_about_threads):
    """Create a graph of the experiment results.

    More specifically, this function creates a graph of the
    experiment results. The graph shows the comparison
    of the parallel and sequence experiments.

    Keyword arguments:
    experiment_parallel -- the results of the parallel experiment
    experiment_sequence -- the results of the sequence experiment
    info_about_threads -- the information about threads
    """
    dimensions = [result["dimensions"] for result in experiment_parallel]
    time_para = [result["time"] for result in experiment_parallel]
    time_sequence = [result["time"] for result in experiment_sequence]

    x = np.arange(len(dimensions))
    width = 0.35

    fig, ax = plt.subplots()

    rects1 = ax.bar(x - width / 2, time_para, width,
                    label='Parallel', color="r")
    rects2 = ax.bar(x + width / 2, time_sequence, width,
                    label='Sequence', color="g")

    ax.set_xlabel("Length of three strings")
    ax.set_ylabel("Time [s]")
    ax.set_title("Comparison of Parallel and Sequence Experiments")
    ax.set_xticks(x)
    ax.set_xticklabels(dimensions)

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    # Add information about threads
    threads_info = \
        f"Threads for 1 processor: {info_about_threads['threads']}\n" \
        f"Threads per block: {info_about_threads['threads_per_block']}\n" \
        f"Blocks per grid: {info_about_threads['blocks_per_grid']}"

    # Create a custom legend entry
    from matplotlib.lines import Line2D
    custom_lines = [Line2D([0], [0], color='r', lw=4),
                    Line2D([0], [0], color='g', lw=4),
                    Line2D([0], [0], color='w', lw=4)]
    ax.legend(custom_lines, ['Parallel', 'Sequence', threads_info])

    plt.show()


if __name__ == '__main__':
    main()
