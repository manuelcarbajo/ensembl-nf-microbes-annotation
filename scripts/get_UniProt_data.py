import sys
import ast
import requests
import os
import subprocess


def read_tax_rank(genome_name):
    tax_ranks = {}
    tax_rank_file = genome_name + "/tax_ranks.txt"
    with open(tax_rank_file, 'r') as file:
        content = file.read()
        tax_rank = ast.literal_eval(content)
    return tax_rank


def query_UniProt(tax_ranks, baseDir):
    for l in range(2):
        current_name = "level_" + str(l) + "_name"
        current_tax = "level_" + str(l) + "_tax"
        if tax_ranks[current_name]:
            g_name = tax_ranks[current_name]
            genome_name = process_string(g_name)
            genome_tax = tax_ranks[current_tax]
            root_path_prefix = tax_ranks['genome_name'] + "/" + genome_name
            uniprot_fasta_file = root_path_prefix + "_uniprot.fa"
            url = "https://rest.uniprot.org/uniprotkb/stream?format=fasta&query=taxonomy_id:" + str(genome_tax) + "&existence:1&existence:2format=json"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    print("SUCCESS at level " + str(l) + ": " + uniprot_fasta_file)
                    with open(uniprot_fasta_file,"w") as gf:
                        gf.write(response.text)
                    index_fasta(root_path_prefix, baseDir)
                    break
            except Exception as err:
                print("Error querying UniProt: " + str(err) + " at level " + str(l) + " : " + genome_name + " " + str(genome_tax) + " dir: " + uniprot_fasta_file )


def process_string(input_string):
    # Remove apostrophes
    processed_string = input_string.replace("'", "")
    # Replace white spaces with underscores
    processed_string = processed_string.replace(" ", "_")
    # Convert to lowercase
    processed_string = processed_string.lower()

    return processed_string


def index_fasta(root_path_prefix, baseDir):
    # Paths for intermediate and final files
    fasta_file = root_path_prefix + "_uniprot.fa"
    reheadered_fasta = root_path_prefix + "_reheadered.fasta"
    deduped_fasta = root_path_prefix + "_deduped.fasta"
    output_fasta = root_path_prefix + "_uniprot_proteins.fa"

    # Reheader the FASTA file using the Perl script
    reheader_command = f"perl {baseDir}/bin/reheader_uniprot_seqs.pl {fasta_file} > {reheadered_fasta}"
    subprocess.run(reheader_command, shell=True, check=True)

    # Remove duplicate sequences using the Perl script
    dedup_command = f"perl {baseDir}/bin/remove_dup_seqs.pl {reheadered_fasta} > {output_fasta}"
    subprocess.run(dedup_command, shell=True, check=True)

    # Index the final output using samtools
    samtools_command = f"samtools faidx {output_fasta}"
    subprocess.run(samtools_command, shell=True, check=True)



if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("The path to the genome is missing as an argument.")
    else:
        genome_name = sys.argv[1]
        baseDir = sys.argv[2]
        tr = read_tax_rank(genome_name)
        query_UniProt(tr, baseDir)
