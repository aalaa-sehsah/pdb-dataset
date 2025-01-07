import numpy as np
import Bio.PDB as pdb

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
