#!/embl-nf-microbes-annotationsr/bin/env nextflow

/*
 * Define the default parameters
 */

params.csv_file = "$baseDir/data/genomes_list.csv"
params.output_path = "$baseDir/data/genome_annotations"
params.ncbi_config = "$baseDir/config/ncbi_db.conf"

csv_file_ch = Channel.of(params.csv_file)
output_path_ch = Channel.of(params.output_path)
ncbi_conf_ch = Channel.of(params.ncbi_config)
 
log.info """\

    M I C R O B E S  A N N O T A T I O N - N F   P I P E L I N E
    ===================================
    "csv_file" file with list of genomes to process: ${params.csv_file}
    "output_path" path to print out the results: ${params.output_path}
    "ncbi_config" file with the connexion parameters to NCBI taxonomy mysql db: ${params.ncbi_config}

    """
    .stripIndent()

// Define the process 'get_NCBI_taxonomy_data'
process get_NCBI_taxonomy_data {
    debug true

    // Define the input variables
    input:
    path csv_file 
    path output_path 
    path ncbi_conf

    // Define the output variable 'stdout'
    output:
    stdout

    // Script block to execute the process
    script:
    """
    mkdir -p ${output_path}
    python3 ${baseDir}/scripts/get_NCBI_taxo_data.py ${baseDir}/data/${csv_file} ${baseDir}/data/${output_path} ${baseDir}/config/${ncbi_conf}
    """ 
}

process get_UniProt_data {
    debug true

    input:
    path genome_path

    output:
    stdout

    script:
    """
    python3 ${baseDir}/scripts/get_UniProt_data.py ${genome_path}
    """
}

// Main workflow
workflow {
    get_NCBI_taxonomy_data(csv_file_ch, output_path_ch, ncbi_conf_ch)
    
    genome_paths_ch = Channel.fromPath( "data/genome_annotations/*/tax_ranks.txt" )
 
    genome_paths_ch.view().each {
        path ->
        get_UniProt_data(path)
    }
}

