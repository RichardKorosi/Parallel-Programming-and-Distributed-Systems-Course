import time
import math
import warnings
import string

import numpy as np
import matplotlib.pyplot as plt

# from mpi4py import MPI
from numba import cuda, core
from numba.core.errors import NumbaPerformanceWarning

warnings.filterwarnings("ignore", category=NumbaPerformanceWarning)


# MASTER = 0
# comm = MPI.COMM_WORLD
# rank = comm.Get_rank()
# nproc = comm.Get_size()


@cuda.jit
def cuda_kernel(dp, shorter, longer, anti_diagonal, elements_for_thread):
    pos = cuda.grid(1)
    length = len(anti_diagonal)
    start = pos * elements_for_thread
    end = min(start + elements_for_thread, length)

    for i in range(start, end):
        col = anti_diagonal[i][1]
        row = anti_diagonal[i][0]
        if shorter[col - 1] == longer[row - 1]:
            dp[col, row] = dp[col - 1, row - 1] + 1
        else:
            dp[col, row] = max(dp[col - 1, row], dp[col, row - 1])


def main():
    string1 = "stone"
    string2 = "longest"

    cuda_lcs(string1, string2)


def cuda_lcs(s1, s2):
    shorter = s1 if len(s1) < len(s2) else s2
    longer = s2 if len(s1) < len(s2) else s1

    print("shorter:", shorter)
    print("longer:", longer)

    shorter = list(shorter.encode('utf-8'))
    longer = list(longer.encode('utf-8'))
    dp = np.zeros((len(shorter) + 1, len(longer) + 1), dtype=np.int32)

    dp_cuda = cuda.to_device(dp)
    shorter_cuda = cuda.to_device(shorter)
    longer_cuda = cuda.to_device(longer)

    no_anti_diagonal = len(shorter) + len(longer) - 1
    blocks_per_grid = 1

    for i in range(1, no_anti_diagonal + 1):
        col = min(i, len(shorter))
        row = i - col + 1
        anti_diagonal = get_anti_diagonal(row, col, dp)

        elements_for_thread = min(2, len(anti_diagonal))
        threads_per_block = math.ceil(len(anti_diagonal) / elements_for_thread)

        (cuda_kernel[blocks_per_grid, threads_per_block]
         (dp_cuda, shorter_cuda, longer_cuda, anti_diagonal, elements_for_thread))

    dp_result = dp_cuda.copy_to_host()
    shorter = bytes(shorter).decode('utf-8')
    longer = bytes(longer).decode('utf-8')

    print(dp_result)
    get_result(dp_result, shorter, longer)


def get_anti_diagonal(row, col, dp):
    anti_diagonal = []
    while col >= 1 and row < len(dp[0]):
        anti_diagonal.append([row, col])
        col -= 1
        row += 1
    return np.array(anti_diagonal, dtype=np.int32)


def get_result(dp, shorter, longer):
    pass


if __name__ == '__main__':
    main()
