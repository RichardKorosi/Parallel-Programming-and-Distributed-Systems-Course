import numpy as np
from mpi4py import MPI


NRA = 32  # number of rows in matrix A
NCA = 15  # number of columns in matrix A
NCB = 7   # number of columns in matrix B


MASTER = 0

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
nproc = comm.Get_size()
assert NRA % nproc == 0, f"#MPI_nodes should divide #rows of matrix A"

print(f"{rank}: Starting parallel matrix multiplication example...")
print(f"{rank}: Using matrix sizes A[{NRA}][{NCA}], B[{NCA}][{NCB}], C[{NRA}][{NCB}]")


rows = NRA // nproc
if rank == MASTER:
    print(f"{rank}: Initializing matrices A and B.")
    A = np.array([i+j for j in range(NRA) for i in range(NCA)]).reshape(NRA, NCA)
    B = np.array([i*j for j in range(NCA) for i in range(NCB)]).reshape(NCA, NCB)

    for proc in range(nproc):
        if proc == MASTER:
            A_loc = A[proc*rows:proc*rows+rows]
            continue
        comm.send(A[proc*rows:proc*rows+rows], dest = proc)
else:
    A_loc = comm.recv()
    B = None

B = comm.bcast(B, root = MASTER)

# Perform sequential matrix multiplication
C_loc = np.zeros((rows, NCB), dtype = int)
print(f"{rank}: Performing matrix multiplication...")
for i in range(rows):
    for j in range(NCB):
        for k in range(NCA):
            C_loc[i][j] += A_loc[i][k] * B[k][j]


# Combine results into matrix C
C = np.zeros((NRA, NCB), dtype = int)
if rank == MASTER:
    for proc in range(nproc):
        if proc == MASTER:
            C[proc*rows:proc*rows+rows] = C_loc
            continue
        C[proc*rows:proc*rows+rows] = comm.recv(source = proc)
    print(f"{rank}: Here is the result matrix:")
    print(C)
else:
    comm.send(C_loc, dest = MASTER)

print(f"{rank}: Done.")