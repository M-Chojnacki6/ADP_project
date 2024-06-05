#!/usr/bin/env python3

from Bio import Phylo
from Bio import AlignIO
from Bio.Phylo.TreeConstruction import DistanceCalculator
from Bio.Phylo.TreeConstruction import DistanceTreeConstructor
import argparse
import os

def nj_tree(alignment_file):
    directory, filename = os.path.split(alignment_file)
    calculator = DistanceCalculator('identity')
    align = AlignIO.read(alignment_file, "clustal")
    distance_matrix = calculator.get_distance(align)
    constructor = DistanceTreeConstructor()
    NJTree = constructor.nj(distance_matrix)

    # Remove internal node labels
    for internal in NJTree.get_nonterminals():
        internal.name = ""

    # Don't save if tree has negative branch length
    if not any(edge.branch_length is not None and edge.branch_length < 0 for edge in NJTree.find_clades()):

        if directory:
            directory+='/'
        
        print(f'{directory} and path {filename}')
        Phylo.write(NJTree, f'{directory}{filename.split(".")[0]}_njtree.nwk', "newick")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Construct Neighbour Joining tree from a given alignment file')
    parser.add_argument('aln_file', type=str, help='Path to your alignment file')
    args = parser.parse_args()
    nj_tree(args.aln_file)
