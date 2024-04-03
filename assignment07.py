import numpy as np
from mpi4py import MPI
import time
import matplotlib.pyplot as plt

"""This file is implementation of the 4th (week 7) assignment of the PPDS."""

__author__ = "Richard Körösi"

MASTER = 0
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
nproc = comm.Get_size()


def p2p_version(nra, nca, ncb):
    """Compute matrix multiplication using P2P communication.

    More specifically, this function computes the matrix multiplication of
    two matrices A and B using P2P communication. (Distribution of rows of
    matrix A `A_loc` to different processes using `comm.send` and `comm.recv`)
    This function allows usage of `nproc` processes. `nra` number doesn't
    have to be divisible by `nproc`.

    Keyword arguments:
    nra -- number of rows of matrix A
    nca -- number of columns of matrix A
    ncb -- number of columns of matrix B"""

    print(f"{rank}: Starting parallel matrix multiplication "
          f"example using P2P communication...")
    print(f"{rank}: Using matrix sizes A[{nra}][{nca}], "
          f"B[{nca}][{ncb}], C[{nra}][{ncb}]")

    avg_rows = nra // nproc
    extras = nra % nproc
    rows = None
    offset = 0

    if rank == MASTER:
        print(f"{rank}: Initializing matrices A and B.")
        A = (np.array([i + j for j in range(nra) for i in range(nca)])
             .reshape(nra, nca))
        B = (np.array([i * j for j in range(nca) for i in range(ncb)])
             .reshape(nca, ncb))
        rows = avg_rows + 1 if extras else avg_rows

        for proc in range(nproc):
            rows_for_process = avg_rows + 1 if proc < extras else avg_rows
            if proc == MASTER:
                A_loc = A[offset:(offset + rows_for_process)]
                offset += rows_for_process
                continue
            comm.send(A[offset:(offset + rows_for_process)], dest=proc)
            offset += rows_for_process
    else:
        A_loc = comm.recv()
        rows = A_loc.shape[0]
        B = None

    B = comm.bcast(B, root=MASTER)

    # Perform sequential matrix multiplication
    C_loc = np.zeros((rows, ncb), dtype=int)
    print(f"{rank}: Performing matrix multiplication...")
    for i in range(rows):
        for j in range(ncb):
            for k in range(nca):
                C_loc[i][j] += A_loc[i][k] * B[k][j]

    # Combine results into matrix C
    if rank == MASTER:
        C = np.zeros((nra, ncb), dtype=int)
        offset = 0
        for proc in range(nproc):
            rows_for_process = avg_rows + 1 if proc < extras else avg_rows
            if proc == MASTER:
                C[offset:(offset + rows_for_process)] = C_loc
                offset += rows_for_process
                continue
            C[offset:(offset + rows_for_process)] = comm.recv(source=proc)
            offset += rows_for_process
        print(f"{rank}: Here is the result matrix:")
        print(C)
    else:
        comm.send(C_loc, dest=MASTER)

    print(f"{rank}: Done.")


def collective_version(nra, nca, ncb):
    """Compute matrix multiplication using collective communication.

    More specifically, this function computes the matrix multiplication of
    two matrices A and B using collective communication.
    (Distribution of rows of matrix A (`A_loc`) to different processes
    using `comm.scatter` and `comm.gather`)
    This function allows usage of `nproc` processes. `nra` number doesn't
    have to be divisible by `nproc`.

    Keyword arguments:
    nra -- number of rows of matrix A
    nca -- number of columns of matrix A
    ncb -- number of columns of matrix B"""

    print(f"{rank}: Starting parallel matrix multiplication example "
          f"using collective communication...")
    print(f"{rank}: Using matrix sizes A[{nra}][{nca}], "
          f"B[{nca}][{ncb}], C[{nra}][{ncb}]")

    A = None
    B = None
    if rank == MASTER:
        print(f"{rank}: Initializing matrices A and B.")
        A = (np.array([i + j for j in range(nra) for i in range(nca)])
             .reshape(nra, nca))
        A = np.array_split(A, nproc)
        B = (np.array([i * j for j in range(nca) for i in range(ncb)])
             .reshape(nca, ncb))

    A_loc = comm.scatter(A, root=MASTER)
    B = comm.bcast(B, root=MASTER)
    rows = A_loc.shape[0]

    # Perform sequential matrix multiplication
    C_loc = np.zeros((rows, ncb), dtype=int)
    print(f"{rank}: Performing matrix multiplication...")
    for i in range(rows):
        for j in range(ncb):
            for k in range(nca):
                C_loc[i][j] += A_loc[i][k] * B[k][j]

    # Combine results into matrix C
    C = comm.gather(C_loc, root=MASTER)
    if rank == MASTER:
        C = np.array([ss for s in C for ss in s])
        print(f"{rank}: Here is the result matrix:")
        print(C)

    print(f"{rank}: Done.")


def measure_version(version):
    """Measure the avg. times of experiments.

    More specifically, this function measures the average time
    of matrix multiplication using the specified version of
    communication out of 100 runs. Measured matrix sizes are
    {"nra": 128, "nca": 60, "ncb": 28},
    {"nra": 256, "nca": 120, "ncb": 56},
    {"nra": 512, "nca": 240, "ncb": 112},
    {"nra": 240, "nca": 120, "ncb": 112},
    {"nra": 512, "nca": 112, "ncb": 240}.\n
    Function returns a list of dictionaries containing
    the matrix sizes, average time of matrix multiplication,
    version of communication and number of processes used.

    Keyword arguments:
    version -- the version of the matrix multiplication algorithm to be used"""
    matrix = [{"nra": 128, "nca": 60, "ncb": 28},
              {"nra": 256, "nca": 120, "ncb": 56},
              {"nra": 512, "nca": 240, "ncb": 112},
              {"nra": 240, "nca": 120, "ncb": 112},
              {"nra": 512, "nca": 112, "ncb": 240},
              ]
    results = []
    for matrix in matrix:
        nra = matrix["nra"]
        nca = matrix["nca"]
        ncb = matrix["ncb"]

        times = []
        for _ in range(1):
            if version == "P2P":
                start_time = time.time()
                p2p_version(nra, nca, ncb)
                end_time = time.time()
            elif version == "COLLECTIVE":
                start_time = time.time()
                collective_version(nra, nca, ncb)
                end_time = time.time()
            else:
                raise ValueError("Invalid version")
            times.append(end_time - start_time)

        average_time = sum(times) / len(times)
        results.append({"nra": nra, "nca": nca, "ncb": ncb,
                        "time": average_time, "version": version,
                        "nproc": nproc})

    return results


def createGraph(p2p_results, collective_results):
    """Create a bar graph of measured results of the experiment.

    Keyword arguments:
    p2p_results -- the results of the experiment using P2P communication
    collective_results -- the results of the experiment using col communication
    """
    nras = [result["nra"] for result in p2p_results]
    ncas = [result["nca"] for result in p2p_results]
    ncbs = [result["ncb"] for result in p2p_results]

    p2pVersion = p2p_results[0]["version"]
    p2p_times = [result["time"] for result in p2p_results]
    collectiveVersion = collective_results[0]["version"]
    collective_times = [result["time"] for result in collective_results]

    x = np.arange(len(nras))
    width = 0.25

    fig, ax = plt.subplots()

    rects1 = ax.bar(x, p2p_times, width, label=p2pVersion, color="r")
    rects2 = ax.bar(x + width, collective_times, width,
                    label=collectiveVersion, color="g")

    ax.set_xlabel("Matrix sizes [NRA][NCA][NCB]")
    ax.set_ylabel("Time [s]")
    ax.set_title(f"Average times of matrix multiplication"
                 f" with {nproc} processes \n after 100 runs")
    labels = [f"NRA:{nra}\nNCA:{nca}\nNCB:{ncb}"
              for nra, nca, ncb in zip(nras, ncas, ncbs)]
    ax.set_xticks(x + width / 2)
    ax.set_xticklabels(labels)

    ax.bar_label(rects1)
    ax.bar_label(rects2)

    ax.legend()
    plt.show()


def main():
    """Main function of the program.

    In this function, the results of the matrix multiplication
    using P2P and collective communication are measured
    and printed out. After that, a bar graph is created
    using the measured results. Only the master process
    prints out the results and creates the graph.
    """

    results2 = measure_version("COLLECTIVE")
    results = measure_version("P2P")

    if rank == MASTER:
        for result in results:
            print(result, end="\n")
        print("\n")
        for result in results2:
            print(result, end="\n")

    if rank == MASTER:
        createGraph(results, results2)


if __name__ == "__main__":
    main()
