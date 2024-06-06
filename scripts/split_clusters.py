#!/usr/bin/env python3


import argparse
import os
import re


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, 
    description="""Split results from mmseq2 clustering to different fasta files;
    Removes all clusters smaller than max(3, c*num_of_species);
    Save filtered clusters to following directories:

    > [name]/nonpara    - directory containing clusters with at most 1 sequence 
                        from each organism 

    > [name]/para       - directory containing full clustes, corresponding to clusters
                        from [name]/para, from which some sequences were omitted.
    In addition, [name]/ directiory contains two files:
     np.txt (nonparalogous, all clusters)
     p.txt  (paralogous, if cluster doesn't contain paralogous, path is the same as in pa.txt)
    containing paths to corresponding fasta files, to aviod comuting the filogenetic trees twice.

    """)

    parser.add_argument('input',metavar='i', nargs=1, help="""Path to the result 
        [name]_all_seqs.fasta file from mmseq2""", default=None)
    parser.add_argument('-c',metavar='FLOAT',nargs=1,
        help="""float value used to compute cutoff -> minimum number of sequences 
        in each cluster, should be 0 <= c < 1; default: 0.3""",
        default=0.3)
    args = parser.parse_args()
    in_file=""
    if args.input is None:
        print(f"Provide input file")
    elif not os.path.isfile(args.input[0]):
        print(f"Provide input file: {args.input[0]} doesn't exist")
    else:
        in_file=args.input[0]
        if not re.search(".+_all_seqs[.]fasta$",in_file):
            print(f"Input file {in_file} not recognized as correct [name]_all_seqs.fasta file.")
            in_file=""
    c=0.1
    if isinstance(args.c,list):
        if args.c[0]>=0 and args.c[0]<1:
            c=float(args.c[0])
        else:
            print("parametr: msi = {args.c[0]} out of range, changing to 0.800")
    if in_file:    
        return[in_file,c]
    else:
        return None

def process_clusters(clusters,output_dir,cutoff):
    np=open(f"{output_dir}/np.txt","w")
    pa=open(f"{output_dir}/p.txt","w")

    p=1
    list_npID=[]
    list_pID=[]
    list_npSEQ=[]
    list_pSEQ=[]
    with open(clusters,"r") as clust_file:
        go=False
        for line in clust_file:
            if line[0]==">" and len(line.strip().split())==1:
                if len(list_npID)>=cutoff:
                    
                    f=open(f"{output_dir}/nonpara/np_{p}_{len(list_npID)}.fasta","w")
                    if list_pID:
                        g=open(f"{output_dir}/para/pa_{p}_{len(list_npID)}.fasta","w")
                    for ids,seq in zip(list_npID,list_npSEQ):
                        f.write(f">{ids}      \n")
                        if list_pID:
                            g.write(f">{ids}      \n")
                        while len(seq)>50:
                            f.write(f"{seq[:50]}\n")
                            if list_pID:
                                g.write(f"{seq[:50]}\n")
                            seq=seq[50:]
                        if seq:
                            f.write(f"{seq}\n")
                            if list_pID:
                                g.write(f"{seq}\n")
                    f.close()
                    if list_pID:
                        for ids,seq in zip(list_pID,list_pSEQ):
                            g.write(f">{ids}     \n")
                            while len(seq)>50:
                                g.write(f"{seq[:50]}\n")
                                seq=seq[50:]
                            if seq:
                                g.write(f"{seq}\n")
                        g.close()

                    np.write(f"{output_dir}/nonpara/np_{p}_{len(list_npID)}.fasta\n")
                    if list_pID:
                        pa.write(f"{output_dir}/para/pa_{p}_{len(list_npID)}.fasta\n")
                    else:
                        pa.write(f"{output_dir}/nonpara/np_{p}_{len(list_npID)}.fasta\n")
                    p+=1
                    
                list_npID=[]
                list_pID=[]
                list_npSEQ=[]
                list_pSEQ=[]
                nr=0
            elif line[0]==">":
                line=line.strip().split()
                line=re.findall("^[0-9]+[gmr]",line[0][1:])[0]
                line=line[:len(line)-1]
                if line in list_npID:
                    go=False
                    list_pID.append(f"{line}_{nr}")
                    nr+=1
                else:
                    list_npID.append(line)
                    go=True
            else:
                
                if go:
                    list_npSEQ.append(line.strip())
                else:
                    list_pSEQ.append(line.strip())
    np.close()
    pa.close()

def main():
    inputs=parse_args()
    
    if not inputs is None:
        print(f"{' '*12}> Split clusters file < \n\n{'#'*20}START{'#'*20}")
        print(f"\nInput file:\t\t\t{inputs[0]}")
        output=inputs[0].replace("_all_seqs.fasta","")
        cutoff=max(3,int(inputs[1]*int(re.findall("[0-9]+$",output)[0])))
        print(f"cutoff\t\t\t\t{cutoff}")
        if not os.path.exists(output):
            print(f"Preparing output directory:\t{output}")
            os.mkdir(output)
        if not os.path.exists(f"{output}/nonpara"):
            print(f"Preparing nonpara directory:\t{output}/nonpara")
            os.mkdir(f"{output}/nonpara") 
        if not os.path.exists(f"{output}/para"):
            print(f"Preparing para directory:\t{output}/para")
            os.mkdir(f"{output}/para")
        print(f"Output directory:\t\t{output}")

        process_clusters(inputs[0],output,cutoff)
        



if __name__ == "__main__":
    main()
