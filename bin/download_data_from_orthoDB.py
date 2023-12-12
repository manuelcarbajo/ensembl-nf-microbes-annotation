#!/usr/bin/env python

import argparse
import os
import re
import sys
import time
import subprocess
import numpy as np
import json
import multiprocessing
from functools import partial  
import my_process as mp


def parallize_jobs(jobs,orig_clusters_comb):
    if jobs:
        procs = multiprocessing.Pool(CPU)
        # Use partial to fix the orig_clusters_comb argument
        func = partial(get_sequences, orig_clusters_comb)
        procs.map(func, jobs)
        procs.close()
        procs.join()

def get_sequences(orig_clusters_comb, data):
    outfname = "sub_%s.fa"%(data)
    command2= ["curl", "-s", "https://data.orthodb.org/current/fasta?id=%s&species="%(data), "-L", '-o', outfname]
    response2 = subprocess.Popen(command2)
    out2, err2 = response2.communicate(timeout=5)

    # Append the contents of the downloaded cluster to the combined file
    with open(outfname, 'r') as single_cluster_file, open(orig_clusters_comb, 'a') as combined_clusters_file:
        combined_clusters_file.write(single_cluster_file.read())
    #remove the single cluster
    os.remove(outfname)




def map_retrieve(ncbi_id=None, w_dir=None, orig_clusters_comb=None):
    print("WORKING ON %s" % ncbi_id)
    command1 = ["curl", "https://data.orthodb.org/current/search?universal=0.9&singlecopy=0.9&level=%s&species=%s&take=5000"%(ncbi_id, ncbi_id)]
    response = subprocess.Popen(command1, stdout=subprocess.PIPE) # pipe the terminal output to response
    out, err = response.communicate(timeout=5) # Wait for process to terminate
    p_status = response.wait() # Wait for child process to terminate. Additional wait time, just in case there is a lag.
    out = json.loads(out) # convert the output from bytes to dictionary

    if out:
        #print(out)
        groups  = out["data"]
        parallize_jobs(groups,orig_clusters_comb) # parallize the fasta download.

    os.chdir(w_dir)


if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("the ncbi id is missing as an argument.")
    else:
        ncbi_id = sys.argv[1]
        baseDir = sys.argv[2]
        genome_name = sys.argv[3]
        print("ncbi id: " + str(ncbi_id) )
        current_dir = os.getcwd()
        CPU = 91 # no of simultaneous runs.

        
        out_dir_name = genome_name + "/ncbi_id_" + ncbi_id + "_sequences"

        d_dir = os.path.join(current_dir, out_dir_name)

        if not os.path.exists(d_dir):
            print(d_dir + " doesnt exist, about to create it")
            os.makedirs(d_dir, exist_ok=True)
        else:
            pass

        os.chdir(d_dir)

        orig_clusters_comb = os.path.join(d_dir, "Combined_OrthoDB.orig.fa")
        single_cluster = map_retrieve(ncbi_id=ncbi_id, w_dir=d_dir, orig_clusters_comb=orig_clusters_comb)
       
        if not os.path.exists(orig_clusters_comb):
            print("No OrthoDB data found for " + str(ncbi_id))
            sys.exit(1)
        

        ## Process the Combined cluster DB fasta to sort out headers. Retaining unique orthoDB seqIDs, but removing...
        ## redundancy and adding a counter when sequences are not unique to single OrthoDB clusters.
        # Define file paths
        dedup_out_temp = f"{d_dir}/Combined_OrthoDB_{ncbi_id}_no_dups.tmp"
        final_ortho_fasta = f"{d_dir}/Combined_OrthoDB_{ncbi_id}_final.out.fa"
        reheader_out = f"{d_dir}/Combined_OrthoDB_{ncbi_id}_reheaded.fa.tmp"

        if os.path.exists(dedup_out_temp):
            os.remove(dedup_out_temp)

        if os.path.exists(final_ortho_fasta):
            os.remove(final_ortho_fasta)

        # Remove duplicate sequences from the original cluster file
        print(f"Removing duplicate sequences from {orig_clusters_comb}")
        try:
            mp.remove_dup_seqs(orig_clusters_comb, dedup_out_temp)
            print(f"Remove duplicates successful. Output saved to {dedup_out_temp}")
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to remove duplicates.")
        
        # Process deduplicated sequences to create a reheadered OrthoDB fasta file
        print("Processing deduplicated seq headers, isolating to unique OrthoDB gene ID...")

        try:
            mp.rehead_fasta(dedup_out_temp,final_ortho_fasta)
            print(f"Reheading successful. Output saved to {final_ortho_fasta}")
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to rehead.")
        
        # Create a samtools index file
        print(f"Creating samtools index of {final_ortho_fasta}")
        samtools_command = f"samtools faidx {final_ortho_fasta}"
        try:
            subprocess.run(samtools_command, shell=True, check=True)
            print(f"Samtools index creation successful for {final_ortho_fasta}")
        except subprocess.CalledProcessError as e:
            print(f"Error: Failed to create Samtools index for {final_ortho_fasta}")

        # Clean up temporary files
        for filename in os.listdir(d_dir):
            if filename.endswith(".tmp"):
                os.remove(os.path.join(d_dir, filename))
        os.remove(orig_clusters_comb)