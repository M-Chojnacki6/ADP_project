#!/usr/bin/env python3

"""
Script Name: fetch_proteomes.py

Version: 4

Description:
Script for fetching proteomes from Uniprot or NCBI database.

Usage:
    python fetch_proteomes.py <-i species_list> [-o output_directory]

"""

import os
import argparse
import requests
import subprocess
import json
import re

taxon_library="taxon_library.csv"



def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, 
    description="""Download proteomes for species listed in a TXT file.""")

    parser.add_argument('input',metavar= 'i',nargs=1, help="""Path to the input TXT file containing 
        species names or organism IDs""")
    parser.add_argument('-o',metavar= 'o',nargs=1, help="""Directory where the proteome files will be saved;
         if not provided, save to ./proteome_database/""",default="./proteome_database/")

    args = parser.parse_args()
    in_file=""
    if args.input is None:
        print(f"Provide input file")
    elif not os.path.isfile(args.input[0]):
        print(f"Provide input file: {args.input[0]} doesn't exist")
    else:
        in_file=args.input[0]
    
    out_dir=""
    if isinstance(args.o,list):
        if os.path.dirname(args.o[0]):
            out_dir=args.o[0]
            if out_dir[-1]!="/":
                out_dir=f"{out_dir}/"
            out_dir=out_dir.replace("//","/")
        else:
            out_dir="./proteome_database/"
    else:
        out_dir=args.o
    if in_file:    
        return[in_file,out_dir]
    else:
        return None
"""
Fuction check_taxon() check, wheter given name (species name, taxon nr or Uniprot_proteomeID) is already 
in downloaded database and if is, returns Uniprot/NCBI id associated with name.

file taxon_library.csv contains data in format:

scientificName/commonName/synonymName \t taxonID \t [Uniprot/NCBI]_proteome_ID \t fasta.gz name
Homo sapiens                          \t 9606   \t UP000005640                \t ./proteome_datasets/UP000005640_9606.fasta.gz
"""

def check_taxon(name):
    with open(f"./proteome_database/{taxon_library}","r") as f:
        for line in f:
            line=line.strip().split("\t")
            if line[0].lower() ==str(name).lower() or line[0].lower().split("(")[0].strip() ==str(name).lower():
                return line[3]
            elif line[1]==str(name):
                return line[3]
            elif line[2]==name:
                return line[3] 
    return None


def get_data_from_json_NCBI(results):
    results=results.decode("utf-8").strip()
    results=json.loads(results)
    if re.match("^GCF_[0-9]+(.)*[0-9]*$",results['accession']):
        NCBIid=results['current_accession']
    else:
        NCBIid=results['paired_accession']  
    taxon=results["organism"]['tax_id']
    names=[results["organism"]['organism_name']]
    if 'common_name' in results["organism"].keys():
        names.append(results["organism"]['common_name'])
    print(f"NCBI ID: {NCBIid}\ntaxonomy ID: {taxon}\nnames: {names}")
    return [NCBIid,taxon,names]

def search_proteome_ncbi(species_name,id_type):
    output=None
    if id_type==3: 
        result = subprocess.run([f"datasets", "summary" , "genome" , "accession",f"{species_name}", "--limit", "1", "--as-json-lines" ], # 
            stdout=subprocess.PIPE)
        if result.returncode==0:
            output = get_data_from_json_NCBI(result.stdout)
        else:
            print(f"NCBI accession {species_name} not found in NCBI database")
    elif id_type==0 or id_type==1:
        result = subprocess.run([f"datasets", "summary" , "genome" , "taxon",f"{species_name}", "--limit", "1", "--as-json-lines" ], # 
            stdout=subprocess.PIPE)
        if result.returncode==0:
            output = get_data_from_json_NCBI(result.stdout)
        else:
            if id_type==0:
                print(f"name: {species_name} not found in NCBI database")
            else:
                print(f"Taxom id: {species_name} not found in NCBI database")
    else:
        result = subprocess.run([f"datasets", "summary" , "genome" , "accession",f"{species_name}", "--limit", "1", "--as-json-lines" ], # 
            stdout=subprocess.PIPE)
        if result.returncode==0:
            output = get_data_from_json_NCBI(result.stdout)
        else:
            result = subprocess.run([f"datasets", "summary" , "genome" , "taxon",f"{species_name}", "--limit", "1", "--as-json-lines" ], # 
                stdout=subprocess.PIPE)
            if result.returncode==0:
                output = get_data_from_json_NCBI(result.stdout)
            else:
                print(f"name {species_name} not found in NCBI database")
    return output

def fetch_proteome_ncbi(proteome_id,taxon,names, output_directory):
    result = subprocess.run([f"datasets", "download" , "genome" , "accession",f"{proteome_id}", "--filename",
     f"{output_directory}tmp.zip", "--include", "protein" ], stdout=subprocess.PIPE)
    if result.returncode==0:
        os.system(f"unzip {output_directory}tmp.zip -d {output_directory}tmp")
        os.system(f"mv {output_directory}tmp/ncbi_dataset/data/{proteome_id}/protein.faa {output_directory}{proteome_id.replace('.','_')}.fasta")
        os.system(f"gzip {output_directory}{proteome_id.replace('.','_')}.fasta")
        os.system(f"rm -r {output_directory}tmp")
        os.system(f"rm {output_directory}tmp.zip")
        for name in names:
            print(f"actualising libraru file with name '{name}'")
            os.system(f"""echo "{name}\t{taxon}\t{proteome_id}\t{output_directory}{proteome_id.replace('.','_')}.fasta.gz" >> {output_directory}{taxon_library}""")
        return proteome_id.replace('.','_')
    else:
        print(f"NCBI accession {proteome_id} not found in NCBI database")
    return None


"""
Searches for the proteome of a species in UniProt and returns the ID.
"""
def get_data_from_json_UniProt(response):
    UPid=response["id"]
    taxon=response["taxonomy"]["taxonId"]
    names=[response["taxonomy"]["scientificName"]]
    if "commonName" in response["taxonomy"].keys():
        names.append(response["taxonomy"]["commonName"])
    if "synonyms" in response["taxonomy"].keys():
        names+=response["taxonomy"]["synonyms"]
    print(f"UniProt ID: {UPid}\ntaxonomy ID: {taxon}\nnames: {names}")
    return [UPid,taxon,names]


def search_proteome_uniprot(species_name,id_type):
    if id_type==2 or id_type==1:
        url=f"https://rest.uniprot.org/proteomes/stream?format=json&query=%28{species_name}%29+AND+%28proteome_type%3A1%29"
    else:
        url = f"https://rest.uniprot.org/proteomes/stream?format=json&query=%28{species_name.replace(' ','+')}%29+AND+%28proteome_type%3A1%29"
    response = requests.get(url)
    check_whole=True
    if response.status_code == 200:
        lines = response.json()['results']
        if len(lines):
            check_whole=False
            if id_type:
                r=get_data_from_json_UniProt(lines[0])
                r.append(1)
                return r
            else:
                if not "virus" in species_name and "virus" in lines[0]["taxonomy"]["scientificName"]:
                    if species_name==lines[0]["taxonomy"]["mnemonic"]:
                        r=get_data_from_json_UniProt(lines[0])
                        r.append(1)
                        return r
                    else:
                        print(f"{lines[0]['taxonomy']}")
                else:

                    r=get_data_from_json_UniProt(lines[0])
                    r.append(1)
                    return r
                    
    if check_whole:
        print(f"\n! Species {species_name} not found in UniProt - Refererence proteomes;\nChecking in whole UniProt Proteome...")
        if id_type==1:
            url = f"https://rest.uniprot.org/proteomes/stream?format=json&query=upid%3A{species_name}"
        elif id_type==2:
            url=f"https://rest.uniprot.org/proteomes/stream?format=json&query=%28{species_name}%29"
        else:
            url = f"https://rest.uniprot.org/proteomes/stream?format=json&query=%28{species_name.replace(' ','+')}%29"
        response = requests.get(url)
        if response.status_code == 200:
            lines = response.json()['results']
            if len(lines):
                if id_type:
                    r=get_data_from_json_UniProt(lines[0])
                    r.append(0)
                    r.append(lines[0]['genomeAssembly']['assemblyId'])
                    return r
                else:
                    if not "virus" in species_name and "virus" in lines[0]["taxonomy"]["scientificName"]:
                        if species_name==lines[0]["taxonomy"]["mnemonic"]:
                            print(f"type= {id_type}\tmnemonic\n{lines}")
                            r=get_data_from_json_UniProt(lines[0])
                            r.append(0)
                            r.append(lines[0]['genomeAssembly']['assemblyId'])
                            return r
                        else:
                            print(f"the most similar record in UniProt: {lines[0]['taxonomy']}")
                    else:
                        print(f"type= {id_type}\n{lines[0].keys()}")
                        r=get_data_from_json_UniProt(lines[0])
                        r.append(0)
                        r.append(lines[0]['genomeAssembly']['assemblyId'])
                        return r
    return None

def clasify_id(name):
    if re.match("^UP[0-9]+",name):
        return 1
    elif re.match("^[0-9]+$",name):
        return 2
    elif re.match("^(GCF)|(GCA)_[0-9]+[.]*[0-9]*$",name):
        return 3
    elif " " in name:
        return 0
    print(f"Ambiguous name (potentially mnemonic name or unsupported abbreviation from NCBI): {name}")
    return 4

def DownloadFile(url,directory):
    local_filename = url.split('/')[-1]
    r = requests.get(url)
    f = open(f"{directory}{local_filename}", 'wb')
    for chunk in r.iter_content(chunk_size=512 * 1024): 
        if chunk:
            f.write(chunk)
    f.close()
    return local_filename


"""
Function fetch_proteome_uniprot() fetches the proteome data from UniProt and saves it to a file in selected 
directory.
"""

def fetch_proteome_uniprot(proteome_id,taxon,names, output_directory):
    domens=["Archaea","Bacteria","Eukaryota","Viruses"]
    for dom in domens:
        url = f"https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/reference_proteomes/{dom}/{proteome_id}/{proteome_id}_{taxon}.fasta.gz"
        response = requests.get(url)
        if response.status_code == 200:
            ln = DownloadFile(url,output_directory)

            for name in names:
                print(f"actualising libraru file with name '{name}'")
                os.system(f"echo '{name}\t{taxon}\t{proteome_id}\t{output_directory}{ln}' >> {output_directory}{taxon_library}")
            return ln

        elif response.status_code != 200 and dom=="Viruses":
            print(f"Error fetching proteome {proteome_id} from UniProt: {response.status_code}")
    return None

def process_by_name(input_txt, output_directory):
    names_list=[]
    with open(input_txt, 'r') as txtfile:
        for line in txtfile:
            names_list.append(line.strip())
    paths_to_proteomes=[]
    for species in names_list:
        print(f"\nProcessing {species}...")
        check_tmp=check_taxon(species)
        if check_tmp:
            paths_to_proteomes.append(check_tmp)
            print("Found in local database!")
        else:
            found=False
            id_type=clasify_id(species)
            proteome=None
            if id_type!=3:
                print("searching in UniProt ...")
                proteome = search_proteome_uniprot(species,id_type)
                if not proteome is None:
                    check_tmp=check_taxon(proteome[1])
                    if check_tmp is None:
                        if proteome[3]:
                            ln=fetch_proteome_uniprot(proteome[0],proteome[1],proteome[2], output_directory)
                            if ln:
                                print(f"Proteome for {species} saved as {output_directory}{ln}")
                                paths_to_proteomes.append(f"{output_directory}{ln}")
                                found=True
                            else:
                                print(f"No matching proteome found for {species} in UniProt Proteomes")
                    else:
                        found=True
                        print("Found in local database!")
                        paths_to_proteomes.append(check_tmp)                        
                else:
                    print(f"No matching proteome found for {species} in UniProt Proteomes")          
            if not found:
                proteomeNCBI=None
                if proteome is None:
                    print("searching in NCBI ...")
                    if id_type!=1:
                        proteomeNCBI = search_proteome_ncbi(species,id_type)
                elif not proteome[3]:
                    proteomeNCBI = search_proteome_ncbi(proteome[4],3)
                    proteomeNCBI[2]=list(set(proteome[2]+proteomeNCBI[2]))

                print(f"\nproteome from NCBI: {proteomeNCBI}\n")
                if not proteomeNCBI is None:
                    check_tmp=check_taxon(proteomeNCBI[1])
                    if check_tmp is None:
                        ln=fetch_proteome_ncbi(proteomeNCBI[0],proteomeNCBI[1],proteomeNCBI[2], output_directory)
                        if ln:
                            print(f"Proteome for {species} saved as {output_directory}{ln}")
                            paths_to_proteomes.append(f"{output_directory}{ln}")
                        else:
                           paths_to_proteomes.append("")
                    else:
                        print("Found in local database!")
                        paths_to_proteomes.append(check_tmp)
                else:
                    paths_to_proteomes.append("")

    return paths_to_proteomes


def main():
    inputs=parse_args()

    if not os.path.exists("proteome_database/"):
        os.system("mkdir -p proteome_database")
        print(f"preparing database directory: ./proteome_database")
        
    if not os.path.exists("working_dir/"):
        os.system("mkdir -p working_dir")
        print(f"preparing working directory: ./working_dir")
        
    if not os.path.isfile(f"proteome_database/{taxon_library}"):
        os.system(f"echo -n '' > proteome_database/{taxon_library}")
        print(f"preparing library for species names/taxonomy IDs/Uniprot IDs/NCBI IDs: ./proteome_database/{taxon_library}")

    if not inputs is None:
        print(f"{' '*13}> Fetch proteomes < \n\n{'#'*20}START{'#'*20}")
        print(f"\nInput file:\t\t\t{inputs[0]}\nOutput directory:\t\t{inputs[1]}\n")
        paths=process_by_name(inputs[0], inputs[1])
        with open(f"{inputs[0]}.paths","w") as f:
            for p in paths:
                print(p)
                f.write(f"{p}\n")

if __name__ == "__main__":
    main()
