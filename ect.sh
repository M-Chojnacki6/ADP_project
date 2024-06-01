#!/bin/bash

#######################################
# Easy Consensus Tree
# by Mateusz Chojnacki, Krzysztof Łukasz, Younginn Park, Daniel Zalewski
#######################################

# Default values for options
OPTION1="default_value1"

function display_help() {
    echo "ECT - Easy Consensus Tree"
    echo "by Mateusz Chojnacki, Krzysztof Łukasz, Younginn Park, Daniel Zalewski"
    echo ""
    echo "A streamlined tool for reconstructing genome-based phylogenetic trees."
    echo ""
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -h, --help        Show this help message"
    echo "  -o1, --option1    Set value for option1 (default: $OPTION1)"
    exit 0
}

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -h|--help) display_help ;;
        -o1|--option1) OPTION1="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; display_help ;;
    esac
    shift
done

# Function to print timestamped messages
function log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Activate the conda environment
CONDA_ENV="ect_env"
log_message "Activating conda environment: $CONDA_ENV"
source $(conda info --base)/etc/profile.d/conda.sh
conda activate $CONDA_ENV


#######################################
# Fetch proteomes
#######################################
log_message "Running $SCRIPT with options: $OPTION1"
python scripts/fetch_proteomes.py $OPTION1
if [[ $? -ne 0 ]]; then
    log_message "Error: $SCRIPT failed. Exiting."
    exit 1
fi
log_message "$SCRIPT completed successfully."


#######################################
# Clustering with MMseqs2
#######################################
log_message "Running MMseqs2 with min-seq-id: $MINSEQID"
scripts/run_mmseqs.sh $FASTA $MINSEQID
if [[ $? -ne 0 ]]; then
    log_message "Error: MMseqs2 failed. Exiting."
    exit 1
fi
log_message "Clustering completed successfully."


#######################################
# Filter clusters
#######################################



#######################################
# Construction of gene family trees
#######################################



#######################################
# Construction of consensus tree
#######################################



#######################################
# Tree visualization
#######################################




log_message "All completed successfully."
