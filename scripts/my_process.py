import ast
from urllib.parse import urlparse, parse_qs

ranks_dict = {
    'superkingdom': 1, 'kingdom': 2, 'subkingdom': 3, 'superphylum': 4, 'phylum': 5, 
    'subphylum': 6, 'infraphylum': 7, 'superclass': 8, 'class': 9, 'subclass': 10, 
    'infraclass': 11, 'cohort': 12, 'subcohort': 13, 'superorder': 14, 'order': 15, 
    'suborder': 16, 'infraorder': 17, 'parvorder': 18, 'superfamily': 19, 'family': 20, 
    'subfamily': 21, 'tribe': 22, 'subtribe': 23, 'genus': 24, 'subgenus': 25, 'section': 26, 
    'subsection': 27, 'series': 28, 'subseries': 29, 'species group': 30, 'species subgroup': 31, 
    'species': 32, 'forma specialis': 33, 'subspecies': 34, 'varietas': 35, 'subvariety': 36, 
    'forma': 37, 'serogroup': 38, 'serotype': 39, 'strain': 40, 'isolate': 41
}

def read_config(conf_file_path):

    # Read configuration file and extract the URL
    with open(conf_file_path, 'r') as config_file:
        url = config_file.readline().strip()

    # Parse the URL to get the connection parameters
    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.query)

    # Extract the connection parameters
    host = parsed_url.hostname
    user = parsed_url.username
    password = parsed_url.password
    database = parsed_url.path[1:]
    port = int(parsed_url.port)

    return host, user, password, database, port


def read_tax_rank(genome_name):
    tax_ranks = {}
    tax_rank_file =  genome_name + "/tax_ranks.txt"
    with open(tax_rank_file, 'r') as file:
        content = file.read()
        tax_rank = ast.literal_eval(content)
    return tax_rank

def process_string(input_string):
    # Remove apostrophes
    processed_string = input_string.replace("'", "")
    # Replace white spaces with underscores
    processed_string = processed_string.replace(" ", "_")
    # Convert to lowercase
    processed_string = processed_string.lower()

    return processed_string
