import sys
import ast
import requests
import os
import subprocess
from datetime import datetime
import my_process as mp


def generate_ena_csv(tax_ranks,genome, baseDir):
    data_found = False
    for l in range(0,4):
        current_name = "level_" + str(l) + "_name"
        current_tax = "level_" + str(l) + "_tax"
        current_hierarchy = "level_" + str(l) + "_hierarchy"
        #TO DO - review filtering conditions, otherwise ranks_dict["species"] is just enough. 
        if tax_ranks[current_name] and tax_ranks[current_hierarchy] == mp.ranks_dict["species"] and not data_found:
            g_name = tax_ranks[current_name]
            genome_name = mp.process_string(g_name)
            genome_tax = tax_ranks[current_tax]
            output_rna_csv_path = genome + "_" + str(genome_tax) + "_rna.csv"
            command = ["perl", baseDir + "/frameworks/ensembl-hive/scripts/standaloneJob.pl", "Bio::EnsEMBL::Analysis::Hive::RunnableDB::HiveDownloadCsvENA", "-taxon_id", str(genome_tax),"-inputfile", output_rna_csv_path]
            log_file_path = os.path.join(baseDir, 'rna_script.log')
            with open(log_file_path, 'w') as log_file:
                try:
                    subprocess.run(command, stdout=log_file, stderr=subprocess.STDOUT, check=True)
                    line_count = 0
                    with open(output_rna_csv_path, 'r') as rnafile:
                        for line in rnafile:
                            fastq_file = line.strip().split('\t')[3]
                            download_fastq_command = ["perl",baseDir + "/frameworks/ensembl-hive/scripts/standaloneJob.pl","Bio::EnsEMBL::Analysis::Hive::RunnableDB::HiveDownloadRNASeqFastqs","-ftp_base_url","ftp://ftp.sra.ebi.ac.uk/vol1/fastq/","-input_dir","short_read_fastq_dir", "-iid",fastq_file]
                            subprocess.run(download_fastq_command, stdout=log_file, stderr=subprocess.STDOUT, check=True)
                            line_count += 1 
                            print(fastq_file + " downloaded " + str(line_count))
                    current_rank = "level_" + str(l) + "_rank"
                    genome_tax_rank = tax_ranks[current_rank]
                    tax_hierarchy = tax_ranks[current_hierarchy]
                    print("generate_ena_csv executed successfully for level " + str(l) + " " + genome + " " + str(genome_tax) + " ENA CSV files contains " + str(line_count) + " entries for tax hierarchy level: " + genome_tax_rank + " hierarchy: " + str(tax_hierarchy))
                    data_found = True
                except subprocess.CalledProcessError as e:
                    print("generate_ena_csv error for level " + str(l) + " executing command '"+ str(command) +"' : " + str(e) +" ")

        elif data_found:
            break
         
if __name__ == "__main__":
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("*** begin RNA-seq " + str(now) )
    if len(sys.argv) < 1:
        print("The path to the genome is missing as an argument.")
    else:
        genome_name = sys.argv[1]
        baseDir = sys.argv[2]
        print("       genome_name: " + genome_name )
        tr = mp.read_tax_rank(genome_name)
        generate_ena_csv(tr, genome_name, baseDir)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("*** end RNA-seq " + str(now) )
