Farm_blast
==========

Python3 module to run blast+ or blastall in parallel on an LSF compute farm

Installation
------------

Prerequistes:
  * [NCBI BLAST] [NCBI BLAST] blast+, and optionally blastall, installed and their commands in your path
  * [Fastaq] [Fastaq] >= v0.1
  * [Farmpy] [Farmpy] >= v0.2

Once the preequisites are installed, run the tests:

    python3 setup.py test

Note that the tests check that blast+ is installed, but not blastall because it is optional.
If all was OK, then install:

    python3 setup.py install

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
[Fastaq]: https://github.com/sanger-pathogens/Fastaq
[Farmpy]: https://github.com/sanger-pathogens/Farmpy
