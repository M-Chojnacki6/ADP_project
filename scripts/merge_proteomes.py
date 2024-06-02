#!/usr/bin/env python3

import Bio
from Bio import SeqIO
import os
import argparse
import re
import gzip

def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, 
    description="""Merge proteomes and unify organism ids. 
    New id format: ID[my...][gy...][ry...] 
    where:
    > ID    - index number of proteome in input file
    > my... - index number (y) of mitochondrial gene
    > gy... - name of nuclear gene (the same as in proteome)
    > ry... - index number (y) of gene not recognized as mitochondrial or nuclear""")

    parser.add_argument('input',metavar= 'i',nargs=1, help="""Path to the input TXT file containing 
        paths to selected proteomes""")
#    parser.add_argument('-o',metavar= 'o',nargs=1, help="""Directory where the proteome files will be saved;
 #        if not provided, save to ./proteome_database/""",default="./proteome_database/")

    args = parser.parse_args()
    in_file=""
    if args.input is None:
        print(f"Provide input file")
    elif not os.path.isfile(args.input[0]):
        print(f"Provide input file: {args.input[0]} doesn't exist")
    else:
        in_file=args.input[0]
        if not re.search(".+[.]paths$",in_file):
            print(f"Input file {in_file} not recognized as correct .paths file.")
            in_file=""

    if in_file:    
        return[in_file]
    else:
        return None

def process_paths(paths):
    paths_list=[]
    nr=0
    with open(paths,"r") as f:
        for line in f:
            line=os.path.normpath(line.strip())
            if os.path.isfile(line):
                paths_list.append(line.strip())
                nr+=1
            else:
                print(f"! proteome on path: {line} not found;\nomitting proteome\nuse update_database.py to remove all maualy relocated/deleted proteome files.")
                paths_list.append("")
    out_file=re.sub("[.]txt[.]",f"_merged{nr}.",re.sub("[.]paths$",".fasta.gz",paths))  # potentialy problematic line
    if os.path.isfile(out_file):
        os.system(f"rm {out_file}")
    with gzip.open(out_file,"wt") as f:
        for i,p in enumerate(paths_list):
            m=1
            r=1
            if p:
                with gzip.open(p,"rt") as handle:
                    for record in SeqIO.parse(handle, "fasta"):
                        name, sequence = record.description, str(record.seq)
                        if m and ("(mitochondrion)" in name or "mitochondrial" in name):
                            record.id=f"{i}m{m}"
                            m+=1
                        elif re.search("[A-Z][A-Z]_[0-9]+",name):
                            name=re.findall("[A-Z][A-Z]_[0-9]+",name)[0]
                            name=name.split("_")[1]
                            record.id=f"{i}g{name.replace(',','')}"
                        elif re.search("^[st][pr][|][\w]+",name):
                            name=re.findall("^[st][pr][|][\w]+",name)[0]
                            record.id=f"{i}g{name.split('|')[1]}"
                        else:
                            record.id=f"{i}r{r}"
                            r+=1
                        SeqIO.write(record, f, "fasta")
    return out_file


def main():
    inputs=parse_args()

    if not inputs is None:
        print(f"{' '*7}> Merge proteomes & unify ids < \n\n{'#'*20}START{'#'*20}")
        print(f"\nInput file:\t\t\t{inputs[0]}\n")
        paths=process_paths(inputs[0])
        print(f"found proteomes merged to file:\n{paths}")


if __name__ == "__main__":
    main()
