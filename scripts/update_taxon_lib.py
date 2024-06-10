import os
import argparse
import re
from remove_proteomes import delete_path

taxon_library=os.path.join("taxon_library.csv")



def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, 
    description=f"""Update information in {taxon_library}.""")
    parser.add_argument('-l',metavar= 'l',nargs=1, help=f"""Path to the itaxon_library.csv containing 
        informations about downloaded proteomes. Default = ./ECT/proteome_database/{taxon_library}""",
        default=f"./ECT/proteome_database/{taxon_library}")


    args = parser.parse_args()
    if isinstance(args.l,list):
        if os.path.isfile(args.l[0]):
            library=args.l[0]
        else:
            library=f"./ECT/proteome_database/{taxon_library}"
    else:
        library=f"./ECT/proteome_database/{taxon_library}"
    if library:    
        return [library]
    else:
        return None

def find_ids(library):
    names_list=[]
    with open(library, 'r') as txtfile:
        for line in txtfile:
            linet=line.strip().split("\t")[-1]
            if not os.path.isfile(linet) and not linet in names_list:
                print(f"Cannot find file: {linet} : corresponding paths in library will be removed")
                names_list.append(line)
    for species in names_list:
        print(f"\nRemoving {species}...")
        res=delete_path(species,library)
        if res:
            print(f"FAILED: cannot found organism in {library}\n-> organism {species} has been probably already removed")

def main():
    inputs=parse_args()

    if not inputs is None:
        print(f"{' '*13}> Update library < \n\n{'#'*20}START{'#'*20}")
        print(f"\nLibrary file:\t\t{inputs[0]}\n")
        find_ids(inputs[0])


if __name__ == "__main__":
    main()
