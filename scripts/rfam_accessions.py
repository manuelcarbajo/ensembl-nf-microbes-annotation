import sys
import os
from datetime import datetime
import mysql.connector
import my_process as mp


def query_Rfam(tax_ranks, config_file_path, genome_dir):
    # Read MySQL connection parameters from the configuration file
    host, user, password, database, port = mp.read_config(config_file_path)
    genome_name = tax_ranks["genome_name"]
    current_dir = os.getcwd()
    print("current_dir: " + current_dir)
    rfam_ids_path = "rfam_ids.txt"
    rfam_results = []
    # Establish a connection to the MySQL database
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )

        # Create a cursor object to interact with the database
        cursor = connection.cursor()
        max_nb_families = 0
        rfam_result = set()
        for l in range(4):
            name_tag = "level_" + str(l) + "_name"
            tax_tag = "level_" + str(l) + "_tax"
            rank_tag = "level_" + str(l) + "_rank"
            try:
                if tax_ranks[rank_tag]:
                    genome_name = tax_ranks[name_tag]
                    rank = tax_ranks[rank_tag] 
                    rank_hierarchy = mp.ranks_dict[rank]
                    if rank_hierarchy <= mp.ranks_dict['species']:

                        # Define your SQL query
                        count_sql_query = f"""
                            SELECT count(family_ncbi.rfam_acc) 
                            FROM family_ncbi, taxonomy 
                            WHERE family_ncbi.ncbi_id = taxonomy.ncbi_id 
                            AND species LIKE '%{genome_name}%'
                        """
                        # Execute the query
                        cursor.execute(count_sql_query)
                        # Fetch all the rows returned by the query
                        rows = cursor.fetchall()
                        families_count = rows[0][0]
                        print( " genome_name: " + genome_name + " rank_hierarchy: " + str(rank_hierarchy) + " " + rank )
                        print("  families_count: " + str(families_count) )
                        if families_count > max_nb_families:
                            max_nb_families = families_count
                            families_sql_query = f"""
                            SELECT family_ncbi.rfam_acc 
                            FROM family_ncbi, taxonomy 
                            WHERE family_ncbi.ncbi_id = taxonomy.ncbi_id 
                            AND species LIKE '%{genome_name}%'
                            """
                            cursor.execute(families_sql_query)
                            rfam_results = set(row[0] for row in cursor)
            except Exception as e:
                print("Error connecting to Rfam : " + str(e))

        # Write the results to a file
        with open(rfam_ids_path, "w") as output_file:
            for rf in rfam_results:
                output_file.write(rf + "\n")
        # Close the cursor and connection
        cursor.close()
        connection.close()
        print("rfam ids path: " + rfam_ids_path)
    except mysql.connector.Error as err:
        print("Error connecting to MySQL RFam server: ", err)

    return rfam_ids_path

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Please provide the genome name and the rfam config file as arguments.")
    else:
        genome_name = sys.argv[1]
        rfam_config = sys.argv[2]
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("** begin RFAM accessions " + str(now) + " genome_name: " + genome_name + " rfam config: " + rfam_config)
        tr = mp.read_tax_rank(genome_name)
        rfam_ids_path = query_Rfam(tr, rfam_config, genome_name)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("** end RFAM accessions " + str(now) )
