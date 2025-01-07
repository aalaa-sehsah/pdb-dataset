from pathlib import Path
import multiprocessing as mp

import numpy as np
from tqdm import tqdm
import Bio.PDB as pdb
import h5py

import warnings

warnings.simplefilter("ignore")


def generate_distance_matrices(args) -> list[np.ndarray]:
    """Generate specified resolution a-carbon maps given an input directory."""
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
        for row, residue_1 in enumerate(ca_residues):
            for col, residue_2 in enumerate(ca_residues):
                distance_matrix[row, col] = residue_1["CA"] - residue_2["CA"]
        return list(split_matrix(distance_matrix))


def create_dataset(pdb_path: Path, hdf5_path: Path, res: int) -> bool:
    """Create a dataset in HDF5 format by combining all necessary steps."""

    def get_distance_matrices() -> list[np.ndarray]:
        """Clean the generated maps using all cores in the process."""
        pdb_files = [file for file in pdb_path.glob("*.pdb")]
        with mp.Pool(processes=mp.cpu_count()) as pool:
            results = tqdm(
                pool.imap(generate_distance_matrices, [(f, res) for f in pdb_files]),
                total=len(pdb_files),
            )
            return [i for sublist in results if sublist for i in sublist]

    if hdf5_path.exists() and hdf5_path.stat().st_size > 10_000:
        print(f"[INFO] Skip RES_{res}; file '{hdf5_path}' already exists!\n")
        return
    with h5py.File(hdf5_path, "w") as _:
        print(f"[INFO] File '{hdf5_path}' is created.")

    data: list[np.ndarray] = get_distance_matrices()

    # Show stats
    print(f"  len: {len(data)}")
    print(f"shape: {data[0].shape}")
    print(f"  min: {data[0].min()}")
    print(f"  max: {data[0].max()}")

    with h5py.File(hdf5_path, "a") as fp:
        fp.create_dataset(name="data", data=data, compression="gzip")
        print(f"[INFO] Append data to file '{hdf5_path}'\n")


if __name__ == "__main__":
    PDB_DIR = Path("../pdb-database/pdb")
    DATASET_DIR = Path("generated_dataset")

    DATASET_DIR.mkdir(exist_ok=True)

    for res in (64, 128, 256, 512):
        print(f"[INFO] Resolution: {res}")
        create_dataset(
            pdb_path=PDB_DIR,
            hdf5_path=DATASET_DIR / "dataset_{res}aa.hdf5".format(res=res),
            res=res,
        )
