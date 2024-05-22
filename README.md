# ECT (Easy Consensus Tree)

*by Mateusz Chojnacki, Krzysztof Łukasz, Younginn Park and Daniel Zalewski*

## Overview
Easy Consensus Tree allows the user to easily construct a consensus tree based on a specified list of species names. It automates the workflow from downloading proteomes and clustering sequences to building individual cluster trees and generating a final consensus tree, ensuring a streamlined and efficient process.

## Workflow outline

![pipeline](img/pipeline.png)

## TO-DO list
Our main goal is to create a tool for an easy construction of a consensus tree based on a user-defined list of species names.

- Prepare scripts for each of the steps of the workflow:
  - [ ] Dowloading proteomes from database (NCBI datasets/ Uniprot), Setting up short aliases for each of the species and renaming sequences (**Output: a single multifasta file**)
  - [ ] Clustering with MMseqs2, Setting the cutoff of cluster sizes at 10% of all species by default (or 3 in case of small number of species), filtering non-paralgous clusters (filtering=removing whole clusters or removing individual sequences?) (**Output: tsv file for cluster memberships**) and saving clusters sequences as multifasta files (**Output: a directory with multiple multifasta files with cluster sequences**)
  - [ ] MSA for each of the clusters (with Muscle, Mafft or ClustalW) (**Output: a directory with multiple multifasta files with aligned cluster sequences**)
  - [ ] Tree construcion for each of the clusters (NJ - watch out for negative branch weights) (**Output: multiple newick files for each of the cluster**)
  - [ ] Construction of consensus tree based on cluster trees with DendroPy/... (**Output: newick file**)
- [ ] Prepare environment setup for the user (`.yml` file) with [ncbi-datasets](https://anaconda.org/conda-forge/ncbi-datasets-cli), [mafft](https://anaconda.org/bioconda/mafft), specific python version (e.g. 3.10) and python packages (biopython, pandas, dendropy, numpy, ...), for this having a miniforge3 (mamba, recommended) or conda should be a requirement for the user (add to documentation)
- [ ] Prepare complete documentation for user

Benchmarking
- Compare results from our tool and known philogenetic trees
- Prepare set of examples.

Additional functionalities:
- Adding supertrees (fasturec)
- Cutoff for number of sequences / number of genomes
- Type of consensus and cutoff to consensus

 >**DISCLAIMER**: We cannot ensure, that the resulting trees correspond to correct species tree, especially when the provided species are distantly related.

 [old scripts](https://github.com/M-Chojnacki6/ADP_working)
