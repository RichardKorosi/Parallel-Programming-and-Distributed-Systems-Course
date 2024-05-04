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
def cuda_kernel(dp, col_string, row_string, anti_diagonal, elements_for_thread):
    pos = cuda.grid(1)
    length = len(anti_diagonal)
    start = pos * elements_for_thread
    end = min(start + elements_for_thread, length)

    for i in range(start, end):
        # in CUDA row and col are reversed
        row = anti_diagonal[i][0]
        col = anti_diagonal[i][1]
        if col_string[col - 1] == row_string[row - 1]:
            dp[col, row] = dp[col - 1, row - 1] + 1
        else:
            dp[col, row] = max(dp[col - 1, row], dp[col, row - 1])


def main():
    string1 = "stone"
    string2 = "longest"

    source1 = "**textje********skoro***citatelny******unich"
    source2 = "text*v*tejtoknihe****ma*po***usc*****koniec**robot*rozum"
    source3 = "f*te**xt**sa*je***sko*rio**tu*"

    source1b = "textjeskorocitatelnyunich"
    source2b = "textvtejtoknihemapousckoniecrobotrozum"
    source3b = "ftextsajeskoriotu"

    cuda_lcs(string1, string2)
    print()
    cuda_lcs(source1b, source2b)
    print()
    cuda_lcs(source1b, source3b)
    print()
    cuda_lcs(source2b, source3b)


def cuda_lcs(s1, s2):
    col_string = s1 if len(s1) < len(s2) else s2
    row_string = s2 if len(s1) < len(s2) else s1

    print("col_string:", col_string)
    print("row_string:", row_string)

    col_string = list(col_string.encode('utf-8'))
    row_string = list(row_string.encode('utf-8'))
    dp = np.zeros((len(col_string) + 1, len(row_string) + 1), dtype=np.int32)

    dp_cuda = cuda.to_device(dp)
    col_string_cuda = cuda.to_device(col_string)
    row_string_cuda = cuda.to_device(row_string)

    no_anti_diagonal = len(col_string) + len(row_string) - 1
    blocks_per_grid = 1

    for i in range(1, no_anti_diagonal + 1):
        col = min(i, len(col_string))
        row = i - col + 1
        anti_diagonal = get_anti_diagonal(row, col, dp)

        elements_for_thread = min(2, len(anti_diagonal))
        threads_per_block = math.ceil(len(anti_diagonal) / elements_for_thread)

        (cuda_kernel[blocks_per_grid, threads_per_block]
         (dp_cuda, col_string_cuda, row_string_cuda, anti_diagonal, elements_for_thread))

    dp_result = dp_cuda.copy_to_host()
    col_string = bytes(col_string).decode('utf-8')
    row_string = bytes(row_string).decode('utf-8')

    # print(dp_result)
    # print(dp_result[-1, -1])
    get_result(dp_result, col_string, row_string)


def get_anti_diagonal(row, col, dp):
    anti_diagonal = []
    while col >= 1 and row < len(dp[0]):
        anti_diagonal.append([row, col])
        col -= 1
        row += 1
    return np.array(anti_diagonal, dtype=np.int32)


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

    print(result)


if __name__ == '__main__':
    main()
