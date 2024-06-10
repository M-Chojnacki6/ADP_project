import os
import argparse
import requests
import subprocess
import json
import re
from fetch_proteomes import clasify_id, search_proteome_uniprot, search_proteome_ncbi, check_taxon

taxon_library="taxon_library.csv"



def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, 
    description="""Remove proteomes for species listed in a TXT file.""")

    parser.add_argument('input',metavar= 'i',nargs=1, help="""Path to the input TXT file containing 
        species names or organism IDs""")
    parser.add_argument('-l',metavar= 'l',nargs=1, help=f"""Path to the itaxon_library.csv containing 
        informations about downloaded proteomes. Default = ./ECT/proteome_database/{taxon_library}""",
        default=f"./ECT/proteome_database/{taxon_library}")


    args = parser.parse_args()
    in_file=""
    if args.input is None:
        print(f"Provide input file")
    elif not os.path.isfile(args.input[0]):
        print(f"Provide input file: {args.input[0]} doesn't exist")
    else:
        in_file=args.input[0]
    library=""
    if isinstance(args.l,list):
        if os.path.isfile(args.l[0]):
            library=args.l[0]
        else:
            library=f"./ECT/proteome_database/{taxon_library}"
    else:
        library=f"./ECT/proteome_database/{taxon_library}"
    if in_file:    
        return [in_file,library]
    else:
        return None

def delete_path(paths,library):
    result = subprocess.run(['grep', f'{paths}' , library],
        stdout=subprocess.PIPE)
    if result.returncode==0:
        result=result.stdout.decode("utf-8").strip()
        os.system(f"echo '{result}' >> {library}")
        os.system(f"sort {library} | uniq -u > {library}.tmp")
        os.system(f"cat {library}.tmp > {library}")
        os.system(f"rm {library}.tmp")
        result=result.split()[-1].strip()
        print(f">>> removing file {result}\nDONE!")
        os.system(f"rm {paths}")
        return False
    return True

def delete_ids(input_txt,library):
    names_list=[]
    with open(input_txt, 'r') as txtfile:
        for line in txtfile:
            names_list.append(line.strip())
    for species in names_list:
        print(f"\nRemoving {species}...")
        id_type=clasify_id(species)
        check_tmp=check_taxon(species)
        res=True
        if check_tmp:
            res=delete_path(check_tmp,library)
        else:
            print(f"name: {species} not found in library, checking UniProt Proteomes")
            proteome=search_proteome_uniprot(species,id_type)
            if not proteome is None:
                check_tmp=check_taxon(proteome[1])
                if check_tmp:
                    res=delete_path(check_tmp,library)
            elif id_type!=1:
                print(f"name: {species} not found in library and UniProt Proteomes, checking in NCBI")
                proteome = search_proteome_ncbi(species,id_type)
            if not proteome is None:
                check_tmp=check_taxon(proteome[1])
                if check_tmp:
                    res=delete_path(check_tmp,library)
        if res:
            print(f"FAILED: cannot found organism in {library}\n-> organism {species} has been probably already removed")













def main():
    inputs=parse_args()

    if not inputs is None:
        print(f"{' '*13}> Remove proteomes < \n\n{'#'*20}START{'#'*20}")
        print(f"\nInput file:\t\t{inputs[0]}\nLibrary file:\t\t{inputs[1]}\n")
        delete_ids(inputs[0],inputs[1])

if __name__ == "__main__":
    main()
