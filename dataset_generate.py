from pathlib import Path
import multiprocessing as mp

import Bio.PDB as pdb
import h5py
import numpy as np
from tqdm import tqdm

import warnings

warnings.simplefilter("ignore")


def generate_distance_matrix(args) -> list[np.ndarray]:
    """Generate specified resolution a-carbon maps given a input directory."""
    file, res = args

    def split_matrix(matrix: np.ndarray):
        if len(matrix) >= res:
            for n in range(1, len(matrix) // res):
                # Creating matrices by traversing the spine of input matrix
                chunk = matrix[res * (n - 1) : res * n, res * (n - 1) : res * n]
                yield chunk

    parser = pdb.PDBParser()
    structure = parser.get_structure("X", file)
    for models in structure:
        residues = pdb.Selection.unfold_entities(models["A"], "R")
        ca_residues = [residue for residue in residues if "CA" in residue]
        size = len(ca_residues)
        distance_matrix = np.zeros((size, size), np.float64)
        for row, residue_one in enumerate(ca_residues):
            for col, residue_two in enumerate(ca_residues):
                distance_matrix[row, col] = residue_one["CA"] - residue_two["CA"]
        return list(split_matrix(distance_matrix))


def get_distance_matrices(path: str, res: int) -> list[np.ndarray]:
    """Clean the generated maps using all cores in the process."""
    pdb_files = [file for file in Path(path).glob("*.pdb")]
    with mp.Pool(processes=mp.cpu_count()) as pool:
        results = tqdm(
            pool.imap(generate_distance_matrix, [(f, res) for f in pdb_files]),
            total=len(pdb_files),
        )
        return [i for sublist in results if sublist for i in sublist]


def create_dataset(raw_pdb_path: str, path: str, res: int) -> bool:
    """Create a dataset in HDF5 format by combining all necessary steps."""
    if Path.exists(path):
        print(f"[INFO] Skip RES_{res}; file '{path}' exists\n")
        return

    with h5py.File(path, "w") as _:
        print(f"[INFO] Create file '{path}'")

    data = get_distance_matrices(raw_pdb_path, res)

    # Show stats
    print(f"  len: {len(data)}")
    print(f"shape: {data[0].shape}")
    print(f"  min: {data[0].min()}")
    print(f"  max: {data[0].max()}")

    with h5py.File(path, "a") as fp:
        fp.create_dataset(name="data", data=data, compression="gzip")
        print(f"[INFO] Append RES_{res} to file '{path}'\n")


if __name__ == "__main__":
    RAW_PDB_DATASET_DIR = "../pdb-database/pdb"
    GENERATED_DIR = "generated_dataset"

    Path.mkdir(Path(GENERATED_DIR), exist_ok=True)

    for res in (64, 128, 256, 512):
        path = Path(GENERATED_DIR, "dataset_{res}aa.hdf5".format(res=res))
        print(f"[INFO] Resolution: {res}")
        create_dataset(RAW_PDB_DATASET_DIR, path, res)
