# ECT (Easy Consensus Tree)

*by Mateusz Chojnacki, Krzysztof Łukasz, Younginn Park and Daniel Zalewski*

## Overview
**Easy Consensus Tree** allows the user to easily construct a whole-proteome consensus tree based on a specified list of species names. It automates the workflow from downloading proteomes and clustering sequences to building individual cluster trees and generating a final consensus tree, ensuring a streamlined and efficient process. The user-friendly setup makes it accessible even for those with minimal bioinformatics experience.

## Workflow outline

![pipeline](img/pipeline.png)

## Requirements


To run this tool, you need to have `conda` installed. We recommend using [`miniforge`](https://github.com/conda-forge/miniforge), which is a lightweight installer for `conda`.


Instruction for installing miniforge
```{bash}
# Run
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
# OR
wget "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
# Then
bash Miniforge3-$(uname)-$(uname -m).sh
```

## Installation

```{bash}
git clone https://github.com/M-Chojnacki6/ECT.git

# Go to the project directory
cd ECT

# Run
conda env create -f environment.yml
# mamba env create -f environment.yml # faster
```

## Usage

Example usage: If the list of species called `species.txt` is located in the parent directory relative to ECT directory then run:

```
./ECT/ect.sh -i species.txt
```

>**DISCLAIMER**: We cannot guarantee that the resulting trees will accurately reflect the true relationships between species, especially if the provided species are distantly related.


## Potential future enhancements

- Option for the user to define species for an outgroup to root the tree on
- Adding supertrees (fasturec) for paralogus clusters
- Cutoff for number of sequences / number of genomes
- Type of consensus and cutoff to consensus
