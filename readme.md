# pdb-dataset

We generate from the downloaded full-atom protein files, a distance matrix representation of their tertiary structure.

## Environment

- VS Code
- Python 3.12
- Libraries in `requirements.txt`

## Files and Their Functions

- `requirements.txt`
  - Contains the required Python libraries.
  - USER: Run `python -m pip install -r requirements.txt` in terminal.
- `__main__.py`
  - Generates distance matrices from PDB files.
  - Stores and compresses the dataset as `.hdf5` files.

## Generated dataset

We extract non-overlapping fragments of lengths (64, 128, 256 and 512) for each protein structure starting at the first residue

| Distance Matrix Size (aa) | Distance Matrices Count | Compressed HDF5 Size (GiB) | Memory Usage (GiB) |
| :------------------: | :--------------------------: | :------------------------: | :----------------: |
|          64          |           330,950            |             5.4            |        10.1        |
|         128          |            98,728            |             6.4            |        12.0        |
|         256          |            13,591            |             3.5            |         6.6        |
|         512          |             779              |             0.7            |         1.5        |

NOTE: It is better to use uncompressed datasets; as the compressed ones slow down the loading.

## References

- Anand, N., & Huang, P. (2018). *Generative modeling for protein structures*. <https://papers.nips.cc/paper/7978-generative-modeling-for-protein-structures>
- <https://github.com/collinarnett/protein_gan/tree/master/data>
