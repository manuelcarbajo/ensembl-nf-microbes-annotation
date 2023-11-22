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


publishDir_mode = 'copy' //change this to 'copy'to run in production mode 'symlink' to run in development mode

log.info """

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
    publishDir "${params.output_path}/", mode: publishDir_mode

    input:
    path csv_file 
    path output_path 
    path ncbi_conf

    output:
    path("genome_anno/*"), emit: genomes
    
    script:
    """
    mkdir -p ${output_path}
    python3 ${baseDir}/scripts/ncbi_taxo_data.py ${baseDir}/data/${csv_file} ${baseDir}/data/${output_path} ${baseDir}/config/${ncbi_conf}
    """ 
}

process get_UniProt_data {
    debug true
    publishDir "${params.output_path}/genome_anno", mode: publishDir_mode

    input:
    tuple val(genome), path(genome_folder)
     
    output:
    tuple val(genome), path ("${genome_folder}/*_uniprot_proteins.fa"), path("${genome_folder}/*_uniprot_proteins.fa.fai"), emit: uniprot_data

    script:
    """
    echo  "Processing g_name: $genome with path: ${genome_folder} "   
    python3 ${baseDir}/scripts/uniprot_data.py ${genome} ${baseDir} "${params.output_path}/genome_anno"
    """
}

process get_OrthoDB_protset {
    debug true
    publishDir "${params.output_path}/genome_anno/${genome}", mode: publishDir_mode

    input:
    tuple val(genome), path(genome_folder)
 
    output:
    tuple val(genome), path("ncbi_id_*_sequences/*_final.out.fa"), path("ncbi_id_*_sequences/*_final.out.fa.fai"), emit: orthodb_data, optional: true
    
    script:
    """
    python3 ${baseDir}/scripts/orthoDB_protset.py ${genome} ${baseDir}
    """
}


process get_Rfam_accessions {
    debug true
    publishDir "${params.output_path}/genome_anno/${genome}", mode: publishDir_mode

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
    publishDir "${params.output_path}/genome_anno/${genome}", mode: publishDir_mode

    input:
    tuple val(genome), path(genome_dir)
    
    output:
    tuple val(genome), path("*_rna.csv"), emit: rna_csv

    script:
    """
    python3 ${baseDir}/scripts/rna_seq.py ${genome} ${baseDir}
    """
    
}

process download_fastq_files {
    maxForks 40
    errorStrategy 'retry'
    maxRetries 3
    debug true
    publishDir "${params.output_path}/genome_anno/${genome}/short_read_fastq_dir", mode: publishDir_mode

    input:
    tuple val(genome), val(fastq_file)

    output:
    tuple val(genome),path("*fastq*"), emit: short_read_fastq_dir

    script:
    """
    python3 ${baseDir}/scripts/fastq_download.py ${genome} ${fastq_file} ${baseDir}
    """ 
}

process run_ensembl_anno {
    debug true
    publishDir "${params.output_path}/genome_anno/${genome}", mode: publishDir_mode

    input:
    tuple val(genome), path(genome_folder)
    //tuple val(genome), path(genome_folder)
    //tuple val(genome), path(genome_dir)
    tuple val(genome), path(fastq_folder)

    output:
    stdout
    //path("${genome}/*anno*"), emit: annotation

    script:
    """
    ls -li "${genome_dir}/short_read_fastq_dir"	
    """
}


workflow {
    def ncbi_ch = get_NCBI_taxonomy_data(csv_file_ch, output_path_ch, ncbi_conf_ch)
    def genomes_ch = get_NCBI_taxonomy_data.out.genomes
                          .flatten()
                          .map{ genome_path -> tuple( genome_path.getBaseName(2), genome_path) }
		    
    uniprot_ch = get_UniProt_data(genomes_ch)
    orthodb_ch = get_OrthoDB_protset(genomes_ch)
    rfam_ch = get_Rfam_accessions(genomes_ch, rfam_conf_ch) 
    
    get_RNA_csv(genomes_ch)
    
    rna_fastq_files_ch = get_RNA_csv.out.rna_csv
				.splitCsv(elem: 1, header: false, sep: '\t' )
				.map{row -> tuple (row[0],row[1][3])}
							
    fastq_ch = download_fastq_files(rna_fastq_files_ch)
    rfam_ch.concat(orthodb_ch,rna_fastq_files_ch,fastq_ch).view()
    //run_ensembl_anno(rfam_ch)
}


