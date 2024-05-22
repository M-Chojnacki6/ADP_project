#uniprot ID dziala dobrze, reszta chyba poprawic URL trzeba, nie wiem co z tym emailem




import argparse
import requests
from Bio import Entrez
from Bio import SeqIO

Entrez.email = "danil.zalewski@gmail.com"

def read_species_from_txt(filename):
    """Reads species names from a TXT file."""
    species_list = []
    with open(filename, 'r') as txtfile:
        for line in txtfile:
            species_list.append(line.strip())
    return species_list

def read_ids_from_txt(filename):
    """Reads organism IDs from a TXT file."""
    id_list = []
    with open(filename, 'r') as txtfile:
        for line in txtfile:
            id_list.append(line.strip())
    return id_list

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

def search_proteome_uniprot(species_name):
    """Searches for the proteome of a species in UniProt and returns the ID."""
    url = f"https://rest.uniprot.org/uniprotkb/stream?format=fasta&query=%28%28proteome%3A{species_name}%29%29"
    response = requests.get(url)
    if response.status_code == 200:
        lines = response.text.splitlines()
        if len(lines) > 1:
            return lines[1].split('\t')[0]
    print(f"Error searching for {species_name} in UniProt: {response.status_code}")
    return None

def fetch_proteome_uniprot(proteome_id, output_filename):
    """Fetches the proteome data from UniProt and saves it to a file."""
    url = f"https://rest.uniprot.org/uniprotkb/stream?format=fasta&query=%28%28proteome%3A{proteome_id}%29%29"
    response = requests.get(url)
    if response.status_code == 200:
        with open(output_filename, "w") as out_handle:
            out_handle.write(response.text)
    else:
        print(f"Error fetching proteome {proteome_id} from UniProt: {response.status_code}")

def process_by_species(input_txt, output_directory, database):
    species_list = read_species_from_txt(input_txt)
    for species in species_list:
        print(f"Processing {species}...")
        if database == 0:
            proteome_id = search_proteome_ncbi(species)
            fetch_proteome_func = fetch_proteome_ncbi
        elif database == 1:
            proteome_id = search_proteome_uniprot(species)
            fetch_proteome_func = fetch_proteome_uniprot
        if proteome_id:
            output_filename = f"{output_directory}/{species.replace(' ', '_')}_proteome.gb" if database == 0 else f"{output_directory}/{species.replace(' ', '_')}_proteome.fasta"
            fetch_proteome_func(proteome_id, output_filename)
            print(f"Proteome for {species} saved as {output_filename}")
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download proteomes for species listed in a TXT file.')
    parser.add_argument('input_txt', help='Path to the input TXT file containing species names or organism IDs')
    parser.add_argument('output_directory', help='Directory where the proteome files will be saved')
    parser.add_argument('-t', type=int, choices=[0, 1], required=True, help='Type of input file: 0 for species names, 1 for organism IDs')
    parser.add_argument('-d', type=int, choices=[0, 1], required=True, help='Database to use: 0 for NCBI, 1 for UniProt')

    args = parser.parse_args()
    
    if args.t == 0:
        process_by_species(args.input_txt, args.output_directory, args.d)
    elif args.t == 1:
        process_by_id(args.input_txt, args.output_directory, args.d)
