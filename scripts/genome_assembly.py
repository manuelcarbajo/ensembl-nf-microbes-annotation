import sys
import requests
import os
import subprocess
import gzip
from datetime import datetime
import my_process as mp


def query_ENA(tax_ranks, baseDir):
    current_rank = "level_0_rank"
    current_name = "level_0_name"
    current_tax = "level_0_tax"
    
    g_name = tax_ranks[current_name]
    genome_name = mp.process_string(g_name)
    genome_tax = tax_ranks[current_tax]
    genome_accession = tax_ranks["genome_accession"]
    root_path_prefix = tax_ranks["genome_name"] + "/" + genome_name
    downloaded_fasta_file = root_path_prefix + "_original_genome.fa"
    reheaded_fasta_file = root_path_prefix + "_reheaded_assembly.fa"

    url = "https://www.ebi.ac.uk/ena/browser/api/fasta/" + genome_accession + "?download=true&lineLimit=0"
    
    try:
        response = requests.get(url)

        if response.status_code == 200:
            with open(downloaded_fasta_file,"w") as gf:
                gf.write(response.text)
            mp.rehead_fasta(downloaded_fasta_file, reheaded_fasta_file)
            print("SUCCESS querying ENA.Fasta file downloaded and reheaded to " + reheaded_fasta_file)
            
    except Exception as err:
        print("Error querying ENA: " + str(err) + " : " + genome_name + " " + str(genome_tax) + " dir: " + assembly_fasta_file )

"""
def replace_non_utf8_chars(input_str):
    return ''.join(char if ord(char) < 128 else '_' for char in input_str)

def rehead_fasta(input_filename, output_filename):
    with open(input_filename, 'r') as infile, open(output_filename, 'w') as outfile:
        for line in infile:
            if line.startswith('>'):
                header = replace_non_utf8_chars(line.strip())
                outfile.write(f"{header}\n")
            else:
                outfile.write(line)
"""

if __name__ == "__main__":
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("** begintime ENA: " + str(now))
    
    if len(sys.argv) < 1:
        print("The path to the genome is missing as an argument.")
    else:
        genome_name = sys.argv[1]
        baseDir = sys.argv[2]
        tr = mp.read_tax_rank(genome_name)
        query_ENA(tr, baseDir)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("** endtime ENA: " + str(now))

