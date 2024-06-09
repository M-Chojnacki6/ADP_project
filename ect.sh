#!/bin/bash

#######################################
# Easy Consensus Tree
# by Mateusz Chojnacki, Krzysztof Łukasz, Younginn Park, Daniel Zalewski
#######################################

# Define absolute paths
THIS_SCRIPT_PATH=$(realpath "$0")
PROJECT_DIR=$(dirname $THIS_SCRIPT_PATH) # ECT
CURRENT_DIR=$PWD # wherever the user is, safety valve

SPECIES_LIST=$CURRENT_DIR/species.txt


# Define defoult parameters
MSA_MODE=0
MSI_MODE=0.3
CLUST_MODE=0
COV_MODE=0
COV_VALUE=0.8
STEP=0

function display_help() {
    echo "ECT"
    echo "by Mateusz Chojnacki, Krzysztof Łukasz, Younginn Park, Daniel Zalewski"
    echo ""
    echo "A streamlined tool for reconstructing phylogenetic trees using whole-proteome approach."
    echo ""
    echo "Usage: $0 <-i SPECIES_LIST>"
    echo "Options:"
    echo "  -h, --help         Show this help message"
    echo "  -i, --input        Text file with species names or taxonomy id in lines (default: species.txt)"
    echo "  -o, --output       Name of the output directory; it is created if doesn't exist"
    echo "  -e, --step         Select step, from ehich you wont to start script (to use in case, when you 
                     have files made to some step, but due to some reasons script was abruptly aborted.
                     > 0: All steps (default)
                     > 1: start with merging step
                     > 2: start with MMseq2 clustering
                     > 3: start with filtering step
                     > 4: Start with making MSA
                     > 5: start with construction NJ trees
                     > 6: start with preparing consensus (final) tree"
    echo "  -s, --msi,         MMseq2 option: list matches above this sequence identity (range 0.0-1.0); 
                     (default: 0.3)"
    echo "  -l, --clusterMode  MMseq2 option: select clustering mode:
                     > 0: Set-Cover (greedy) (default)
                     > 1: Connected component (BLASTclust)
                     > 2,3: Greedy clustering by sequence length (CDHIT)"
    echo "  -v, --covMode      MMseq2 option:  sevuence coverage mode:
                     > 0: coverage of query and target (default)
                     > 1: coverage of target
                     > 2: coverage of query
                     > 3: target seq. length has to be at least x percent of query length
                     > 4: query seq. length has to be at least x percent of target length
                     > 5: short seq. needs to be at least x percent of the other seq. length"
    echo "  -c, --cov          MMseq2 option: list matches above this fraction of aligned (covered) residues;
                     (default: 0.800)"
    echo "  -m, --msa          Algorithm used to MSA: 
                     > 0 - ClustalW (default)
                     > 1 - Muscle
                     > 2 - Mafft"
    exit 0
}

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -h|--help) display_help ;;
        -i|--input) SPECIES_LIST="$2"; shift ;;
        -m|--msa) MSA_MODE="$2"; shift ;;
        -s|--msi) MSI_MODE="$2"; shift ;;
        -l|--clusterMode) CLUST_MODE="$2"; shift ;;
        -v|--covMode) COV_MODE="$2"; shift ;;
        -c|--cov) COV_VALUE="$2"; shift ;;
        -e|--step) STEP="$2"; shift ;;
        -o|--output) NEW_CURRENT_DIR="$2"; shift ;;
        # add other options here
        # don't forget to add them to usage and help too
        *) echo "Unknown parameter passed: $1"; display_help ;;
    esac
    shift
done

# changing current direcrtory to selected, if neccesary
if [[ ! -d $NEW_CURRENT_DIR ]];then
    mkdir $NEW_CURRENT_DIR
    echo "Creating output directory $NEW_CURRENT_DIR"
fi


if [[ -d $NEW_CURRENT_DIR ]];then
    echo "Setting output directory: $NEW_CURRENT_DIR"
    $CURRENT_DIR=$NEW_CURRENT_DIR
fi

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

# Function to run a command and save output to log
function run_and_log() {
    local cmd="$1"
    local action="$2"

    output=$($cmd 2>&1)
    status=$?

    echo "$output" | tee -a "$log_file"

    if [[ $status -ne 0 ]]; then
        log_message "Error: $action failed. Exiting."
        exit 1
    else
        log_message "$action completed successfully."
    fi
}

log_message "Starting Easy Consensus Tree"

if [ ! -f $SPECIES_LIST ]; then
    log_message "File $SPECIES_LIST not found"
    echo "to show help, use: ./ECT/ect.sh -h"
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
if [ $STEP -lt 1 ]; then
    log_message "Fetching proteomes from $SPECIES_LIST..."

    run_and_log "python3 $PROJECT_DIR/scripts/fetch_proteomes.py $SPECIES_LIST" "Fetching"
else
    log_message "Skipping fetching step from $SPECIES_LIST..."
fi
#######################################
# Merge proteomes
#######################################
if [ $STEP -lt 2 ]; then
    log_message "Merging proteomes from $SPECIES_LIST.paths..."

    run_and_log "python3 $PROJECT_DIR/scripts/merge_proteomes.py $SPECIES_LIST.paths" "Merging"
else
    log_message "Skipping merging step from $SPECIES_LIST.paths..."
fi
#######################################
# Sequence clustering
#######################################

# in: path to merged fasta.gz
#   # problem: ambiguous name - this keeps being a problem down the line)
#   # assumption for now: filename prefix is always [name_of_species_txt]_merged[nr_of_proteoms]
MERGED_PREFIX="$(basename $SPECIES_LIST .txt)_merged$(grep -c '.' $SPECIES_LIST.paths)" # e.g. names_merged5
# options: msi (--min_seq_id), clustermode, covmode, c
# out: ...all_seqs.fasta, ...cluster.csv in $CURRENT_DIR
if [ $STEP -lt 3 ]; then
    log_message "Clustering sequences from $MERGED_PREFIX.fasta.gz..."

    run_and_log "python3 $PROJECT_DIR/scripts/run_mmseqs.py $CURRENT_DIR/$MERGED_PREFIX.fasta.gz -msi $MSI_MODE -clusterMode $CLUST_MODE -covMode $COV_MODE -c $COV_VALUE" "Clustering"
else
    log_message "Skipping MMseq2 clusterng step from $MERGED_PREFIX.fasta.gz..."
fi
#######################################
# Filter clusters
#######################################
if [ $STEP -lt 4 ]; then
    log_message "Filtering clusters from ${MERGED_PREFIX}_all_seqs.fasta..."
    # in:  ...all_seqs.fasta
    # option: -c (cutoff for min number of species in a nonpara cluster)
    # out: folders para and nonpara and files np.txt and p.txt in $CURRENT_DIR/merged-prefix

    run_and_log "python3 $PROJECT_DIR/scripts/split_clusters.py $CURRENT_DIR/${MERGED_PREFIX}_all_seqs.fasta" "Filtering"

else
    log_message "Skipping filering step from ${MERGED_PREFIX}_all_seqs.fasta..."
fi
#######################################
# Run MSA
#######################################
if [ $STEP -lt 5 ]; then
    log_message "Running MSA on clusters from $MERGED_PREFIX/np.txt..."
    # in: path to np.txt from filtering
    # out: aln files in merged-prefix/nonpara folder

    # error while using clustalw: for some reason it thinks np.txt is an "unknown option"
    run_and_log "python3 $PROJECT_DIR/scripts/run_MSA.py $CURRENT_DIR/$MERGED_PREFIX/np.txt -mode $MSA_MODE" "MSA"
else
    log_message "Skipping MSA step from $MERGED_PREFIX/np.txt..."
fi
#######################################
# Construction of gene family trees
#######################################
if [ $STEP -lt 6 ]; then
    log_message "Constructing trees for gene families in folder $MERGED_PREFIX/nonpara/*.aln..."
    # in: aln files (see below)
    # out: nwk files in nonpara folder

    # the script processes only one file at a time with no wrapper
    # shopt -s nullglob
    for file in $CURRENT_DIR/$MERGED_PREFIX/nonpara/*aln; do
        run_and_log "python3 $PROJECT_DIR/scripts/run_NJ_on_alignment.py $file" "Tree construction"
    done

    log_message "Gene family tree construction completed successfully."
else
    log_message "Skipping NJ trees construction step from $MERGED_PREFIX/nonpara/*aln..."
fi

#######################################
# Construction of consensus tree
#######################################
if [ $STEP -lt 7 ]; then
    log_message "Constructing consensus tree for trees in $MERGED_PREFIX/nonpara/*.nwk..."
    # in: folder with nwk (nonpara folder), file with taxa list ($SPECIES_LIST), min_freq (from user, this is not optional, for now)
    # out: CONSENSUS.tree file in nonpara folder

    run_and_log "python3 $PROJECT_DIR/scripts/run_consensus.py $CURRENT_DIR/$MERGED_PREFIX/nonpara $SPECIES_LIST 0.3" "Consensus tree construction"

    log_message "Final tree saved to $CURRENT_DIR/$MERGED_PREFIX/nonpara/CONSENSUS.tree"
else
    log_message "Skipping consensus tree construction step from $MERGED_PREFIX/nonpara/*nwk..."
fi


#######################################
# Tree visualization
#######################################
log_message "Show tree from $MERGED_PREFIX/nonpara/CONSENSUS.tree..."
# in: CONSENSUS.tree file in nonpara folder

run_and_log "python3 $PROJECT_DIR/scripts/plot_tree.py $CURRENT_DIR/$MERGED_PREFIX/nonpara/CONSENSUS.tree" "Tree visualisation"



log_message "All finished"
