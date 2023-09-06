#!/embl-nf-microbes-annotationsr/bin/env nextflow

/*
 * Define the default parameters
 */

params.csv_file = "$baseDir/data/genomes_list.csv"
params.output_path = "$baseDir/genomes_output"
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

process get_NCBI_taxonomy_data {
    debug true
    publishDir "${params.output_path}", mode: 'copy'

    input:
    path csv_file 
    path output_path 
    path ncbi_conf

    output:
    path "genom_anno_dev/*", emit: genome_names
    
    script:
    """
    mkdir -p ${output_path}
    python3 ${baseDir}/scripts/get_NCBI_taxo_data.py ${baseDir}/data/${csv_file} ${baseDir}/data/${output_path} ${baseDir}/config/${ncbi_conf}
    """ 
}

process get_UniProt_data {
    debug true
    publishDir "${params.output_path}/genom_anno_dev", mode: 'copy'

    input:
    path genome_names

    output:
    path "${genome_names}/*_uniprot.fa", emit: uniprot_fa

    script:
    """
    python3 ${baseDir}/scripts/get_UniProt_data.py ${genome_names}
    """
}

workflow {
    def ncbi_ch = get_NCBI_taxonomy_data(csv_file_ch, output_path_ch, ncbi_conf_ch)

    get_UniProt_data( get_NCBI_taxonomy_data.out.genome_names.flatten() )
}


