

def download_fastq(fastq_file, baseDir):
    log_file_path = os.path.join(baseDir, 'rna_script.log')
    with open(log_file_path, 'w') as log_file:
        try:
            
            download_fastq_command = ["perl",baseDir + "/frameworks/ensembl-hive/scripts/standaloneJob.pl","Bio::EnsEMBL::Analysis::Hive::RunnableDB::HiveDownloadRNASeqFastqs","-ftp_base_url","ftp://ftp.sra.ebi.ac.uk/vol1/fastq/","-input_dir","short_read_fastq_dir", "-iid",fastq_file]
            subprocess.run(download_fastq_command, stdout=log_file, stderr=subprocess.STDOUT, check=True)
            print(fastq_file + " downloaded " )
            #current_rank = "level_" + str(l) + "_rank"
            #genome_tax_rank = tax_ranks[current_rank]
            #tax_hierarchy = tax_ranks[current_hierarchy]
            #print(genome + " " + str(genome_tax) + genome_tax_rank + " hierarchy: " + str(tax_hierarchy))
            
        except subprocess.CalledProcessError as e:
            print("Download fastq error. Command :"+ str(command) +": " + str(e) +" ")
              

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("The path to the genome is missing as an argument.")
    else:
        genome_name = sys.argv[1]
        fastq_file = sys.argv[2]
        baseDir = sys.argv[3]
        print("-- genome_name: " + genome_name +"\t fastq_file: " + fastq_file )
      
        #download_fastq( fastq_file, baseDir)

