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
rfam_conf_ch = Channel.of(params.rfam_config).first() 


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
    python3 ${baseDir}/scripts/ncbi_taxo_data.py ${baseDir}/data/${csv_file} ${baseDir}/data/${output_path} ${baseDir}/config/${ncbi_conf} ${baseDir}
    """ 
}

process get_genome_assembly {
    debug true
    publishDir "${params.output_path}/genome_anno", mode: publishDir_mode

    input:
    tuple val(genome), path(genome_folder)

    output:
    tuple val(genome), path ("${genome_folder}/*_reheaded_assembly.fa"), emit: assembly_fa

    script:
    """
    python3 ${baseDir}/scripts/genome_assembly.py ${genome} ${baseDir} "${params.output_path}/genome_anno"
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
    python3 ${baseDir}/scripts/uniprot_data.py ${genome} ${baseDir} "${params.output_path}/genome_anno"
    """
}

process get_OrthoDB_protset {
    debug true
    publishDir "${params.output_path}/genome_anno", mode: publishDir_mode

    input:
    tuple val(genome), path(genome_folder)
 
    output:
    tuple val(genome), path("${genome}/ncbi_id_*_sequences/*_final.out.fa"), path("${genome}/ncbi_id_*_sequences/*_final.out.fa.fai"), emit: orthodb_data
    
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
    tuple val(genome),path ("rfam_ids.txt"), emit: rfam_ids

    script:
    """
    python3 ${baseDir}/scripts/rfam_accessions.py ${genome} ${baseDir}/config/${rfam_conf}
    """
}

process get_RNA_csv {
    debug true
    publishDir "${params.output_path}/genome_anno", mode: publishDir_mode

    input:
    tuple val(genome), path(genome_dir)
    
    output:
    tuple val(genome), path("${genome}/*_rna.csv"), path(genome_dir), emit: rna_csv

    script:
    """
    python3 ${baseDir}/scripts/rna_seq.py ${genome} ${baseDir} ${genome_dir}
    """
    
}

process download_fastq_files {
    maxForks 40
    errorStrategy 'retry'
    maxRetries 5
    debug true
    publishDir "${params.output_path}/genome_anno", mode: publishDir_mode

    input:
    tuple val(genome), val(fastq_file), path(genome_dir)

    output:
    tuple val(genome),path("${genome}/short_read_fastq_dir/*.fastq.gz"),emit: short_read_fastq_dir
    
    script:
    """
    python3 ${baseDir}/scripts/fastq_download.py ${genome_dir} ${fastq_file} ${baseDir}
    """ 
}

process run_ensembl_annotation {
    debug true
    publishDir "${params.output_path}/genome_anno/${genome}", mode: publishDir_mode

    input:
    tuple val(genome), path(genome_dir),path(rfam_ids),path(uniprot_fa),path(uniprot_fai),path(ortho_db_fa),path(ortho_db_fai),val(short_read_fastq_dir), path(genome_assembly)

    output:
    tuple val(genome), path("all_anno_outputs/",type: 'dir'),emit: output_dirs 
    tuple val(genome), path("ensembl_anno.log"),emit: anno_log

    script:
    """
    export ENSCODE=${baseDir}/frameworks
    source ${baseDir}/bin/locale_perl_setup.sh
    python3 ${baseDir}/scripts/ensembl_anno.py ${genome} ${genome_dir} ${rfam_ids} ${uniprot_fa} ${uniprot_fai} ${ortho_db_fa} ${ortho_db_fai} ${short_read_fastq_dir} ${baseDir} ${genome_assembly}
    mkdir all_anno_outputs
    mv *_output/ all_anno_outputs
    """
}


process run_annotation {
    debug true
    publishDir "${params.output_path}/genome_anno/${genome}", mode: 'copy'

    input:
    val(genome)

    output:
    tuple val(genome), path("all_anno_outputs/",type: 'dir'),emit: output_dirs
    tuple val(genome), path("anno.log"),emit: anno_log

    script:
    """
    echo "import os;import sys;genome = sys.argv[1];os.makedirs('busco_output', exist_ok=True);open('busco_output/foofile.txt', 'w').close();os.makedirs('annotation_output', exist_ok=True);open('annotation_output/somefile.txt', 'w').close();open('anno.log', 'w').write(genome);print('Current Directory:', os.getcwd())" > create_foo_folders.py
    python create_foo_folders.py "${genome}"
    mkdir all_anno_outputs
    mv *_output/ all_anno_outputs
    echo publish_dir files:
    echo "${params.output_path}/genome_anno/genome"
    """
}



workflow {
     
    def ncbi_ch = get_NCBI_taxonomy_data(csv_file_ch, output_path_ch, ncbi_conf_ch)
    
    def genomes_ch = get_NCBI_taxonomy_data.out.genomes
                          .flatten()
                          .map{ genome_path -> tuple( genome_path.getBaseName(2), genome_path) }

    assembly_ch = get_genome_assembly(genomes_ch)     
    orthodb_ch = get_OrthoDB_protset(genomes_ch)
    uniprot_ch = get_UniProt_data(genomes_ch)
    rfam_ch = get_Rfam_accessions(genomes_ch, rfam_conf_ch)
    
    get_RNA_csv(genomes_ch)
    rna_fastq_files_ch = get_RNA_csv.out.rna_csv
				.splitCsv(elem: 1, header: false, sep: '\t' )
				.map{row -> tuple (row[0],row[1][3],row[2])}
							
    download_fastq_files(rna_fastq_files_ch)
    fastq_ch = download_fastq_files.out.short_read_fastq_dir
				    .map{it -> tuple(it[0],"short_read_fastq_dir") }
    
    joined_ch = genomes_ch.join(rfam_ch, remainder:true).join(uniprot_ch, remainder:true).join(orthodb_ch,remainder:true).join(fastq_ch).join(assembly_ch)
    joined_ch.view()
    
    run_ensembl_annotation(joined_ch)

    /*
    foo_ch = Channel.from("malassezia globosa")
    run_annotation(foo_ch)
    */
}


