from pathlib import Path
import multiprocessing as mp

from tqdm import tqdm
import h5py

from dataset_generator import generate_distance_matrices


def create_dataset(
    pdb_path: Path, hdf5_path: Path, res: int, compression: bool = None
) -> bool:
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
        fp.create_dataset(name="data", data=data, compression=compression)
        print(f"[INFO] Append data to file '{hdf5_path}'\n")


if __name__ == "__main__":
    import os

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    import argparse

    parser = argparse.ArgumentParser(
        description="A script to create PDB dataset (using train/test files)"
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=["train", "test"],
        default="train",
        help="mode of operation: 'train', 'test'",
    )
    parser.add_argument(
        "--compressed",
        action="store_true",
        help="enable compression",
    )
    parser.add_argument("-64", action="store_true", help="output 64x64 resolution")
    parser.add_argument("-128", action="store_true", help="output 128x128 resolution")
    parser.add_argument("-256", action="store_true", help="output 256x256 resolution")
    parser.add_argument("-512", action="store_true", help="output 512x512 resolution")

    args = parser.parse_args()

    # Script arguments
    mode: str = args.mode
    compressed: bool = args.compressed
    resolutions: list[int] = [
        int(k) for k, v in args.__dict__.items() if k.isdecimal() and v
    ]

    if not resolutions:
        print("[WARN] No resolutions are specified!")
        print("[INFO] Resolution 128x128 is selected by default!\n")
        resolutions.append(128)
    print("[INFO] Script Arguments")
    print(f"[INFO] {mode=}")
    print(f"[INFO] {resolutions=}")
    print()

    database_path = Path(f"../pdb-database/pdb_{mode}")
    output_dir = Path(f"{mode}_dataset")

    if not database_path.exists():
        print("[EXIT] Cannot find PDB database!")
        exit(1)

    output_dir.mkdir(exist_ok=True)

    for i, res in enumerate(resolutions, start=1):
        print(f"[INFO] (iter={i}/{len(resolutions)}) {res}x{res}")
        create_dataset(
            pdb_path=database_path,
            hdf5_path=output_dir / "{res}aa.hdf5".format(res=res),
            res=res,
            compression="gzip" if compressed else None,
        )
