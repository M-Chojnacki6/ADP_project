#!/usr/bin/env python3

import os
import subprocess
import argparse
import re
from Bio import AlignIO

def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, 
    description="""Make multiple sequence alignment of file/files in selected .txt file, 
    using one of following alghotitm: Muscle, ClustalW, Mafft;
    Output format: .aln (clustal)""")
    parser.add_argument('input', type=str, nargs=1, help="""Path to the input fasta file 
        or .txt file containing paths to fasta files""", default=None)
    parser.add_argument('-mode',metavar='INT',type=int,nargs=1,choices=[0,1,2],help="""Algorithm used to MSA: 
        0 - ClustalW (default); 1 - Muscle; 2 - Mafft;""",default=0)
    args = parser.parse_args()
    in_file=""
    if args.input is None:
        print(f"Provide input file")
    elif not os.path.isfile(args.input[0]):
        print(f"Provide input file: {args.input[0]} doesn't exist")
    else:
        in_file=args.input[0]
        if re.search(".+[.]txt",in_file):
            is_file=False
        elif re.search(".+[.]fasta",in_file):
            is_file=True

        else:
            print(f"Input file {in_file} not recognized as correct [name]_all_seqs.fasta file.")
            in_file=""
    if isinstance(args.mode,list):
        args.mode=args.mode[0]
    if in_file:    
        return[in_file,is_file,args.mode]
    else:
        return None

def process_fasta2MSA(input_file,is_fasta,mode):
    fasta_list=[]
    if is_fasta:
        fasta_list.append(input_file)
    else:
        with open(input_file,"r") as f:
            for line in f:
                fasta_list.append(line.strip())
    for p,path in enumerate(fasta_list):
        if mode==0:
            result = subprocess.run([f"clustalw", f"{path}" , "-align" ],
                stdout=subprocess.PIPE)
            if result.returncode==0:
                print(f"ClustaW progress:\t{p+1}/{len(fasta_list)}")
                os.system(f"rm {path.replace('.fasta','.dnd')}")
            else:
                print(f"ClustaW error!!! {p+1}/{len(fasta_list)}")
        elif mode==1:
            result = subprocess.run([f"muscle", "-align",f"{path}", "-output", f"{path.replace('.fasta','.afa')}" ], 
                capture_output=True)
            if result.returncode==0:
                print(f"Muscle progress:\t{p+1}/{len(fasta_list)}")
                with open(path.replace('.fasta','.afa'),"r") as aln:
                    alignments = AlignIO.parse(aln, "fasta")
                    out=open(path.replace('.fasta','.aln'),"w")
                    AlignIO.write(alignments, out, "clustal")
                    out.close()
                os.system(f"rm {path.replace('.fasta','.afa')}")
            else:
                print(f"Muscle error!!! {p+1}/{len(fasta_list)}")
        else:
            result = subprocess.run(f"mafft --auto --clustalout {path} > {path.replace('.fasta','.aln')}", 
                shell=True,capture_output=True)
            if result.returncode==0:
                print(f"Mafft progress:\t{p+1}/{len(fasta_list)}")
            else:
                print(f"Mafft error!!! {p+1}/{len(fasta_list)}")  

def main():
    inputs=parse_args()
    if not inputs is None:
        print(f"{' '*17}> Make MSA < \n\n{'#'*20}START{'#'*20}")
        print(f"\nInput file:\t\t{inputs[0]}\nis single fasta:\t{inputs[1]}\nmode:\t\t\t{inputs[2]}")
        process_fasta2MSA(inputs[0],inputs[1],inputs[2])

if __name__ == "__main__":
    main()