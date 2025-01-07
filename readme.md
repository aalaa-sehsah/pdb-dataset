# pdb-dataset

Instead of focusing on the full atomic details, we chose to represent protein structures as **2D pairwise distance matrices** between **α-carbons** on the protein backbone. This approach allows us to retain essential structural information while simplifying the data we work with.

## Files and Their Functions

- `requirements.txt`
  - Contain the required Python libraries.
  - Run `python -m pip install -r requirements.txt` in terminal.
- `dataset_generate.py`
  - Generate distance matrices from PDB files.
  - Store and compress the dataset as `.hdf5` files.

## Generated dataset

We extract non-overlapping fragments of lengths (64, 128, 256 and 512) for each protein structure starting at the first residue

| Distance Matrix Size (aa) | Distance Matrices Count | Compressed HDF5 Size (GiB) | Memory Usage (GiB) |
| :------------------: | :--------------------------: | :------------------------: | :----------------: |
|          64          |           330,950            |             5.4            |        10.1        |
|         128          |            98,728            |             6.4            |        12.0        |
|         256          |            13,591            |             3.5            |         6.6        |
|         512          |             779              |             0.7            |         1.5        |

## References

- Anand, N., & Huang, P. (2018). *Generative modeling for protein structures*. <https://papers.nips.cc/paper/7978-generative-modeling-for-protein-structures>
- <https://github.com/collinarnett/protein_gan/tree/master/data>
