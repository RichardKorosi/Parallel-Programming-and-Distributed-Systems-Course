import time
import math
import warnings

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
def cuda_kernel(dp_cuda, anti_diagonal, i):
    pos = cuda.grid(1)
    if pos < len(anti_diagonal):
        x = anti_diagonal[pos][0]
        y = anti_diagonal[pos][1]
        dp_cuda[x, y] = i


def main():
    string1 = "textabc"
    string2 = "teixabc"

    cuda_lcs(string1, string2)


def cuda_lcs(s1, s2):
    x_string = s1 if len(s1) >= len(s2) else s2
    y_string = s2 if len(s1) >= len(s2) else s1

    dp = np.zeros((len(x_string) + 1, len(y_string) + 1), dtype=np.int32)
    dp_cuda = cuda.to_device(dp)
    no_anti_diagonal = len(x_string) + len(y_string) - 1
    threads_per_block = 1024
    blocks_per_grid = 1
    elements_for_thread = 2

    for i in range(1, no_anti_diagonal + 1):
        x = min(i, len(x_string))
        y = i - x + 1
        anti_diagonal = get_anti_diagonal(x, y, dp)

        cuda_kernel[1, 8](dp_cuda, anti_diagonal, i)

    dp_result = dp_cuda.copy_to_host()

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
