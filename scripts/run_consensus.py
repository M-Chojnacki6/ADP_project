#!/usr/bin/env python3

import os
import dendropy
import argparse

# Function to read taxa from list.txt
def read_taxa_list(filename):
    with open(filename, 'r') as file:
        taxa_list = [line.strip() for line in file.readlines()]
    return taxa_list


# Function to replace leaves with taxa names in DendroPy tree
def replace_leaves(tree, taxa_list):
    for leaf in tree.leaf_nodes():
        leaf.taxon.label = taxa_list[int(leaf.taxon.label)]
    return tree

# Main function
def main(folder, taxa_filename, min_freq):
    cons_tree = folder + '/CONSENSUS.tree'
    tree_list = dendropy.TreeList()
    taxa_list = read_taxa_list(taxa_filename)

    for filename in os.listdir(folder):
        if filename.endswith('.nwk') or filename.endswith('.newick'):
            tree_path = os.path.join(folder, filename)
            tree = dendropy.Tree.get(path=tree_path, schema='newick')
            tree = replace_leaves(tree, taxa_list)
            tree_list.append(tree)

    # Generate consensus tree
    consensus_tree = tree_list.consensus(min_freq=min_freq, is_bipartitions_updated=True)

    # Save the consensus tree to the output file
    consensus_tree.write(path=cons_tree, schema='newick')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Consensus tree calculator')
    parser.add_argument('folder', type=str, help='Folder containing tree files .nwk')
    parser.add_argument('taxa_list', type=str, help='Text file with a list of taxa to replace the numbers')
    parser.add_argument('min_freq', type=float, help='Minimum frequency of splits to be considered in the consensus tree')

    args = parser.parse_args()
    
    main(args.folder, args.taxa_list, args.min_freq)

