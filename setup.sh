#bsub -Is -q production -M 50000 -n 50 -R"select[mem>50000] rusage[mem=50000]  span[hosts=1]" $SHELL

module load nextflow-22.10.1-gcc-11.2.0-ju5saqw

WORKDIR="path_to_your/ensembl-nf-microbes-annotation"
FRAMEWORKS=$WORKDIR/frameworks

#ENSEMBL_ROOT_DIR="define_your_own_path_to_Ensembl_git_repos"
cd $ENSEMBL_ROOT_DIR
declare -A GIT_REPOS_DICT=(
    ['ensembl']='https://github.com/Ensembl/ensembl.git'
    ['ensembl-hive']='https://github.com/Ensembl/ensembl-hive.git'
    ['ensembl-genes']='https://github.com/Ensembl/ensembl-genes.git'
    ['ensembl-anno']='https://github.com/Ensembl/ensembl-anno.git'
    ['ensembl-analysis']='https://github.com/Ensembl/ensembl-analysis.git'
    ['ensembl-variation']='https://github.com/Ensembl/ensembl-variation.git'
    ['ensembl-killlist']='https://github.com/Ensembl/ensembl-killlist.git'
)

for repo in "${!GIT_REPOS_DICT[@]}"; do
    # Check if the repository directory already exists
    if [ ! -d "$repo" ]; then
        # Clone the repository
        git clone "${GIT_REPOS_DICT[$repo]}"
    else
        echo "${GIT_REPOS_DICT[$repo]}" repo already exist
    fi

    # Create the symlink if it doesn't already exist
    symlink_target_path="$FRAMEWORKS/$repo"
    source_path="$ENSEMBL_ROOT_DIR/$repo"
    if [ ! -e "$symlink_target_path" ]; then
        ln -s "$source_path" "$symlink_target_path"
        echo "Symlink created for '$repo'."
    else
        echo "Symlink already exist for '$repo'."
    fi
done

cd ${WORKDIR}
#define path to uniprot_euk.fa.dmnd and add symlink or download a copy into ${WORKDIR}/data/
diamond_source_path="/hps/nobackup/flicek/ensembl/genebuild/blastdb/uniprot_euk_diamond/uniprot_euk.fa.dmnd"
diamond_target_path="${WORKDIR}/data/uniprot_euk.fa.dmnd""
ln -s "$diamond_source_path" "$diamond_target_path"

export BIOPERL_LIB="/hps/software/users/ensembl/ensw/C8-MAR21-sandybridge/linuxbrew/opt/bioperl-169/libexec"
export PERL5LIB=${WORKDIR}/bin:${WORKDIR}/frameworks/ensembl/modules:${WORKDIR}/frameworks/ensembl-analysis/modules:${WORKDIR}/frameworks/ensembl-analysis/scripts:${WORKDIR}/frameworks/ensembl-analysis/scripts/buildchecks/:${WORKDIR}/frameworks/ensembl-hive/modules:${WORKDIR}/frameworks/ensembl-hive/:${WORKDIR}/frameworks/ensembl-variation/modules:$BIOPERL_LIB
export PYTHONPATH=${WORKDIR}/bin:$PYTHONPATH:${FRAMEWORKS}/ensembl-genes/ensembl_genes:${WORKDIR}/scripts

TEAM=microbes
LOCAL_PYENV=1
export PYENV_ROOT="/path_to_microbes_pyenv"
conda activate microbes_gb
PYENV_VIRTUALENV_DISABLE_PROMPT=1

export PATH="${WORKDIR}:${WORKDIR}/bin:$PATH" 


#nextflow run microbes_annotation.nf  --output_path "/hps/nobackup/flicek/ensembl/microbes/shared/genome_annotations" 
