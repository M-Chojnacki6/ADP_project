# ECT (Easy Consensus Tree)
Repository for ADP project (v. 0.01 alpha)

## Workflow for consensus tree construction

![pipeline](img/pipeline.png)

## Main task
Our main goal is to create tool for an easy construction of a consensus tree based on a list of species names. 
- prepare tool according to description in workflow:
 - dowloading from database (NCBI datasets/ Uniprot)
 - clustering with cutoff 10% of provided species (or 3 in case of small number of species) and non-paralogous
 - MSA (with Muscle, Mafft or ClustalW) 
 - tree construcion (NJ)
 - construction of consensus tree with DendoPhy/...
- compare results from our tool and known philogenetic trees
- prepare complete documentation
- prepare set of examples.
Additional functionalities:
- adding supertrees (fasturec)
- cutoff for number of sequences / number of genomes
- type of consensus and cutoff to consensus

 We cannot ensure, that trees are correct in case, when species from different kingdoms are provided.
