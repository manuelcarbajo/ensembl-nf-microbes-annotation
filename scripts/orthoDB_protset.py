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

def query_OrthoDB(tax_ranks, baseDir):
    data_found = False
    for l in range(1,4):
        current_name = "level_" + str(l) + "_name"
        current_tax = "level_" + str(l) + "_tax"
        if tax_ranks[current_name] and not data_found:
            g_name = tax_ranks[current_name]
            genome_name = process_string(g_name)
            genome_tax = tax_ranks[current_tax]

            command = ["python3", baseDir + "/bin/download_orthodb_protset.py", str(genome_tax), baseDir]
            try:
                subprocess.run(command, check=True)
                print("Command executed successfully for level " + str(l) + " " + genome_name + " " + str(genome_tax))
                data_found = True
            except subprocess.CalledProcessError as e:
                print(f"Error executing command '{command}' : {e}")
        elif data_found:
            break
         

def process_string(input_string):
    # Remove apostrophes
    processed_string = input_string.replace("'", "")
    # Replace white spaces with underscores
    processed_string = processed_string.replace(" ", "_")
    # Convert to lowercase
    processed_string = processed_string.lower()

    return processed_string

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("The path to the genome is missing as an argument.")
    else:
        genome_name = sys.argv[1]
        uniprot_fa = sys.argv[2]
        uniprot_fai = sys.argv[3]
        baseDir = sys.argv[4]
        print("genome_name: " + genome_name + " uniprot_fa: " + uniprot_fa + " uniprot_fai: " + uniprot_fai)
        tr = read_tax_rank(genome_name)
        query_OrthoDB(tr, baseDir)
