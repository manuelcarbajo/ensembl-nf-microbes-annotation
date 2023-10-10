import sys
import ast
import requests
import os
import subprocess
from datetime import datetime
import my_process as mp


def query_OrthoDB(tax_ranks, baseDir):
    data_found = False
    for l in range(1,4):
        current_name = "level_" + str(l) + "_name"
        current_tax = "level_" + str(l) + "_tax"
        if tax_ranks[current_name] and not data_found:
            g_name = tax_ranks[current_name]
            genome_name = mp.process_string(g_name)
            genome_tax = tax_ranks[current_tax]
            command = ["python3", baseDir + "/bin/download_orthodb_protset.py", str(genome_tax), baseDir]
            #command = ["python3", baseDir + "/bin/download_data_from_orthoDB.py", str(genome_tax), baseDir]
            try:
                subprocess.run(command, check=True)
                print("Command executed successfully for level " + str(l) + " " + genome_name + " " + str(genome_tax))
                data_found = True
            except subprocess.CalledProcessError as e:
                print("Error for level " + str(l) + " executing command '{command}' : {e}")
        elif data_found:
            break
         
if __name__ == "__main__":
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("** begin ORTHODB " + str(now) )
    if len(sys.argv) < 1:
        print("The path to the genome is missing as an argument.")
    else:
        genome_name = sys.argv[1]
        baseDir = sys.argv[2]
        print("       genome_name: " + genome_name )
        tr = mp.read_tax_rank(genome_name)
        query_OrthoDB(tr, baseDir)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("** end ORTHODB " + str(now) )
