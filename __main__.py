from pathlib import Path
import multiprocessing as mp

from tqdm import tqdm
import h5py

from dataset_generator import generate_distance_matrices


def create_dataset(pdb_path: Path, hdf5_path: Path, res: int) -> bool:
    """Create a dataset in HDF5 format by combining all necessary steps."""

    if hdf5_path.exists() and hdf5_path.stat().st_size > 10_000:
        print(f"[INFO] Skip RES_{res}; file '{hdf5_path}' already exists!\n")
        return
    with h5py.File(hdf5_path, "w") as _:
        print(f"[INFO] File '{hdf5_path}' is created.")

    pdb_files = [file for file in pdb_path.glob("*.pdb")]
    with mp.Pool(processes=mp.cpu_count()) as pool:
        results = tqdm(
            pool.imap(generate_distance_matrices, [(f, res) for f in pdb_files]),
            total=len(pdb_files),
        )
        data = [i for sublist in results if sublist for i in sublist]

    # Show stats
    print(f"  len: {len(data)}")
    print(f"shape: {data[0].shape}")
    print(f"  min: {data[0].min()}")
    print(f"  max: {data[0].max()}")

    with h5py.File(hdf5_path, "a") as fp:
        fp.create_dataset(name="data", data=data, compression="gzip")
        print(f"[INFO] Append data to file '{hdf5_path}'\n")


if __name__ == "__main__":
    import sys
    import os

    dir_ = os.path.dirname(sys.argv[0])
    dir_ and os.chdir(dir_)

    PDB_DIR = Path("../pdb-database/pdb")
    DATASET_DIR = Path("generated_dataset")

    if not PDB_DIR.exists():
        print("[FATAL] Cannot find PDB database!")
        exit(1)

    DATASET_DIR.mkdir(exist_ok=True)

    for res in (64, 128, 256, 512):
        print(f"[INFO] Resolution: {res}")
        create_dataset(
            pdb_path=PDB_DIR,
            hdf5_path=DATASET_DIR / "dataset_{res}aa.hdf5".format(res=res),
            res=res,
        )
