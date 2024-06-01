#!/bin/bash

# A simple wrapper for MMseqs2
# Usage: run_mmseqs.sh <input_file FASTA> <min_seq_id FLOAT>

# Remove any previous output
# The only needed output
rm clstrs_mmseqs_cluster.tsv

# Fasta file with sequences to cluster (FASTA)
FASTA=$1
# Minimum sequence identity (Float: 0-1)
MINSEQID=$2

mmseqs easy-cluster "$FASTA" clstrs_mmseqs tmp --min-seq-id $MINSEQID
if [[ $? -ne 0 ]]; then
    exit 2
fi

rm clstrs_mmseqs_all_seqs.fasta
rm clstrs_mmseqs_rep_seq.fasta
rm -r tmp
