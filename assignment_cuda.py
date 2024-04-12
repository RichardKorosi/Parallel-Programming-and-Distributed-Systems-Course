"""This file is implementation of the 5th (week 8) assignment of the PPDS.

The solutions of this assignment was inspired by the following source(s):
    - https://en.wikipedia.org/wiki/Samplesort
    - https://github.com/tj314/ppds-seminars/tree/ppds2024/seminar8
        - 02-cv-multi-kernel_streams.py
Function create_buckets was explained in documentation and inspired
    by the following source(s):
    - https://www.w3schools.com/python/gloss_python_for_else.asp
Functions series_bubble_sort and my_kernel were made 
    with the help of the following source(s):
    - https://www.geeksforgeeks.org/bubble-sort/
Function create_graph was inspired by the following source(s):
    -https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html

More info about the assignment can be found in the README.md document.
"""

import numpy as np
from numba import cuda
import time
import warnings
from numba.core.errors import NumbaPerformanceWarning
import matplotlib.pyplot as plt
import math

warnings.filterwarnings("ignore", category=NumbaPerformanceWarning)


def create_buckets(array, splitters):
    """Create buckets of the array based on the splitters.

    More specifically, this function creates buckets of the array based
    on the splitters. Buckets are not sorted. The first bucket contains
    all the elements that are smaller than the first splitter.
    Second one contains all the elements that are smaller
    than the second splitter etc. The last bucket contains all the
    elements that are greater than the last splitter.

    Keyword arguments:
    array -- the array to be sorted
    splitters -- the values that will be used to split the array
    """
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


def create_graph(experiment_parallel, experiment_series):
    """Create a bar graph of measured results of the experiment.

    Keyword arguments:
    experiment_parallel -- the results of the parallel experiment
    experiment_series -- the results of the series experiment
    """
    array_len = [result["array_len"] for result in experiment_parallel]
    no_buckets = [result["no_buckets"] for result in experiment_parallel]

    time_para = [result["time"] for result in experiment_parallel]
    time_series = [result["time"] for result in experiment_series]

    x = np.arange(len(array_len))
    width = 0.35

    fig, ax = plt.subplots()

    rects1 = ax.bar(x - width/2, time_para, width, label='Parallel', color="r")
    rects2 = ax.bar(x + width/2, time_series, width, label='Normal', color="g")

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
    """Sort the array using bubble sort algorithm.

    Keyword arguments:
    array -- the array to be sorted
    """
    for i in range(array.size):
        swapped = False
        for j in range(array.size - i - 1):
            if array[j] > array[j + 1]:
                array[j], array[j + 1] = array[j + 1], array[j]
                swapped = True
        if not swapped:
            break

    return array


@cuda.jit
def my_kernel(bucket):
    """Sort the array using bubble sort algorithm using GPU.

    Keyword arguments:
    bucket -- the array to be sorted
    """
    for i in range(bucket.size):
        swapped = False
        for j in range(bucket.size - i - 1):
            if bucket[j] > bucket[j + 1]:
                bucket[j], bucket[j + 1] = bucket[j + 1], bucket[j]
                swapped = True
        if not swapped:
            break


def main():
    """Execute the main function of the program.

    More specifically, in this function arrays of different
    lengths are created and sorted using parallel and series
    bubble sort. Sorting is also timed and the results of
    the experiments are printed and displayed in a bar graph.
    """
    no_experimtens = 1
    cuda_cores = 7168
    arrayDummy = np.random.rand(2).astype(np.float32)
    array0 = np.random.rand(10).astype(np.float32)
    array1 = np.random.rand(100).astype(np.float32)
    array2 = np.random.rand(1000).astype(np.float32)
    array3 = np.random.rand(10000).astype(np.float32)
    # array4 = np.random.rand(100000).astype(np.float32)
    experiment_arrays = [arrayDummy, array0, array1, array2, array3]
    experimetns_parallel = []
    sorted_in_parallel = []
    experiments_series = []
    sorted_in_series = []

    curr_arr_index = 0
    for array in experiment_arrays:
        avg_time = 0
        for _ in range(no_experimtens):
            array = np.copy(experiment_arrays[curr_arr_index])
            result = np.empty(0, dtype=np.float32)

            buckets_gpu = []
            no_splitters = int(array.shape[0] // math.sqrt(cuda_cores))
            splitters = np.random.choice(array, no_splitters, replace=False)
            splitters = np.sort(splitters)
            buckets = create_buckets(array, splitters)
            streams = [cuda.stream() for _ in range(len(buckets))]

            time_start = time.perf_counter()
            for bucket, stream in zip(buckets, streams):
                buckets_gpu.append(cuda.to_device(bucket, stream=stream))

            for bucket, stream in zip(buckets_gpu, streams):
                my_kernel[1, 1, stream](bucket)

            for bucket, stream in zip(buckets_gpu, streams):
                result = np.append(result, bucket.copy_to_host(stream=stream))

            time_end = time.perf_counter()
            avg_time += time_end - time_start

        experiment = {"array_len": len(array), "no_buckets": len(buckets),
                      "time": (avg_time / no_experimtens)}
        experimetns_parallel.append(experiment)
        sorted_in_parallel.append(result)
        print("DONE PARALLEL")
        curr_arr_index += 1


    curr_arr_index = 0
    for array in experiment_arrays:
        avg_time = 0
        for _ in range(no_experimtens):
            array = np.copy(experiment_arrays[curr_arr_index])
            time_start = time.perf_counter()
            array = series_bubble_sort(array)
            time_end = time.perf_counter()
            avg_time += time_end - time_start
        experiment = {"array_len": len(array),
                      "time": (avg_time / no_experimtens)}
        experiments_series.append(experiment)
        sorted_in_series.append(array)
        print("DONE NORMAL")
        curr_arr_index += 1

    for experiment in experimetns_parallel[1:]:
        print(experiment)
    for experiment in experiments_series[1:]:
        print(experiment)
    
    for array in sorted_in_parallel:
        print(np.all(array[:-1] <= array[1:]))
    for array in sorted_in_series:
        print(np.all(array[:-1] <= array[1:]))

    create_graph(experimetns_parallel[1:], experiments_series[1:])


if __name__ == '__main__':
    main()
