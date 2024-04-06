import math
import numpy as np
from numba import cuda
import time
import warnings
from numba.core.errors import NumbaPerformanceWarning
import matplotlib.pyplot as plt

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


def create_graph(experiment_parallel, experiment_normal):
    array_len = [result["array_len"] for result in experiment_parallel]
    no_buckets = [result["no_buckets"] for result in experiment_parallel]

    time_para = [result["time"] for result in experiment_parallel]
    time_normal = [result["time"] for result in experiment_normal]

    x = np.arange(len(array_len))
    width = 0.35

    fig, ax = plt.subplots()

    rects1 = ax.bar(x - width/2, time_para, width, label='Parallel', color="r")
    rects2 = ax.bar(x + width/2, time_normal, width, label='Normal', color="g")

    ax.set_xlabel("Array Length / Number of Buckets")
    ax.set_ylabel("Time [s]")
    ax.set_title("Comparison of Parallel and Normal Experiments")
    labels = [f"Len:{len}\nBuckets:{buckets}" for len, buckets in zip(array_len, no_buckets)]
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    ax.legend()
    plt.show()


@cuda.jit
def my_kernel(io_array):
    pos = cuda.grid(1)
    if pos < io_array.size:
        for i in range(pos + 1, io_array.size):
            if io_array[pos] > io_array[i]:
                io_array[pos], io_array[i] = io_array[i], io_array[pos]




def main():
    len1, len2, len3, len4 = 10000, 20000, 50000, 32
    array1 = create_unordered_array(len1)
    array2 = create_unordered_array(len2)
    array3 = create_unordered_array(len3)
    array4 = create_unordered_array(len4)
    experimetns_parallel = []
    experiments_normal = []

    
    for array in [array1, array2, array3, array4]:
        time_start = time.time()
        print("START:", array)
        result = np.empty(0, dtype=np.float32)
        threadsperblock = 32
        blockspergrid = math.ceil(array.shape[0] / threadsperblock)


        buckets_gpu = []
        no_splitters = threadsperblock - 1
        splitters = np.random.choice(array, no_splitters, replace=False)
        splitters = np.sort(splitters)
        buckets = create_buckets(array, splitters)
        streams = [cuda.stream() for _ in range(len(buckets))]

        for bucket, stream in zip(buckets, streams):
            buckets_gpu.append(cuda.to_device(bucket, stream=stream))
        
        for bucket, stream in zip(buckets_gpu, streams):
            my_kernel[blockspergrid, threadsperblock, stream](bucket)

        for bucket, stream in zip(buckets_gpu, streams):
            result = np.append(result, bucket.copy_to_host(stream=stream))

        
        print("SORTED:", result, "\n\n\n")
        time_end = time.time()
        experiment = {"array_len": len(array), "no_buckets": len(buckets), "time": (time_end - time_start)}
        experimetns_parallel.append(experiment)


    for array in [array1, array2, array3, array4]:
        time_start = time.time()

        print("START:", array)
        result = np.empty(0, dtype=np.float32)

        for i in range(array.shape[0]):
            for j in range(i + 1, array.shape[0]):
                if array[i] > array[j]:
                    array[i], array[j] = array[j], array[i]
        print("SORTED:", array, "\n\n\n")
        time_end = time.time()
        experiment = {"array_len": len(array), "no_buckets": len(buckets), "time": (time_end - time_start)}
        experiments_normal.append(experiment)

    for experiment in experimetns_parallel:
        print(experiment)
    for experiment in experiments_normal:
        print(experiment)

    create_graph(experimetns_parallel, experiments_normal)
    


if __name__ == '__main__':
    main()