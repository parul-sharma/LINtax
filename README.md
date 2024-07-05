# Creating LIN taxonomy for metagenomic classification

Run:
```
creating-taxonomy-files.py input.txt
```
which will produce:
* `names.dmp` - NCBI format custom taxonomy for LINS produced from input.txt
* `nodes.dmp` - NCBI format custom taxonomy file #2
* `data.txt` - intermediate debugging/tracking format, used by header changing script

## running the pipeline

You can run the whole pipeline like so:

```
./LIN-kraken-db-pipeline.sh input.txt xyz 
```

Then add the above taxonomy to a custon database for Kraken2, like so:
```
for i in xyz/genomes_taxids/*.fna;
do
   kraken2-build --add-to-library $i --db xyz;
done
```
and build the kraken2 database like so:
```
kraken2-build --build --db xyz
```
then run like so:
```
kraken2 --db xyz metagenome_input.fastq
```
```
LINtax: Create custom taxonomy for metagenome classification

    This is LINtax version $version
    Usage: $0 <command> [options]"
    Commands:
    create  - Create LINtax from input file and genomes directory
        Options:
        -i  or   --input          Specify input file [REQUIRED]
        -g  or   --genomes        Specify directory containing input genomes [REQUIRED]
        -o  or   --output         Name and path of output directory [REQUIRED]
        Other options:
        --download_genomes        Download assemblies listed in input file from NCBI
        -h  or --help             Show usage
        Example: lintax create -i linfile.tsv -g /path/to/dir -o /path/to/output

    build - Build the database using the output from 'lintax create'
        Options:
        -i  or  --input           Specify the output directory from 'lintax create' 
        [REQUIRED]                This folder should include the modified genomes directory as well as 
                                  the taxonomy directory with the necessary files
        -h  or --help             Show usage
        Example: lintax build -i /output/from/create 
    
    classify - classify your metagenomic reads using the provided lintax database
        Options:
        --db                      lintax Database to use for classifications (make sure to run build before this step) [REQUIRED]       
        -o  or --output           LINreport containing the results [REQUIRED]
        -h or --help              show usage
        Other options:
        -c or --confidence        specify the confidence threshold for kraken classification [recommended]
        --paired                  for paired-end reads
        Example: for single reads - 
        lintax classify --db /database/ -o sample-results.tsv <sample.fastq>
        for paired reads - 
        lintax classify --db /database/ -o sample-results.tsv  --paired <sample_1.fastq> <sample_2.fastq>

    report  - Generate a final LIN using the results from classification
        Options:
        -ko  or  --koutput        defualt output file from kraken2 [REQUIRED]
        -kr  or  --kreport        report format output from kraken2 [REQUIRED]
        -o  or --output           LINreport containing the results [REQUIRED]
    help     Show help
    ```