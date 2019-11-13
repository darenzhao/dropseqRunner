
import os
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--fasta', type=str, help='Genome fasta file in gzip format.')
    parser.add_argument('--gtf', type=str, help='Genome annotations in GTF format.')
    parser.add_argument('--outDir', type=str, help='Output directory of of genome index')
    parser.add_argument('--cluster', type=str, help='Will this run on SLURM cluster? Options: yes or no. Default: no.')
    args = parser.parse_args()
    
    if args.fasta == None or args.gtf == None:
      msg='Please provide a valid gzippzed fasta file, and a genome annotation file in GTF format.'
      raise Exception(msg)
      
    if args.cluster == None:
      args.cluster = 'no'
    
    if os.path.exists('STAR_indeces/'):
      os.system('rm -r STAR_indeces/')
    
    print('Setting up directory and creating auxililary files..')
    os.system('mkdir STAR_indeces')
    os.system(f'source activate dropRunner; gtfToGenePred {args.gtf} tmp -genePredExt')
    cmd = """awk '{print $12"\t"$0}' tmp | cut -f1-11 > STAR_indeces/refFlat_for_picard.refFlat; rm tmp"""
    os.system(cmd)
    
    if args.cluster == 'yes':
      
        cmd =f"""#!/bin/bash

#SBATCH --job-name=genome_index
#SBATCH --output=genome_index.log
#SBATCH --error=genome_index.error
#SBATCH --time=10:00:00
#SBATCH --partition=broadwl
#SBATCH --mem=32G
#SBATCH --tasks-per-node=4

source activate dropRunner
STAR --runThreadN 4 --runMode genomeGenerate --genomeDir STAR_indeces/ --genomeFastaFiles {args.fasta} --sjdbGTFfile {args.gtf} --sjdbOverhang 74
"""

        with open('generate_indeces.sbatch', 'w') as f:
            f.write(cmd)
        
        os.system('sbatch generate_indeces.sbatch')
        print('Index generation has been submitted to the cluster. Type qstat -u CNETID to check the status.')
    
    else:
      
      print('Genome index generation will run locally on this machine. This may not complete due to STARs large memory requirement.')
      os.system(f'source activate dropRunner; STAR --runThreadN 1 --runMode genomeGenerate --genomeDir STAR_indeces/ --genomeFastaFiles {args.fasta} --sjdbGTFfile {args.gtf} --sjdbOverhang 59')