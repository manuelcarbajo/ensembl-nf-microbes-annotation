import csv
import sys
import os
import mysql.connector
from urllib.parse import urlparse, parse_qs

def read_csv_file(csv_file, output_path, ncbi_config):
    try:
        with open(csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            species_dict = {}
            for row in reader:
                if row and not row[0].startswith('#'):
                    level_0_name = row[0]
                    level_0_tax = row[1]
                    level_0_gca = row[2]
                    if '.' in level_0_gca:
                        level_0_gca = level_0_gca.split('.')[0]
                        
                    level_0_name_gca = level_0_name + "_" + level_0_gca
                    level_0_dir = output_path + "/" + level_0_name_gca
                    if not os.path.exists(level_0_dir):
                        # Create the directory
                        os.makedirs(level_0_dir)
                    species_dict[level_0_gca] = {
                            "level_0_name": level_0_name,
                            "level_0_tax": level_0_tax,
                            "genome_dir": level_0_dir,
                            }

            species_dict = execute_mysql_query(ncbi_config, species_dict)
            print(species_dict)        
    except FileNotFoundError:
        print(f"Error: File '{csv_file}' or '{output_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    
    # write the tax rank data to the corresponding folder of each species
    try:
        for gca in species_dict:
            genome_dir = species_dict[gca]["genome_dir"]
            tax_rank_file = os.path.join(genome_dir,"tax_ranks.txt")
            try:
                with open(tax_rank_file, "w") as output_file:
                    # Write the data associated with the key (gca) to the file
                    output_file.write(str(species_dict[gca])) 
            except IOError as e:
                print(f"Error writing to tax_rank file '{output_file_path}': {e}")
            except UnicodeEncodeError as e:
                print(f"Error encoding data for tax_rank file '{output_file_path}': {e}")
    
    except Exception as e:
        print(f"An error occurred while storing the taxonomic rank data: {e}")

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
    database = parsed_url.path[1:]  # Remove the leading '/'
    port = int(parsed_url.port)
    return host, user, password, database, port

# Rest of the code remains the same as before



def execute_mysql_query(config_file_path, species_dict):
    # Read MySQL connection parameters from the configuration file
    host, user, password, database, port = read_config(config_file_path)

    # Establish MySQL connection
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        print("Connection established successfully.")
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return

    # Execute MySQL query and get taxon and name for 3 taxonomic ranks above the current one
    for gca in species_dict:
        try:
            query_tax = species_dict[gca]["level_0_tax"]
            for query_level in ["level_0","level_1","level_2","level_3"]:
                query = "SELECT nm.taxon_id, nm.name, parent_id from ncbi_taxa_name nm join ncbi_taxa_node nd using(taxon_id) where name_class='scientific name' and taxon_id=" + str(query_tax) + ";" 
                cursor = connection.cursor()
                cursor.execute(query)
                result = cursor.fetchall()[0]
                query_tax = result[2]
                if query_level != "level_0":
                    current_tax = query_level + "_tax"
                    current_name = query_level + "_name"
                    species_dict[gca][current_tax] = result[0]
                    species_dict[gca][current_name] = result[1]
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
     
    
    # Close the cursor and connection
    if 'cursor' in locals() and cursor is not None:
        cursor.close()
    if 'connection' in locals() and connection.is_connected():
        connection.close()
    return species_dict

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Please provide the csv file path and the output_path as arguments.")
    else:
        csv_file = sys.argv[1]
        output_path = sys.argv[2]
        ncbi_config = sys.argv[3]
        read_csv_file(csv_file, output_path, ncbi_config)

