Farm_blast
==========

Python3 module to run blast+ or blastall in parallel on an LSF compute farm

Installation
------------

Prerequisites:
  * [NCBI BLAST] [NCBI BLAST] blast+, and optionally blastall, installed and their commands in your path

Once the prerequisites are installed, install with pip:

    pip3 install farm_blast

Synopsis
--------

Compare a query and a reference using blast+ blastn:

    farm_blast reference.fasta query.fasta

Compare a query and a reference using blastall blastn:

    farm_blast --blastall reference.fasta query.fasta

Run blast+ megablast:

    farm_blast --blast_type megablast reference.fasta query.fasta

Run blastall tblastx:

    farm_blast --blast_type tblastx --blastall reference.fasta query.fasta

Set the e-value and word length and do not filter the query sequence:

    farm_blast --no_filter -e 0.1 -W 30 reference.fasta query.fasta

To get all the options, use --help:

    farm_blast --help

[NCBI BLAST]: http://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Web&PAGE_TYPE=BlastDocs&DOC_TYPE=Download
