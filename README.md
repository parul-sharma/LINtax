# LIN parsing code for kraken2

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
./LIN-kraken-db-pipeline.sh $(pwd)/input.txt xyz 
```

Then add the genomes to the taxonomy like so:
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
