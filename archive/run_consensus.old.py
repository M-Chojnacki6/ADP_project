#!/usr/bin/env python3

"""
Script Name: run_consensus.py

Version: 4

Description:
Construct a consensus tree based on unrooted gene trees

Usage:
    python run_consensus.py TBD

"""

from dendropy import TaxonNamespace, TreeList

def run_consensus():
    # Initialize a TreeList object
    # Select trees that have a full set of taxa as leaves
    tlist = TreeList.get(path="trees_np.txt",
            schema="newick",
            rooting="default-unrooted",
            taxon_namespace=TaxonNamespace(aliases))

    with open("trees_cnp.txt", "w") as f:
        pass

    # All trees used to make consensus require to have the same set of taxa
    desired_num_leaves = len(aliases)

    # Open the output file in append mode
    with open("trees_cnp.txt", "a") as outfile:
        # Iterate through trees in the TreeList
        for tree in tlist:
            # Check the number of leaves
            num_leaves = len(tree.leaf_nodes())

            # If the number of leaves is equal to 23, append to the new file
            if num_leaves == desired_num_leaves:
                outfile.write(tree.as_string(schema="newick"))

    # Read selected trees
    tlist = TreeList.get(path="trees_cnp.txt",
            schema="newick",
            rooting="default-unrooted",
            taxon_namespace=TaxonNamespace(aliases))
    
if __name__ == "__main__":
    # Needed at input:
    # path to file with gene trees (one tree per line in newick format)
    # aliases - list of unique aliases for 
    # example:
    aliases = ["ECOL", "HSAP"]

    run_consensus()
