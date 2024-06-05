#!/bin/bash

#######################################
# Easy Consensus Tree
# by Mateusz Chojnacki, Krzysztof Łukasz, Younginn Park, Daniel Zalewski
#######################################

# Define absolute paths
THIS_SCRIPT_PATH=$(realpath "$0")
PROJECT_DIR=$(dirname $THIS_SCRIPT_PATH) # ECT
CURRENT_DIR=$(pwd) # wherever the user is, safety valve

SPECIES_LIST=$CURRENT_DIR/species.txt

function display_help() {
    echo "ECT"
    echo "by Mateusz Chojnacki, Krzysztof Łukasz, Younginn Park, Daniel Zalewski"
    echo ""
    echo "A streamlined tool for reconstructing phylogenetic trees using whole-proteome approach."
    echo ""
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -i, --input    Set value for option1 (default: species.txt)"
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
log_file=$CURRENT_DIR/log.txt
echo "Welcome to Easy Consensus Tree" > $log_file

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
python3 $PROJECT_DIR/scripts/fetch_proteomes.py $SPECIES_LIST | tee -a $log_file

if [[ $? -ne 0 ]]; then
    log_message "Error: Fetching proteomes failed. Exiting."
    exit 1
fi
log_message "Fetch completed successfully."


#######################################
# Merge proteomes
#######################################
log_message "Merging proteomes..."
python3 $PROJECT_DIR/scripts/merge_proteomes.py $SPECIES_LIST.paths | tee -a $log_file

if [[ $? -ne 0 ]]; then
    log_message "Error: Merging proteomes failed. Exiting."
    exit 1
fi
log_message "Merge completed successfully."


#######################################
# Sequence clustering
#######################################
log_message "Clustering sequences..."
# in: path to merged fasta.gz (problem: ambiguous name - this keeps being a problem down the line)
# options: msi, clustermode, covmode, c
# out: ...all_seqs.fasta, ...cluster.csv in $CURRENT_DIR


#######################################
# Filter clusters
#######################################
log_message "Filtering clusters..."
# in:  ...all_seqs.fasta
# out: folders para and nonpara and files np.txt and p.txt in $CURRENT_DIR

#######################################
# Run MSA
#######################################
log_message "Running MSA..."
# in: path to np.txt from filtering
# out: aln files in nonpara folder

#######################################
# Construction of gene family trees
#######################################
log_message "Constructing trees for gene families..."
# in: aln files (see below)
# out: nwk files in nonpara folder

# the script processes only one file at a time with no wrapper
# for file in dir/nonpara/*.aln; do python3 run_NJ.py $file | tee -a $log_file; done


#######################################
# Construction of consensus tree
#######################################
log_message "Constructing consensus tree..."
# in: folder with nwk (nonpara folder), file with taxa list ($SPECIES_LIST), min_freq (from user, this is not optional, for now)
# out: CONSENSUS.tree file in nonpara folder


#######################################
# Tree visualization
#######################################
# ?TODO?



log_message "All completed successfully."
