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

This project uses nextflow-22.10.1 and can be loaded with: 

module load nextflow-22.10.1-gcc-11.2.0-ju5saqw


### Initialising and running the environment

export WORK_DIR="path_to_git_hub_repo/ensembl-nf-microbes-annotation"
export PATH="$WORK_DIR:$PATH"

\#Place a tab separated list of genomes to annotate in "$WORK_DIR/data/genomes_list.csv" (following the template "$WORK_DIR/data/genomes_list_template.csv")

\#Make sure "$WORK_DIR/config/ncbi_db.conf" has the right credentials

cd $WORK_DIR

nextflow run get_NCBI_taxo_data.nf --csv_file "$WORK_DIR/data/genomes_list.csv" --output_path "path_to_output_dir" --ncbi_config "$WORK_DIR/config/ncbi_db.conf"


