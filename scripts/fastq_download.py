import sys
import requests
import os
import subprocess
from datetime import datetime
import my_process as mp
import random
import time


def download_fastq(fastq_file, genome_dir, baseDir):
    log_file_path = os.path.join(baseDir, 'rna_script.log')
    with open(log_file_path, 'w') as log_file:
        try:
            download_fastq_command = ["perl", baseDir + "/frameworks/ensembl-hive/scripts/standaloneJob.pl","Bio::EnsEMBL::Analysis::Hive::RunnableDB::HiveDownloadRNASeqFastqs","-ftp_base_url","ftp://ftp.sra.ebi.ac.uk/vol1/fastq/","-input_dir","." , "-iid",fastq_file]
            subprocess.run(download_fastq_command, stdout=log_file, stderr=subprocess.STDOUT, check=True)
            
        except subprocess.CalledProcessError as e:
            print("Download fastq error. Command :"+ str(download_fastq_command) +": " + str(e) +" ")
              

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("The path to the genome is missing as an argument.")
    else:
        # Generate a random wait time between 0 and 15 seconds to avoid spaming ENA
        wait_time = random.randint(1, 1500) / 100.0
        time.sleep(wait_time)
        
        genome_dir = sys.argv[1]
        fastq_file = sys.argv[2]
        baseDir = sys.argv[3]
        now1 = datetime.now()
        #print("-- genome_dir: " + genome_dir +"\t fastq_file: " + fastq_file + " " + str(now1.strftime('%Y-%m-%d %H:%M:%S')))
        download_fastq( fastq_file, genome_dir, baseDir)
        now2 = datetime.now()
        lap = now2 - now1
        print(fastq_file + " downloaded. Elapsed time: " + str(lap) )
