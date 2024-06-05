#!/bin/bash

#######################################
# Easy Consensus Tree
# by Mateusz Chojnacki, Krzysztof Łukasz, Younginn Park, Daniel Zalewski
#######################################

# Default values for options
SPECIES_LIST="species.txt"

function display_help() {
    echo "ECT - Easy Consensus Tree"
    echo "by Mateusz Chojnacki, Krzysztof Łukasz, Younginn Park, Daniel Zalewski"
    echo ""
    echo "A streamlined tool for reconstructing phylogenetic trees using whole-proteome approach."
    echo ""
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -h, --help        Show this help message"
    echo "  -i, --input    Set value for option1 (default: $SPECIES_LIST)"
    exit 0
}

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -h|--help) display_help ;;
        -i|--input) SPECIES_LIST="$2"; shift ;;
        # add other options here
        # don't forget to add to usage and help too
        *) echo "Unknown parameter passed: $1"; display_help ;;
    esac
    shift
done

# Initialize log file
log_file="log.txt"
echo "" > $log_file

# Function to print timestamped messages
function log_message() {
    local message="$1"
    local timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    local log_entry="$timestamp - $message"

    echo "$log_entry"
    echo "$log_entry" >> "$log_file"
}

log_message "Starting Easy Consensus Tree"

if [ ! -f $SPECIES_LIST ]; then
    log_message "File $SPECIES_LIST not found"
    exit 1
fi

# Activate the conda environment
CONDA_ENV="ect_env"
log_message "Activating conda environment: $CONDA_ENV"
source $(conda info --base)/etc/profile.d/conda.sh
conda activate $CONDA_ENV


#######################################
# Fetch proteomes
#######################################
log_message "Fetching proteomes from $SPECIES_LIST..."
python3 scripts/fetch_proteomes.py $SPECIES_LIST | tee -a $log_file

if [[ $? -ne 0 ]]; then
    log_message "Error: Fetching proteomes failed. Exiting."
    exit 1
fi
log_message "Fetch completed successfully."


#######################################
# Merge proteomes
#######################################
log_message "Merging proteomes..."


#######################################
# Clustering with MMseqs2
#######################################
log_message "Running MMseqs2..."



#######################################
# Filter clusters
#######################################
log_message "Filtering clusters..."


#######################################
# Run MSA
#######################################
log_message "Running MSA..."


#######################################
# Construction of gene family trees
#######################################
log_message "Constructing trees for gene families..."


#######################################
# Construction of consensus tree
#######################################
log_message "Constructing consensus tree..."


#######################################
# Tree visualization
#######################################




log_message "All completed successfully."
