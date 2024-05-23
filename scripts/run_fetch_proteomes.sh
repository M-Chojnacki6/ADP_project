#!/bin/bash

# Usage: ./run_fetch_proteomes.sh <species.txt>
# species.txt - text file with organism name or taxonomic ID

# Selected species from the article
# FILE="species.txt"

FILE=$1

# 
rm org_accs.txt
rm org_spec.txt

# Remove \r from $FILE - a problem on Windows
sed -i 's/\r//g' $FILE

while IFS="" read -r GEN || [ -n "$GEN" ]
do
    echo $GEN

    # Confirmed compatibility with NCBI datasets 16.3.0
    # Fetch reference genome accession
    ACC=$(./datasets summary genome taxon "$GEN" \
                --reference \
                --report ids_only \
                --limit 1 \
                --as-json-lines \
                | grep -Eo '"accession":"[^"]*' | grep -Eo '[^":]*$' \
                )

    # Check which organism/strain is the genome from exactly
    ORG=$(./datasets summary genome accession "$ACC" \
                --reference \
                --limit 1 \
                --as-json-lines \
                | grep -Eo '"organism_name":"[^"]*' | grep -Eo '[^":]*$' -m 1 \
                )

    # Download genome with accession $ACC
    ./datasets download genome accession $ACC \
                                --include protein

    # Overwrite Readmes and unzip quietly
    unzip -oq ncbi_dataset.zip

    # Save search results
    echo $ACC >> org_accs.txt
    echo $ORG >> org_spec.txt

done <$FILE

#
rm ncbi_dataset.zip
