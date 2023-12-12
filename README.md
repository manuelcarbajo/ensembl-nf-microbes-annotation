# ensembl-nf-microbes-annotation
This repo hosts the nextflow code necessary to annotate in bulk microbial genbomes.
The script that runs the actual annotation  was developped by the gene-build team and can be found in https://github.com/Ensembl/ensembl-anno/ensembl_anno.py 

## Prerequisites
Pipelines are intended to be run inside the Ensembl production environment.
Please, make sure you have all the proper credential, keys, etc. set up.

### Getting this repo

```
git clone git@github.com:manuelcarbajo/ensembl-nf-microbes-annotation
```

### Configuration

#### Refresing environment

This project uses nextflow-22.10.1 and can be loaded with: 

module load nextflow-22.10.1-gcc-11.2.0-ju5saqw


### Initialising and running the environment

After downloading the ensembl-nf-microbes-annotation define your WORK_DIR (path to ensembl-nf-microbes-annotation git repo), ENSEMBL_ROOT_DIR (path to your other ensemb git repositories) and diamond_path (the path to the copy of uniprot_euk.fa.dmnd database)

Place a tab separated list of genomes to annotate in "$WORK_DIR/data/genomes_list.csv"  
(following the template in "$WORK_DIR/data/genomes_list_template.csv")  

  GENOME_NAME	TAX_ID	ENA_ACCESSION  
  Place here a tab separated list of genomes to process.  
  Example:  
  toxoplasma_gondii_ME49	508771	GCA_000006565.2  
  tripanosoma_cruzi	5693	GCA_003719455.1  

Make sure to rename the file "genomes_list.csv"  

#### Run the setup.sh script
Execute:
```
source setup.sh
```

#### Run the nextflow pipeline 
Use the command:
```
nextflow run microbes_annotation.nf  --output_path "path_to_your_output_publishDir"
```
