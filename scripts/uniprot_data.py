import sys
import requests
import os
import subprocess
import gzip
from datetime import datetime
import my_process as mp


def query_UniProt(tax_ranks, baseDir):
    data_found = False
    for l in range(4):
        current_rank = "level_" + str(l) + "_rank"
        current_name = "level_" + str(l) + "_name"
        current_tax = "level_" + str(l) + "_tax"
        if tax_ranks[current_name] and not data_found:
            g_name = tax_ranks[current_name]
            genome_name = mp.process_string(g_name)
            genome_tax = tax_ranks[current_tax]
            root_path_prefix = tax_ranks['genome_name'] + "/" + genome_name
            uniprot_fasta_file = root_path_prefix + "_uniprot.fa"
            url = "https://rest.uniprot.org/uniprotkb/stream?compressed=false&format=fasta&query=%28%28taxonomy_id%3A" + str(genome_tax) + "%29+AND+%28%28existence%3A1%29+OR+%28existence%3A2%29%29%29"
            try:
                response = requests.get(url)
                
                if response.status_code == 200:
                    print("SUCCESS at level " + str(l) + ": " + uniprot_fasta_file)
                    with open(uniprot_fasta_file,"w") as gf:
                        gf.write(response.text)
                    data_found = True
                    index_fasta(root_path_prefix, baseDir)
            except Exception as err:
                print("Error querying UniProt: " + str(err) + " at level " + str(l) + " : " + genome_name + " " + str(genome_tax) + " dir: " + uniprot_fasta_file )
        elif data_found:
            break

def index_fasta(root_path_prefix, baseDir):
    # Paths for intermediate and final files
    fasta_file = root_path_prefix + "_uniprot.fa"
    reheadered_fasta = root_path_prefix + "_reheadered.fasta"
    deduped_fasta = root_path_prefix + "_deduped.fasta"
    output_fasta = root_path_prefix + "_uniprot_proteins.fa"

    # Reheader the FASTA file using the Perl script
    reheader_command = f"perl {baseDir}/bin/reheader_uniprot_seqs.pl {fasta_file} > {reheadered_fasta}"
    subprocess.run(reheader_command, shell=True, check=True)

    # Remove duplicate sequences using the Perl script
    dedup_command = f"perl {baseDir}/bin/remove_dup_seqs.pl {reheadered_fasta} > {output_fasta}"
    subprocess.run(dedup_command, shell=True, check=True)

    # Index the final output using samtools
    samtools_command = f"samtools faidx {output_fasta}"
    subprocess.run(samtools_command, shell=True, check=True)



if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("The path to the genome is missing as an argument.")
    else:
        genome_name = sys.argv[1]
        baseDir = sys.argv[2]
        tr = mp.read_tax_rank(genome_name)
        query_UniProt(tr, baseDir)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("** endtime UNIPROT: " + str(now))
