# LINtax: Custom taxonomy for metagenomic classification

## Installation:
To install LINtax simply clone this repository and add depencies through the yaml file provided. Use the following commands:
```
# clone repo
git clone https://github.com/parul-sharma/LINtax.git

# install dependencies using the conda recipe: 
conda env create -f lintax.yaml

# activate the environment
conda activate lintax

# add the lintax scripts to path variable
export PATH="LINtax/bin:$PATH" 

```
This last command allows you run the tool from any directory. 
###### .....conda recipe coming soon!
.....
## Usage:

```
lintax [command] <options>
Commands:
    create      - Create LIN taxonomy from a list of input genomes and their LINs
    build       - Build the database using the output from 'lintax create'
    classify    - Classify your metagenomic reads using the provided LINtax database
    report      - Generate a final LIN using the results from   classification
    help        - Show help
```
As shown above, there four main modules for lintax:
* `create` -Creates the custom taxonomy structure using from a given list of genomes and their LINs. For assigning LINs to genomes, use linflow (https://code.vt.edu/linbaseproject/LINflow) to run the CLI version or visit the website, GenomeRxiv (http://genomerxiv.cs.vt.edu) to directly download them. 

* `build` - Uses kraken2 commands to build the database using the custom taxonomy files created with the "create" step. It is essential to run create before running this module to get the necessary taxonomy structure.

* `classify` - Uses kraken2 algorithm to classify any input sequence (fasta or fastq; paired or unpaired) with the custom database created above. You can run kraken2 using your own paramaters as well, if you wish so. Remember to create both kraken2 default output and the report stype output for further analysis.

* `report` - Summarizes the results of Kraken2 in the LINgroup format. (No need to run this after classify. Only needed if using kraken2 directly ! )


### 1. Using `lintax create `
Creates the custom taxonomy structure using from a given list of genomes and their LINs.


```
Usage:
lintax create -i linfile.tsv -g /path/to/dir -o /path/to/output
        Options:
        -i  or   --input          Specify input file [REQUIRED]
        -g  or   --genomes        Specify directory containing input genomes [REQUIRED]
        -o  or   --output         Name and path of output directory [REQUIRED]
        Other options:
        --download_genomes        Download assemblies listed in input file from NCBI
        -h  or --help             Show usage
        Example: 
```
#### Required inputs 
`-i or --input` : The input file requied which lists the genomes and their corresponding LINs. 
For assigning LINs to genomes, use linflow (https://code.vt.edu/linbaseproject/LINflow) to run the CLI version or visit the website, GenomeRxiv (http://genomerxiv.cs.vt.edu) to directly download them. 

The input file must have a column 'LIN' and 'Accession'. 

Example input-file looks omething like this:


| LIN                               | Species              | Strain    | FileName                                         | Accession       |
|-----------------------------------|----------------------|-----------|--------------------------------------------------|-----------------|
| 14,1,0,0,0,0,0,0,0,0,6,0,1,0,1,0,0,0,0,0 | Ralstoniasolanacearum | OE1_1     | GCF_001879565.1_ASM187956v1_genomic.fna | GCF_001879565.1 |
| 14,1,0,0,0,0,0,0,0,0,6,0,1,0,0,0,0,0,0,0 | Ralstoniasolanacearum | PSS1308   | GCF_001870805.1_ASM187080v1_genomic.fna | GCF_001870805.1 |
| 14,1,0,0,0,0,0,0,0,0,2,1,0,0,0,0,0,0,0,0 | Ralstoniasolanacearum | FJAT_1458 | GCF_001887535.1_ASM188753v1_genomic.fna | GCF_001887535.1 |
| 14,1,0,0,0,0,0,0,0,0,2,0,0,4,4,0,0,0,0,0 | Ralstoniasolanacearum | Pe_13     | GCF_012062595.1_ASM1206259v1_genomic.fna | GCF_012062595.1 |

`Note`: If you wish to download the genome assemblies, run the above command with the `--download_genomes` option and then run the analysis again. 

`-g or --genomes`: directory of the downloaded genomes or the directory where you want to download the genomes (when `--download_genomes` is specified.)

#### Description of output
The output of the `create` command produces the following file strcuture:
```
output_dir    
    │
    └───genome_with_taxids
    │ 
    └───taxonomy 
        │     
        └───nodes.dmp     
        └───names.dmp
        └───data.txt

```

- `names.dmp` : stores all tax ranks and their names
- `nodes.dmp` : stores all the heirarchial relations between different ranks
- `data.txt` - intermediate file used by other scripts 
- `genome_with_taxids` : directory that contains a copy of all input genomes with *custom taxonomy IDs* included in the headers of each contigs. This helps to build the custom databases using the **new** assigned taxonomy IDs.

### 2. Using `lintax build `

Build the database using the output from `lintax create`
```        
Usage:
lintax build -i /path/to/dir_with_tax 
        Options:
        -i  or  --input           Specify the dir created with 'lintax create' 
        [REQUIRED]                This folder should include the modified genomes directory as well as 
                                  the taxonomy directory with the necessary files
        -h  or --help             Show usage
    
```

This command runs `kraken2 build` command in the background and necessary database files are created in the same directory as the input directory provided. 

#### Required inputs 
`-i or --input` : The input directory which should be the output produced in the previous step. This directory should include the `genomes_with_taxids` and the `taxonomy` folders with the necessary files. 

#### Description of output
The output of the `lintax build` command are the indexed database files buidl with the user-input genomes and the new taxonomy, neccesaary for carrying out classifications.

### 3. Using `lintax classify `
Classify your metagenomic reads using the lintax database:
```
Usage: 
lintax classify --db /database/ -o sample-results.tsv <sample.fastq>

For paired reads - 
lintax classify --db /database/ -o sample-results.tsv  --paired <sample_1.fastq> <sample_2.fastq>
        
        Options:
        --db                      LINtax Database to use for classifications (make sure to run build before this step) [REQUIRED]
        --lins                    Text file containing lingroups (custom taxa) and their LIN prefixes [REQUIRED]
        -o  or --output           LINreport containing the results [REQUIRED]
        -h  or --help             Show usage
        Other options:
        -c  or --confidence       Specify the confidence threshold for kraken classification [optional]

```
#### Required inputs 
`--db` : specify the database direcotry that contains the necessary files as well as the taxonomy folder (needed for creating the final report).

`--lins` : text file containing the sub-species groups you are interested to identify in the metagenome, along with the LIN prefix. Example text file:
| LINgroup_Name            | LINgroup_prefix           |
|--------------------------|---------------------------|
| A_Total_reads;B_grpA    | 14,1,0,0,0,0,0,0,0,0      |
| A_Total_reads;B_grpA;C_subgrpB | 14,1,0,0,0,0,0,0,0,0,3 |
| A_Total_reads;B_grpA;C_subgrpC | 14,1,0,0,0,0,0,0,0,0,2 |

In this file, the groups follow a taxonomic convection A,B,C,D and so on. The naming convention follows the Group ID followed by the group name such as A_total_reads or B_grpA etc. Adding the lineage using this naming convention helps in the visualization of the results.

`-o  or --output` : name of the final report file and path

`-c or --confidence` : specify the confidence scroring threshold. Recommended 0.1 (10%) for long reads and 0.3 (30%) or more for short reads. 
[Read more about confidence thresholds : (https://github.com/DerrickWood/kraken2/wiki/Manual#confidence-scoring)

#### Description of output
The output is a tab-seprated final report that includes the classification results with the following columns:
- `LINgroup_Name`: lingroup name as in the provided `lins` file
- `LINgroup_prefix`: lingroup prefix as specifed in the `lins` file
- `Assigned_reads`: total number of assigned reads for that lingroup 
- `Percentage_assigned_reads`: percentage of assigned reads
- `Unique_Assigned_reads`: number of unique reads assigned to only that lingroup
- `Percentage_unique_assigned_reads`: percentage of unique reads
- `Total_reads_length`: total read length of the assigned reads (important for long-read assignments)

### 3. Using `lintax report `
Generate LINtax report from kraken outputs
```
Usage:

lintax report -ko <kraken_output> -kr <kraken_report> -o <lin-report>
        Options:
        -ko  or  --koutput        defualt output file from kraken2 [REQUIRED]
        -kr  or  --kreport        report format output from kraken2 [REQUIRED]
        -o  or --output           LINreport containing the results [REQUIRED]
```
NOTE: No need to run this after `lintax classify`. 
You can use `lintax report` if you ran your own kraken2 commands for classification. (Still using the lintax database).
- `-ko  or  --koutput`: kraken2 default output generated during classification
- `-kr  or  --kreport`: kraken2 report generated using the --report option
- `-o or --output`: specify the name and path of the final report.

The final report is generated similar to the result from `lintax classify`. 






