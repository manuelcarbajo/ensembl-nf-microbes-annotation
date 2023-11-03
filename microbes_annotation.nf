#!/embl-nf-microbes-annotationsr/bin/env nextflow

/*
 * Define the default parameters
 */

params.csv_file = "$baseDir/data/genomes_list.csv"
params.output_path = "$baseDir/genomes_output"
params.ncbi_config = "$baseDir/config/ncbi_db.conf"
params.rfam_config = "$baseDir/config/rfam_db.conf"

csv_file_ch = Channel.of(params.csv_file)
output_path_ch = Channel.of(params.output_path)
ncbi_conf_ch = Channel.of(params.ncbi_config)
rfam_conf_ch = Channel.of(params.rfam_config) 


log.info """\

    M I C R O B E S  A N N O T A T I O N - N F   P I P E L I N E
    ===================================
    "csv_file" file with list of genomes to process: ${params.csv_file}
    "output_path" path to print out the results: ${params.output_path}
    "ncbi_config" file with the connexion parameters to NCBI taxonomy mysql db: ${params.ncbi_config}
    "rfam_config" file with the connexion parameters to Rfam mysql db: ${params.rfam_config}

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
    python3 ${baseDir}/scripts/ncbi_taxo_data.py ${baseDir}/data/${csv_file} ${baseDir}/data/${output_path} ${baseDir}/config/${ncbi_conf}
    """ 
}

process get_UniProt_data {
    debug true
    publishDir "${params.output_path}/genom_anno_dev", mode: 'copy'

    input:
    path genome_names
    
    output:
    path "${genome_names}/*_uniprot_proteins.fa", emit: uniprot_fa
    path "${genome_names}/*_uniprot_proteins.fa.fai", emit: uniprot_fai
    path genome_names, emit:genome_dir
    
    script:
    """
    python3 ${baseDir}/scripts/uniprot_data.py ${genome_names} ${baseDir} "${params.output_path}/genom_anno_dev"
    """
}

process get_OrthoDB_protset {
    debug true
    publishDir "${params.output_path}/genom_anno_dev/${genome_dir}", mode: 'copy'

    input:
    path genome_dir
 
    output:
    path "${genome_dir}/*_proteins.fa", emit: orthodb_fa
    path "${genome_dir}/*_proteins.fa.fai", emit: orthodb_fai
    
    script:
    """
    python3 ${baseDir}/scripts/orthoDB_protset.py ${genome_dir} ${baseDir}
    """
}


process get_Rfam_accessions {
    debug true
    publishDir "${params.output_path}/genom_anno_dev/${genome_dir}", mode: 'copy'

    input:
    path genome_dir
    path rfam_conf

    output:
    path "rfam_*_ids.txt", emit: rfam_ids 

    script:
    """
    python3 ${baseDir}/scripts/rfam_accessions.py ${genome_dir} ${baseDir}/config/${rfam_conf}
    """
}


process get_RNA_seq {
    debug true
    publishDir "${params.output_path}/genom_anno_dev/${genome_dir}", mode: 'copy'    

    input:
    path genome_dir
    
    output:
    path "*_rna.csv", emit: rna_csv
    path "short_read_fastq_dir", emit: short_read_fastq_dir

    script:
    """
    python3 ${baseDir}/scripts/rna_seq.py ${genome_dir} ${baseDir}
    """
}


workflow {
    def ncbi_ch = get_NCBI_taxonomy_data(csv_file_ch, output_path_ch, ncbi_conf_ch)

    get_UniProt_data( get_NCBI_taxonomy_data.out.genome_names.flatten() )
    
    get_OrthoDB_protset(get_UniProt_data.out.genome_dir)
   
    get_Rfam_accessions(get_UniProt_data.out.genome_dir, rfam_conf_ch) 

    get_RNA_seq(get_UniProt_data.out.genome_dir)
}


