# ontbc
Tools for oxford nanopore barcoding

## 1. Dependence
python 2.5 or higher (need matplotlib)   
[porechop](https://github.com/rrwick/Porechop) (required if you use barcode)  
SGE (optional)
## 2. Install
```commandline
git clone https://github.com/FlyPythons/ontbc.git
cd ontbc
chmod 755 ontbc.py && dos2unix ontbc.py
```

## 3. Usage
### 3.1 filter raw reads
use to filter ont reads with read_length and read_quality_score
```commandline
ontbc.py filter --fastq 1.fastq --summary 1.summary.txt \
--min_score 7 --min_length 1000 
```

### 3.2 barcoding 
use to ont reads barcoding
```commandline
ontbc.py barcode /path/to/cell/ --barcode BC01 BC02 BC03
```
