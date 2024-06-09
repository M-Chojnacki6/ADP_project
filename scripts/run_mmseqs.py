#!/usr/bin/env python3

import os
import argparse
import re

def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, 
    description="""Run mmseq2 with selected parameters on merged proteomes.""")

    parser.add_argument('input',metavar= 'i',nargs=1, help="""Path to the input .fasta.gz file containing merged proteomes""")
    parser.add_argument('-msi',metavar= 'FLOAT',nargs=1,
        help="""List matches above this sequence identity (range 0.0-1.0); default 0.3""",default=0.3)

    parser.add_argument('-clusterMode',metavar='INT',type=int,nargs=1,choices=[0,1,2,3],help="""Clustering mode:\n0: Set-Cover (greedy)
1: Connected component (BLASTclust)
2,3: Greedy clustering by sequence length (CDHIT)\ndefault: 0""",default=0)
    parser.add_argument('-covMode', metavar='INT',nargs=1,type=int,choices=[0,1,2,3,4,5], help=f"""sevuence coverage mode:
0: coverage of query and target 
1: coverage of target
2: coverage of query
3: target seq. length has to be at least x percent of query length
4: query seq. length has to be at least x percent of target length
5: short seq. needs to be at least x percent of the other seq. length
default 0""",default=0)
    parser.add_argument('-c',metavar='FLOAT',nargs=1,
        help="""List matches above this fraction of aligned (covered) residues; default: 0.800""",
        default=0.800)
#    parser.add_argument('-mmseq_params', metavar ='STRING', nargs="+", # type=str,
#        help="""other parameters for mmseq2 easy-cluster, first type '-h'""",default="") # don't work


    args = parser.parse_args()
    in_file=""
    if args.input is None:
        print(f"Provide input file")
    elif not os.path.isfile(args.input[0]):
        print(f"Provide input file: {args.input[0]} doesn't exist")
    else:
        in_file=args.input[0]
        if not re.search(".+[.]fasta[.]gz$",in_file):
            print(f"Input file {in_file} not recognized as correct .fasta.gz file.")
            in_file=""
    msi=0.3
    if isinstance(args.msi,list):
        if float(args.msi[0])>=0 and float(args.msi[0])<1:
            msi=float(args.msi[0])
        else:
            print("parametr: msi = {args.msi[0]} out of range, changing to 0.3")
    c=0.8
    if isinstance(args.c,list):
        if float(args.c[0])>=0 and float(args.c[0])<1:
            c=float(args.c[0])
        else:
            print("parametr: msi = {args.c[0]} out of range, changing to 0.800")
    if isinstance(args.covMode,list):
        args.covMode=args.covMode[0]
    if isinstance(args.clusterMode,list):
        args.clusterMode=args.clusterMode[0]
#    mmseq_params=""
#    if isinstance(args.mmseq_params,list):
#        mmseq_params=args.mmseq_params[0]

    if in_file:    
        return[in_file,msi,args.clusterMode,args.covMode,c] #,mmseq_params ]
    else:
        return None


def main():
    inputs=parse_args()
    
    if not inputs is None:
        print(f"{' '*16}> Rum mmsq2 < \n\n{'#'*20}START{'#'*20}")
        print(f"\nInput file:\t\t\t{inputs[0]}\nMin seq identity:\t\t{inputs[1]}\nClustering mode:\t\t{inputs[2]}\nCoverage mode:\t\t\t{inputs[3]}\nCoverage:\t\t{inputs[4]}")
        output=inputs[0].replace(".fasta.gz","")
        if os.path.isfile(f"{output}_rep_seq.fasta"):
            os.system(f"rm {output}_rep_seq.fasta")
        if os.path.isfile(f"{output}_cluster.tsv"):
            os.system(f"rm {output}_cluster.tsv")
        if os.path.isfile(f"{output}_all_seqs.fasta"):
            os.system(f"rm {output}_all_seqs.fasta")
        print(f"Output files:\t\t\t{output} [_all_seq.fasta, _cluster.tsv]")
        os.system(f"mmseqs easy-cluster {inputs[0]} {output} working_dir/tmpDir --min-seq-id {inputs[1]} --cluster-mode {inputs[2]} --cov-mode {inputs[3]} -c {inputs[4]}")
        os.system(f"rm {output}_rep_seq.fasta")
        os.system("rm -r working_dir/tmpDir")
#        os.system(f"rm {output}_cluster.tsv")


if __name__ == "__main__":
    main()