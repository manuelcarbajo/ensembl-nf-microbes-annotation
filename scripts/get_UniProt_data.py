import sys
import ast
import requests

def read_tax_rank(tax_rank_file):
    tax_ranks = {}

    with open('tax_ranks.txt', 'r') as file:
        content = file.read()
        tax_ranks = ast.literal_eval(content)

    return tax_ranks


def query_UniProt(tax_ranks):
    for l in range(4):
        current_name = "level_" + str(l) + "_name"
        current_tax = "level_" + str(l) + "_tax"
        if tax_ranks[current_name]:
            genome_name = tax_ranks[current_name]
            genome_tax = tax_ranks[current_tax]
            try:
                print(genome_name + " " + str(genome_tax)) 
                #curl -o uniprot_data_${GENOME_NAME}.fasta https://rest.uniprot.org/uniprotkb/stream?format=fasta&query=%28%28taxonomy_id%3A508771%29%20AND%20%28existence%3A%22Evidence%20at%20protein%20level%20%5B1%5D%22%20OR%20existence%3A%22Evidence%20at%20transcript%20level%20%5B2%5D%22%29%29
            except Exception as err:
                print("Error querying UniProt: " + err)


if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("The path to the genome is missing as an argument.")
    else:
        output_path = sys.argv[1]
        tax_ranks = read_tax_rank(output_path)
        query_UniProt(tax_ranks)
