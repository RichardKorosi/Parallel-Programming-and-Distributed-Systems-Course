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
def cuda_kernel(dp_cuda, anti_diagonal, elements_for_thread):
    pos = cuda.grid(1)
    length = len(anti_diagonal)
    start = pos * elements_for_thread
    end = min(start + elements_for_thread, length)

    for i in range(start, end):
        x, y = anti_diagonal[i]
        dp_cuda[x, y] = pos + 1


def main():
    string1 = "textabc"
    string2 = "teixabc"

    cuda_lcs(string1, string2)


def cuda_lcs(s1, s2):
    x_string = s1 if len(s1) >= len(s2) else s2
    y_string = s2 if len(s1) >= len(s2) else s1

    x_string = list(x_string.encode('utf-8'))
    y_string = list(y_string.encode('utf-8'))

    dp = np.zeros((len(x_string) + 1, len(y_string) + 1), dtype=np.int32)
    dp_cuda = cuda.to_device(dp)
    no_anti_diagonal = len(x_string) + len(y_string) - 1
    blocks_per_grid = 1

    for i in range(1, no_anti_diagonal + 1):
        x = min(i, len(x_string))
        y = i - x + 1
        anti_diagonal = get_anti_diagonal(x, y, dp)
        elements_for_thread = min(2, len(anti_diagonal))
        threads_per_block = math.ceil(len(anti_diagonal) / elements_for_thread)
        cuda_kernel[blocks_per_grid, threads_per_block](dp_cuda, anti_diagonal,
                                                        elements_for_thread)

    dp_result = dp_cuda.copy_to_host()

    print(x_string, bytes(x_string).decode('utf-8'))
    print(y_string, bytes(y_string).decode('utf-8'))

    print(dp_result)


def get_anti_diagonal(x, y, dp):
    anti_diagonal = []
    while x >= 1 and y < len(dp[0]):
        anti_diagonal.append([x, y])
        x -= 1
        y += 1
    return np.array(anti_diagonal, dtype=np.int32)


if __name__ == '__main__':
    main()
