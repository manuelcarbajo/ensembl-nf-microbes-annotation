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
    path("genom_anno_dev/*"), emit: genomes
    
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
    tuple val(genome), path(genome_folder)
     
    output:
    tuple val(genome), path ("${genome}/*_uniprot_proteins.fa"), path("${genome}/*_uniprot_proteins.fa.fai"), emit: uniprot_data

    script:
    """
    echo  "Processing g_name: $genome with path: ${genome_folder} "   
    python3 ${baseDir}/scripts/uniprot_data.py ${genome} ${baseDir} "${params.output_path}/genom_anno_dev"
    """
}

process get_OrthoDB_protset {
    debug true
    publishDir "${params.output_path}/genom_anno_dev/${genome}", mode: 'copy'

    input:
    tuple val(genome), path(genome_folder)
 
    output:
    tuple val(genome), path("*_proteins.fa"), path("*_proteins.fa.fai"), emit: orthodb_data
    
    script:
    """
    python3 ${baseDir}/scripts/orthoDB_protset.py ${genome} ${baseDir}
    """
}


process get_Rfam_accessions {
    debug true
    publishDir "${params.output_path}/genom_anno_dev/${genome_dir}", mode: 'copy'

    input:
    tuple val(genome), path(genome_dir)
    path rfam_conf

    output:
    path "rfam_*_ids.txt", emit: rfam_ids 

    script:
    """
    python3 ${baseDir}/scripts/rfam_accessions.py ${genome} ${baseDir}/config/${rfam_conf}
    """
}

process get_RNA_csv {
    debug true
    publishDir "${params.output_path}/genom_anno_dev/${genome_dir}", mode: 'copy'    

    input:
    tuple val(genome), path(genome_dir)
    
    output:
    tuple val(genome), path("../../../tripanosoma_cruzi_GCA_003719455_5693_rna.csv"), emit: rna_csv

    script:
    """
    echo "REMEBER to change output path of rna_csv to path _rna.csv and uncomment the script sectin of get_RNA_seq"
    """
    //python3 ${baseDir}/scripts/rna_seq.py ${genome} ${baseDir}
    
}

process download_fastq_files {
    debug true
    publishDir "${params.output_path}/genom_anno_dev/${genome_dir}", mode: 'copy'

    input:
    tuple val(genome), path(fastq_file)

    output:
    val(genome)

    script:
    """
    python3 ${baseDir}/scripts/fastq_download.py ${genome} ${fastq_file} ${baseDir}
    """ 
}

workflow {
    def ncbi_ch = get_NCBI_taxonomy_data(csv_file_ch, output_path_ch, ncbi_conf_ch)
    def genomes_ch = get_NCBI_taxonomy_data.out.genomes
                          .flatten()
                          .map{ genome_path -> tuple( genome_path.getBaseName(2), genome_path) }
    
    //get_UniProt_data(genomes_ch)
    //get_OrthoDB_protset(genomes_ch)
    //get_Rfam_accessions(genomes_ch, rfam_conf_ch) 
    get_RNA_seq(genomes_ch)
    rna_fastq_files_ch = get_RNA_csv.out.rna_csv
                          	.map { genome, csv -> csv}
         		   	.splitCsv(header: false, sep: '\t' )
                		.map{row -> row[3]}
				.flatten()
}


