import sys
import requests
import os
import subprocess
from datetime import datetime
import my_process as mp
import random
import time


def run_ensembl_anno(baseDir, genome_name, genome_fasta_file, genome_path, short_read_fastq_dir, uniprot_fa, orthodb_fa):
    log_file_path = os.path.join(baseDir, 'logs',genome_name, 'run_ensembl_anno_script.log') 
    print("log_file_path: " + log_file_path)
    current_dir = os.getcwd()
    print("current_dir :" + current_dir)
    
    with open(log_file_path, 'w') as log_file:
        try:
            workdir = baseDir + "/frameworks/ensembl-anno/ensembl_anno.py"
            diamond_db_path = baseDir + "/data/uniprot_euk.fa.dmnd"
            ensembl_anno_command = ["python", workdir, 
                "--genome_file",os.path.realpath(genome_fasta_file), 
                "--output_dir",current_dir,
                "--short_read_fastq_dir", os.path.realpath(short_read_fastq_dir),
                "--protein_file", os.path.realpath(uniprot_fa),
                "--busco_protein_file", os.path.realpath(orthodb_fa),
                "--num_threads", str(40),
                "--run_full_annotation",
                "--diamond_validation_db", diamond_db_path,
                "--validation_type","moderate"]

            subprocess.run(ensembl_anno_command,stdout=log_file, stderr=subprocess.STDOUT, check=True)
            #print("REMEMBER TO UNCOMMENT ensembl-anno process call. CURRENT STATE: OFF")
        except subprocess.CalledProcessError as e:
            print("Run Ensembl Anno Error. Command :"+ str(ensembl_anno_command) +": " + str(e) +" ")


if __name__ == "__main__":
    if len(sys.argv) < 10:
        print("Some arguments might be missing, only " + str(len(sys.argv)) + " have been passed. 10 expected")
    else:
        for i in range(len(sys.argv)):
            print( "arg[" + str(i) + "] - " + str(sys.argv[i]))
        
        now1 = datetime.now()
        genome_name = sys.argv[1]
        genome_path = sys.argv[2]
        rfam_ids_path = sys.argv[3]
        uniprot_fa = sys.argv[4]
        uniprot_fai = sys.argv[5]
        orthodb_fa = sys.argv[6]
        orthodb_fai = sys.argv[7]
        short_read_fastq_dir = os.path.join(sys.argv[2],sys.argv[8])
        baseDir = sys.argv[9]
        genome_fasta_file = sys.argv[10]
        print("****\n*****\n**** Ensembl run args: \n\tgenome_name: " + genome_name  
                + "\n\tgenome_fasta_file: " + genome_fasta_file
                + "\n\tgenome_path: " + genome_path 
                + "\n\trfam_ids: " + rfam_ids_path
                + "\n\tuniprot_fa: " + uniprot_fa
                + "\n\tuniprot_fai: " + uniprot_fai
                + "\n\torthodb_fa: " + orthodb_fa 
                + "\n\torthodb_fai: " + orthodb_fai
                + "\n\tshort_read_fastq_dir: " + short_read_fastq_dir
                + "\n\tbaseDir: " + baseDir
                + "\n *** run ensembl anno begin time " + str(now1.strftime('%Y-%m-%d %H:%M:%S')))
        run_ensembl_anno(baseDir, genome_name, genome_fasta_file, genome_path, short_read_fastq_dir, uniprot_fa, orthodb_fa)

