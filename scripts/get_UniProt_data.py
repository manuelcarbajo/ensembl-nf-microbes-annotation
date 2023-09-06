import sys
import ast
import requests
import os

def read_tax_rank(genome_name):
    tax_ranks = {}
    tax_rank_file = genome_name + "/tax_ranks.txt"
    with open(tax_rank_file, 'r') as file:
        content = file.read()
        tax_rank = ast.literal_eval(content)
    return tax_rank


def query_UniProt(tax_ranks):
    for l in range(2):
        current_name = "level_" + str(l) + "_name"
        current_tax = "level_" + str(l) + "_tax"
        if tax_ranks[current_name]:
            genome_name = tax_ranks[current_name]
            genome_tax = tax_ranks[current_tax]
            genome_dir = tax_ranks['genome_name'] + "/" + process_string(genome_name) + "_uniprot.fa"
            url = "https://rest.uniprot.org/uniprotkb/stream?format=fasta&query=taxonomy_id:" + str(genome_tax) + "&existence:1&existence:2format=json"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    currentFolderName = os.getcwd()
                    print("SUCCESS at level " + str(l) + ": " + genome_dir + " currentFolderName: " + currentFolderName)
                    with open(genome_dir,"w") as gf:
                        gf.write(response.text)
                    break
            except Exception as err:
                print("Error querying UniProt: " + str(err) + " at level " + str(l) + " : " + genome_name + " " + str(genome_tax) + " dir: " + genome_dir )


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
        tr = read_tax_rank(genome_name)
        query_UniProt(tr)
