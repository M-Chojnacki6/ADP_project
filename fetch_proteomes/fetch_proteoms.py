import os
import argparse
import requests
from Bio import Entrez
from Bio import SeqIO
import re

Entrez.email = "danil.zalewski@gmail.com"
taxa_library="taxa_library.csv"



def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, 
    description="""Download proteomes for species listed in a TXT file.""")

    parser.add_argument('input',metavar= 'i',nargs=1, help="""Path to the input TXT file containing 
        species names or organism IDs""")
    parser.add_argument('-o',metavar= 'o',nargs=1, help="""Directory where the proteome files will be saved;
         if not provided, save to ./proteom_database/""",default="./proteom_database/")
    parser.add_argument('-d',metavar= 'd', type=int, choices=[0, 1], required=True, help="""Database to use: 
        0 for NCBI, 1 for UniProt""")

    args = parser.parse_args()
    print(args)
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
            out_dir="./proteom_database/"
    else:
        out_dir=args.o
    if in_file:    
        return[in_file,out_dir,args.d]
    else:
        return None
"""
Fuction check_taxa() check, wheter given name (species name, taxa nr or Uniprot_proteomeID) is already 
in downloaded database and if is, returns Uniprot/NCBI id associated with name.

file taxa_library.csv contains data in format:

scientificName/commonName/synonymName \t taxaID \t [Uniprot/NCBI]_proteome_ID \t fasta.gz name

"""

def check_taxa(name):
    with open(f"./proteom_database/{taxa_library}","r") as f:
     for line in f:
        line=line.strip().split("\t")
        if line[0]==name:
            return line[3]
        elif int(line[1])==int(name):
            return line[3]
        elif line[2]==name: 
            return line[3] 
    return None


#def read_species_from_txt(filename):
#    """Reads species names from a TXT file."""
#    species_list = []
#    with open(filename, 'r') as txtfile:
#        for line in txtfile:
#            ## testing format of the name ???
#            species_list.append(line.strip())
#    return species_list

#def read_ids_from_txt(filename):
#    """Reads organism IDs from a TXT file."""
#    id_list = []
#    with open(filename, 'r') as txtfile:
#        for line in txtfile:
#            id_list.append(line.strip())
#    return id_list

def search_proteome_ncbi(species_name):
    """Searches for the proteome of a species in NCBI and returns the ID."""
    handle = Entrez.esearch(db="protein", term=f"{species_name}[Organism] AND proteome[filter]", retmax=1)
    record = Entrez.read(handle)
    handle.close()
    if record["IdList"]:
        return record["IdList"][0]
    else:
        return None

def fetch_proteome_ncbi(proteome_id, output_filename):
    """Fetches the proteome data from NCBI and saves it to a file."""
    handle = Entrez.efetch(db="protein", id=proteome_id, rettype="gb", retmode="text")
    with open(output_filename, "w") as out_handle:
        out_handle.write(handle.read())
    handle.close()



#TODO
## !!! function, which delete proteomes and updates taxa_lbrary.csv


"""
Searches for the proteome of a species in UniProt and returns the ID.
"""
def get_data_from_json(response):
    UPid=response["id"]
    taxa=response["taxonomy"]["taxonId"]
    names=[response["taxonomy"]["scientificName"]]
    if "commonName" in response["taxonomy"].keys():
        names.append(response["taxonomy"]["commonName"])
    if "synonyms" in response["taxonomy"].keys():
        names+=response["taxonomy"]["synonyms"]
    print(f"UniprotI: {UPid}\ntaksonomy ID: {taxa}\nnames: {names}")
    return [UPid,taxa,names]


def search_proteome_uniprot(species_name):
    id_type=clasify_id(species_name)
    if id_type==1:
        url = f"https://rest.uniprot.org/proteomes/stream?format=json&query=upid%3A{species_name}"
    elif id_type==2:
        url=f"https://rest.uniprot.org/proteomes/stream?format=json&query=%28{species_name}%29+AND+%28proteome_type%3A1%29"
    else:
        url = f"https://rest.uniprot.org/proteomes/stream?format=json&query=%28{species_name.replace(' ','+')}%29+AND+%28proteome_type%3A1%29"
#    print(f"\nurl = {url}")
    response = requests.get(url)
    if response.status_code == 200:
        lines = response.json()['results']
        if len(lines):
            return get_data_from_json(lines[0])
    #        print(lines["taxonomy"])
#            UPid=lines["id"]
#            taxa=lines["taxonomy"]["taxonId"]
#            names=[lines["taxonomy"]["scientificName"]]
#            if "commonName" in lines["taxonomy"].keys():
#                names.append(lines["taxonomy"]["commonName"])
#            if "synonyms" in lines["taxonomy"].keys():
#                names+=lines["taxonomy"]["synonyms"]
#            print(f"UniprotI: {UPid}\ntaksonomy ID: {taxa}\nnames: {names}")
#            return [UPid,taxa,names]
        else:
            print(f"Species {species_name} not found in UniProt - Refererence proteomes;\nChecking in whole UniProt Proteome")
            if id_type==2:
                url=f"https://rest.uniprot.org/proteomes/stream?format=json&query=%28{species_name}%29"
            else:
                url = f"https://rest.uniprot.org/proteomes/stream?format=json&query=%28{species_name.replace(' ','+')}%29"
            response = requests.get(url)
            if response.status_code == 200:
                lines = response.json()['results']
                if len(lines):
                    return get_data_from_json(lines[0]) 
    
    print(f"Error searching for {species_name} in UniProt: {response.status_code}")
    print(f"Please check, whether species anme is correct and whether proteome for this species exists in Uniprot/NCBI")
    return None
"""
https://rest.uniprot.org/proteomes/stream?format=json&query=%28Ipomoea+nil%29
https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/reference_proteomes/Eukaryota/UP000243839/UP000243839_35883.fasta.gz
https://rest.uniprot.org/proteomes/stream?format=json&query=%28*%29+AND+%28proteome_type%3A1%29
https://www.uniprot.org/proteomes/{UPid}
https://rest.uniprot.org/proteomes/stream?format=json&query=%281566351%29+AND+%28proteome_type%3A1%29
https://rest.uniprot.org/proteomes/stream?format=json&query=upid%3AUP000000355
"""
def clasify_id(name):
    if re.match("^UP[0-9]+",name):
        return 1
    elif re.match("^[0-9]+$",name):
        return 2
    return 0

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

def fetch_proteome_uniprot(proteome_id,taxa,names, output_directory):
    domens=["Archaea","Bacteria","Eukaryota","Viruses"]
    for dom in domens:
        url = f"https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/reference_proteomes/{dom}/{proteome_id}/{proteome_id}_{taxa}.fasta.gz"
        response = requests.get(url)
        if response.status_code == 200:
            ln = DownloadFile(url,output_directory)

            for name in names:
                print(f"actualising libraru file with name '{name}'")
                os.system(f"echo '{name}\t{taxa}\t{proteome_id}\t{output_directory}{ln}' >> {output_directory}{taxa_library}")
            return ln

        elif response.status_code != 200 and dom=="Viruses":
            print(f"Error fetching proteome {proteome_id} from UniProt: {response.status_code}")

def process_by_name(input_txt, output_directory, database):
    names_list=[]
    with open(input_txt, 'r') as txtfile:
        for line in txtfile:
            names_list.append(line.strip())
    for species in names_list:
        print(f"\nProcessing {species}...")
        if database == 0:
            proteome = search_proteome_ncbi(species)
            fetch_proteome_func = fetch_proteome_ncbi
        elif database == 1:
            proteome = search_proteome_uniprot(species)
            fetch_proteome_func = fetch_proteome_uniprot
    if check_taxa(proteome[1]) is None:
        if proteome:
            ln=fetch_proteome_func(proteome[0],proteome[1],proteome[2], output_directory)
            print(f"Proteome for {species} saved as {output_directory}{ln}")
        else:
            print(f"No proteome found for {species}")

def process_by_species(input_txt, output_directory, database):
    species_list = read_species_from_txt(input_txt)
    for species in species_list:
        print(f"\nProcessing {species}...")
        if database == 0:
            proteome = search_proteome_ncbi(species)
            fetch_proteome_func = fetch_proteome_ncbi
        elif database == 1:
            proteome = search_proteome_uniprot(species)
            fetch_proteome_func = fetch_proteome_uniprot
        if check_taxa(proteome[1]) is None:
            if proteome:
                ln=fetch_proteome_func(proteome[0],proteome[1],proteome[2], output_directory)
                print(f"Proteome for {species} saved as {output_directory}{ln}")
            else:
                print(f"No proteome found for {species}")

def process_by_id(input_txt, output_directory, database):
    id_list = read_ids_from_txt(input_txt)
    for org_id in id_list:
        print(f"Processing ID {org_id}...")
        output_filename = f"{output_directory}/{org_id}_proteome.gb" if database == 0 else f"{output_directory}/{org_id}_proteome.fasta"
        if database == 0:
            fetch_proteome_ncbi(org_id, output_filename)
        elif database == 1:
            fetch_proteome_uniprot(org_id, output_filename)
        print(f"Proteome for ID {org_id} saved as {output_filename}")

def main():
    inputs=parse_args()
    if not os.path.exists("proteom_database/"):
        os.system("mkdir proteom_database")
        print(f"preparing database directory: ./proteom_database")

    if not os.path.isfile(f"proteom_database/{taxa_library}"):
        os.system(f"echo -n '' > proteom_database/{taxa_library}")
        print(f"preparing library for species names/taxonomy IDs/Uniprot IDs/NCBI IDs: ./proteom_database/{taxa_library}")

    if not inputs is None:
        print(f"{' '*13}> Fetch proteomes < \n\n{'#'*20}START{'#'*20}")
        print(f"\nInput file:\t\t\t{inputs[0]}\nOutput directory:\t\t{inputs[1]}\ndatabase:\t\t\t{inputs[2]}")
        process_by_name(inputs[0], inputs[1], inputs[2]) 
#        if inputs[3]:
#            process_by_id(inputs[0], inputs[1], inputs[2])
#        else:
#            process_by_species(inputs[0], inputs[1], inputs[2])

if __name__ == "__main__":
    main()