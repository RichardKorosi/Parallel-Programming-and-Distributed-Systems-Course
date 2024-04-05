import math
import numpy as np
from numba import cuda
import warnings
from numba.core.errors import NumbaPerformanceWarning

warnings.filterwarnings("ignore", category=NumbaPerformanceWarning)

def create_unordered_array(n):
    return np.random.rand(n).astype(np.float32)

def create_buckets(array, splitters):
    no_buckets = len(splitters) + 1
    buckets = [np.empty(0, dtype=np.float32) for _ in range(no_buckets)]

    for element in array:
        b_i = 0
        for splitter in splitters:
            if element < splitter:
                buckets[b_i] = np.append(buckets[b_i], element)
                break
            b_i += 1
        else:
            buckets[b_i] = np.append(buckets[b_i], element)
            
    return buckets


@cuda.jit
def my_kernel(io_array):
    pass


def main():
    len1, len2, len3 = 6, 6, 6
    array1 = create_unordered_array(len1)
    array2 = create_unordered_array(len2)
    array3 = create_unordered_array(len3)

    
    for array in [array1, array2, array3]:
        no_proc = 3
        no_splitters = no_proc - 1
        splitters = np.random.choice(array, no_splitters, replace=False)
        splitters = np.sort(splitters)
        buckets = create_buckets(array, splitters)
        print(array)
        print(splitters)
        print(buckets)
        print("-------------------")

        # my_kernel[blockspergrid, threadsperblock](data_mem)
        # data = data_mem.copy_to_host()
        # print(data)


if __name__ == '__main__':
    main()