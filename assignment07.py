"""This file is implementation of the fourth/seventh assignment of the PPDS."""

__author__ = "Richard Körösi"

import numpy as np
from mpi4py import MPI
import time

MASTER = 0
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
nproc = comm.Get_size()

def p2p_version(nra, nca, ncb):   

    print(f"{rank}: Starting parallel matrix multiplication example...")
    print(f"{rank}: Using matrix sizes A[{nra}][{nca}], B[{nca}][{ncb}], C[{nra}][{ncb}]")

    avg_rows = nra // nproc
    extras = nra % nproc
    rows = None
    offset = 0

    if rank == MASTER:
        print(f"{rank}: Initializing matrices A and B.")
        A = np.array([i+j for j in range(nra) for i in range(nca)]).reshape(nra, nca)
        B = np.array([i*j for j in range(nca) for i in range(ncb)]).reshape(nca, ncb)
        rows = avg_rows + 1 if extras else avg_rows

        for proc in range(nproc):
            rows_for_process = avg_rows + 1 if proc < extras else avg_rows
            if proc == MASTER:
                A_loc = A[offset:(offset+rows_for_process)]
                offset += rows_for_process
                continue
            comm.send(A[offset:(offset+rows_for_process)], dest = proc)
            offset += rows_for_process
    else:
        A_loc = comm.recv()
        rows = A_loc.shape[0]
        B = None

    print(f"A_LOC {rank}: {A_loc}")
    B = comm.bcast(B, root = MASTER)

    # Perform sequential matrix multiplication
    C_loc = np.zeros((rows, ncb), dtype = int)
    print(f"{rank}: Performing matrix multiplication...")
    for i in range(rows):
        for j in range(ncb):
            for k in range(nca):
                C_loc[i][j] += A_loc[i][k] * B[k][j]


    # Combine results into matrix C
    C = np.zeros((nra, ncb), dtype = int)
    offset = 0
    if rank == MASTER:
        for proc in range(nproc):
            rows_for_process = avg_rows + 1 if proc < extras else avg_rows
            if proc == MASTER:
                C[offset:(offset+rows_for_process)] = C_loc
                offset += rows_for_process
                continue
            C[offset:(offset+rows_for_process)] = comm.recv(source = proc)
            offset += rows_for_process
        print(f"{rank}: Here is the result matrix:")
        print(C)
    else:
        comm.send(C_loc, dest = MASTER)

    print(f"{rank}: Done.")


def collective_version(nra, nca, ncb):

    print(f"{rank}: Starting parallel matrix multiplication example...")
    print(f"{rank}: Using matrix sizes A[{nra}][{nca}], B[{nca}][{ncb}], C[{nra}][{ncb}]")

    A = None
    B = None
    if rank == MASTER:
        print(f"{rank}: Initializing matrices A and B.")
        A = np.array([i+j for j in range(nra) for i in range(nca)]).reshape(nra, nca)
        A = np.array_split(A, nproc)
        B = np.array([i*j for j in range(nca) for i in range(ncb)]).reshape(nca, ncb)

    A_loc = comm.scatter(A, root = MASTER)
    B = comm.bcast(B, root = MASTER)
    rows = A_loc.shape[0]

    # Perform sequential matrix multiplication
    C_loc = np.zeros((rows, ncb), dtype = int)
    print(f"{rank}: Performing matrix multiplication...")
    for i in range(rows):
        for j in range(ncb):
            for k in range(nca):
                C_loc[i][j] += A_loc[i][k] * B[k][j]

    # Combine results into matrix C
    C = comm.gather(C_loc, root = MASTER)
    if rank == MASTER:
        C = np.array([ss for s in C for ss in s])
        print(f"{rank}: Here is the result matrix:")
        print(C)

    print(f"{rank}: Done.")


def measure_version(version = "P2P"):
    matrixes = [{"nra": 32, "nca": 15, "ncb": 7},
                {"nra": 64, "nca": 30, "ncb": 14},
                {"nra": 128, "nca": 60, "ncb": 28},
                {"nra": 256, "nca": 120, "ncb": 56},
                {"nra": 200, "nca": 200, "ncb": 200},
                ]
    results = []
    for matrix in matrixes:
        nra = matrix["nra"]
        nca = matrix["nca"]
        ncb = matrix["ncb"]

        times = []
        for _ in range(200):
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
        results.append({"nra": nra, "nca": nca, "ncb": ncb, "time": average_time, "version": version, "nproc": nproc})
    
    return results

def main():

    results = measure_version("P2P")

    if rank == MASTER:
        for result in results:
            print(result, end="\n\n")



if __name__ == "__main__":
    main()