# ensembl-nf-microbes-annotation
This repo hosts the nextflow code necessary to annotate in bulk microbial genbomes.
The script that runs the actual annotation  was developped by the gene-build team and can be found in https://github.com/Ensembl/ensembl-anno/ensembl_anno.py 

## Prerequisites
Pipelines are intended to be run inside the Ensembl production environment.
Please, make sure you have all the proper credential, keys, etc. set up.

### Getting this repo

```
git clone git@github.com:Ensembl/ensembl-nf-microbes-annotation
```

### Configuration

#### Refresing environment

This project uses nextflow-22.10.1 and can be loaded with
module load nextflow-22.10.1-gcc-11.2.0-ju5saqw
#   Version: 22.10.1 build 5828                                             
#   Created: 27-10-2022 16:58 UTC (17:58 BST)
#   System: Linux 4.18.0-348.20.1.el8_5.x86_64
#   Runtime: Groovy 3.0.13 on OpenJDK 64-Bit Server VM 16.0.2+7-67
#   Encoding: UTF-8 (UTF-8)

### Initialising and running the environment

export PATH="path_to_git_hub_repo/ensembl-nf-microbes-annotation:$PATH" 
export WORK_DIR="path_to_git_hub_repo/ensembl-nf-microbes-annotation"

cd "path_to_git_hub_repo/ensembl-nf-microbes-annotation"

nextflow run get_NCBI_taxo_data.nf --csv_file "path_to_data_dir/genomes.csv" --output_path "path_to_output_dir" --ncbi_config "path_to_git_hub_repo/ensembl-nf-microbes-annotation/config/ncbi_db.conf"


