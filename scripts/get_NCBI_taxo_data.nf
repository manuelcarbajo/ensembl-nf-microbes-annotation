#!/embl-nf-microbes-annotationsr/bin/env nextflow


params.csv_file = '/hps/nobackup/flicek/ensembl/microbes/shared/genome_annotations/genomes.csv'
params.output_path = '/hps/nobackup/flicek/ensembl/microbes/shared/genome_annotations'
params.ncbi_config = '/nfs/production/flicek/ensembl/microbes/mcarbajo/Projects/ensembl-nf-microbes-annotation/config/ncbi_db.conf'
csv_file_ch = Channel.of(params.csv_file)
output_path_ch = Channel.of(params.output_path)
ncbi_conf_ch = Channel.of(params.ncbi_config)

// Define the process 'get_NCBI_taxonomy_data'
process get_NCBI_taxonomy_data {
    debug true

    // Define the input variables
    input:
    val csv_file
    val output_path
    val ncbi_conf

    // Define the output variable 'stdout'
    output:
    stdout

    // Script block to execute the process
    script:
    """
    python3 $WORK_DIR/scripts/get_NCBI_taxo_data.py  ${csv_file} ${output_path} ${ncbi_conf}
    """ 
   
}

// Main workflow
workflow {
    // Call the process 'get_NCBI_taxonomy_data' and pass the 'csv_file' directly as a string
    get_NCBI_taxonomy_data(csv_file_ch, output_path_ch, ncbi_conf_ch)
}

