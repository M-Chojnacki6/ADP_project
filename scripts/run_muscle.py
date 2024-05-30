#!/usr/bin/env python3

import os
import subprocess
import argparse


def run_muscle(input_file, output_file):
    #muscle  = "C:/Users/krzys/Desktop/muscle5.1.win64.exe"
    #muscle_command = f"{muscle} -align {input_file} -output {output_file}"

    muscle_command = f"muscle -align {input_file} -output {output_file}"
    subprocess.run(muscle_command, shell=True)

def run_muscle_on_folder(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    fasta_files = [file for file in os.listdir(input_folder) if file.endswith(".fasta")]
    for fasta_file in fasta_files:
        input_path = os.path.join(input_folder, fasta_file)
        output_path = os.path.join(output_folder, f"{fasta_file.split('.')[0]}_aligned.fasta")
        run_muscle(input_path, output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Multiple sequence alignment using muscle')
    parser.add_argument('-f', type=str, help='Path to your fasta file')
    parser.add_argument('-d', type=str, help='Path to a directory containing fasta files')


    args = parser.parse_args()
    if args.f:
        output = f"{args.f.split('.')[0]}_aligned.fasta"
        run_muscle(args.f, output)
    if args.d:
        run_muscle_on_folder(args.d, f'{args.d}/muscle_output')