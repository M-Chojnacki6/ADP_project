from Bio import Phylo
from Bio import AlignIO
from Bio.Phylo.TreeConstruction import DistanceCalculator
from Bio.Phylo.TreeConstruction import DistanceTreeConstructor
import argparse
import os

def nj_tree(alignment_file):
    directory, filename = os.path.split(alignment_file)
    calculator = DistanceCalculator('identity')
    align = AlignIO.read(alignment_file, "fasta")
    distance_matrix = calculator.get_distance(align)
    constructor = DistanceTreeConstructor()
    NJTree = constructor.nj(distance_matrix)
    if directory:
        directory+='/'
    print(f'{directory} and path {filename}')

    Phylo.write(NJTree, f'{directory}{filename.split(".")[0]}_njtree.nwk', "newick")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Construct Neighbour Joining tree from a given alignment file')
    parser.add_argument('aln_file', type=str, help='Path to your alignment file')
    args = parser.parse_args()
    nj_tree(args.aln_file)
