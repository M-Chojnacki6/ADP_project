import os
import argparse
import subprocess

taxon_library = "taxon_library.csv"

def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, 
    description=f"""Update information in {taxon_library}.
    This script removes all lines in the local library file containing paths leading to nonexisting fasta.gz files""")
    parser.add_argument('-l', metavar='l', nargs=1, help=f"""Path to the taxon_library.csv containing 
        information about downloaded proteomes. Default = ./ECT/proteome_database/{taxon_library}""",
        default=f"./ECT/proteome_database/{taxon_library}")

    args = parser.parse_args()
    if isinstance(args.l, list):
        if os.path.isfile(args.l[0]):
            library = args.l[0]
        else:
            library = f"./ECT/proteome_database/{taxon_library}"
    else:
        library = f"./ECT/proteome_database/{taxon_library}"
    
    if os.path.isfile(library):
        return [library]
    else:
        print(f"Error: The specified library file '{library}' does not exist.")
        return None

def delete_path_lib(paths, library):
    result = subprocess.run(['grep', f'{paths}', library], stdout=subprocess.PIPE)
    if result.returncode == 0:
        result = result.stdout.decode("utf-8").strip()
        os.system(f"echo '{result}' >> {library}")
        os.system(f"sort {library} | uniq -u > {library}.tmp")
        os.system(f"cat {library}.tmp > {library}")
        os.system(f"rm {library}.tmp")
        result = result.split()[-1].strip()
        print(f">>> removing file {result} from library\nDONE!")
        return False
    return True

def find_ids(library):
    names_list = []
    with open(library, 'r') as txtfile:
        for line in txtfile:
            linet = line.strip().split("\t")[-1]
            if not os.path.isfile(linet) and linet not in names_list:
                print(f"Cannot find file: {linet} : corresponding paths in library will be removed")
                res = delete_path_lib(linet, library)
                if res:
                    print(f"FAILED: cannot find path in {library}\n-> path has probably already been removed")

def main():
    inputs = parse_args()

    if inputs is not None:
        print(f"{' '*13}> Update library < \n\n{'#'*20}START{'#'*20}")
        print(f"\nLibrary file:\t\t{inputs[0]}\n")
        find_ids(inputs[0])

if __name__ == "__main__":
    main()