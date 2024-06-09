#!/usr/bin/env python3

import os
import argparse
import re
from Bio import Phylo


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, 
    description="""Showing simple visualisation of computed tree""")
    parser.add_argument('input', type=str, nargs=1, help="""Path to the input 
        or .tree file containing paths to fasta files""", default=None)
    args = parser.parse_args()
    in_file=""
    if args.input is None:
        print(f"Provide input file")
    elif not os.path.isfile(args.input[0]):
        print(f"Provide input file: {args.input[0]} doesn't exist")
    else:
        in_file=args.input[0]
        if not re.search(".+[.]tree$",in_file):
            print(f"Input file {in_file} not recognized as correct .tree file.")
            in_file=""
    if in_file:    
        return[in_file]
    else:
        return None

def main():
    inputs=parse_args()
    
    if not inputs is None:
        print(f"{' '*16}> Plot tree < \n\n{'#'*20}START{'#'*20}")
        print(f"\nInput file:\t\t\t{inputs[0]}\n")
        tree = Phylo.read(inputs[0],"newick")
        tree.ladderize()
        Phylo.draw(tree)



if __name__ == "__main__":
    main()