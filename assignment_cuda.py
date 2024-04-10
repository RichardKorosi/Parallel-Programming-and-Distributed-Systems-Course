"""This file is implementation of the 5th (week 8) assignment of the PPDS."""

import numpy as np
from numba import cuda
import time
import warnings
from numba.core.errors import NumbaPerformanceWarning
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=NumbaPerformanceWarning)


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
    labels = [f"Len:{len}\nBuckets:{buckets}" for len,
              buckets in zip(array_len, no_buckets)]
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    ax.bar_label(rects1, padding=3)
    ax.bar_label(rects2, padding=3)

    ax.legend()
    plt.show()


def series_bubble_sort(array):
    for i in range(array.shape[0]):
        for j in range(i + 1, array.shape[0]):
            if array[i] > array[j]:
                array[i], array[j] = array[j], array[i]
    return array


@cuda.jit
def my_kernel(io_array):
    for i in range(io_array.size):
        for j in range(i + 1, io_array.size):
            if io_array[i] > io_array[j]:
                io_array[i], io_array[j] = io_array[j], io_array[i]


def main():
    no_experimtens = 10
    cuda_cores = 7168
    array1 = np.random.rand(100).astype(np.float32)
    array2 = np.random.rand(1000).astype(np.float32)
    array3 = np.random.rand(10000).astype(np.float32)
    experimetns_parallel = []
    sorted_in_parallel = []
    experiments_normal = []
    sorted_in_normal = []

    for array in [array1, array2, array3]:
        avg_time = 0
        for i in range(no_experimtens + 1):
            time_start = time.time()
            result = np.empty(0, dtype=np.float32)

            buckets_gpu = []
            no_splitters = min(56-1, array.shape[0])
            splitters = np.random.choice(array, no_splitters, replace=False)
            splitters = np.sort(splitters)
            buckets = create_buckets(array, splitters)
            streams = [cuda.stream() for _ in range(len(buckets))]

            for bucket, stream in zip(buckets, streams):
                buckets_gpu.append(cuda.to_device(bucket, stream=stream))

            for bucket, stream in zip(buckets_gpu, streams):
                my_kernel[1, 1, stream](bucket)

            for bucket, stream in zip(buckets_gpu, streams):
                result = np.append(result, bucket.copy_to_host(stream=stream))

            time_end = time.time()
            if i != 0:
                avg_time += time_end - time_start

        experiment = {"array_len": len(array), "no_buckets": len(buckets),
                      "time": (avg_time / no_experimtens)}
        experimetns_parallel.append(experiment)
        sorted_in_parallel.append(result)
        print("DONE PARALLEL")

    print("\n\n")

    for array in [array1, array2, array3]:
        avg_time = 0
        for i in range(no_experimtens + 1):
            time_start = time.time()
            array = series_bubble_sort(array)
            time_end = time.time()
            if i != 0:
                avg_time += time_end - time_start
        experiment = {"array_len": len(array), "no_buckets": len(buckets),
                      "time": (avg_time / no_experimtens)}
        experiments_normal.append(experiment)
        sorted_in_normal.append(array)
        print("DONE NORMAL")

    for experiment in experimetns_parallel:
        print(experiment)
    for experiment in experiments_normal:
        print(experiment)

    for sorted_array in sorted_in_parallel:
        print(np.all(sorted_array[:-1] <= sorted_array[1:]))
    for sorted_array in sorted_in_normal:
        print(np.all(sorted_array[:-1] <= sorted_array[1:]))

    create_graph(experimetns_parallel, experiments_normal)


if __name__ == '__main__':
    main()
