# Farm_blast
Run blast+ or blastall in parallel on an LSF compute farm.

[![Build Status](https://travis-ci.org/sanger-pathogens/Farm_blast.svg?branch=master)](https://travis-ci.org/sanger-pathogens/Farm_blast)   
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-brightgreen.svg)](https://github.com/sanger-pathogens/Farm_blast/blob/master/LICENSE) .  
[![Docker Build Status](https://img.shields.io/docker/cloud/build/sangerpathogens/farm_blast.svg)](https://hub.docker.com/r/sangerpathogens/farm_blast)  
[![Docker Pulls](https://img.shields.io/docker/pulls/sangerpathogens/farm_blast.svg)](https://hub.docker.com/r/sangerpathogens/farm_blast)  
[![codecov](https://codecov.io/gh/sanger-pathogens/Farm_blast/branch/master/graph/badge.svg)](https://codecov.io/gh/sanger-pathogens/Farm_blast) 

## Contents
  * [Introduction](#introduction)
  * [Installation](#installation)
    * [Required dependencies](#required-dependencies)
    * [Optional dependencies](#optional-dependencies)
    * [Using pip](#using-pip)
    * [Running the tests](#running-the-tests)
  * [Usage](#usage)
  * [License](#license)
  * [Feedback/Issues](#feedbackissues)

## Introduction
Python3 module to run blast+ or blastall in parallel on an LSF compute farm.

## Installation
Farm_blast has the following dependencies:

### Required dependencies
  * [blast+](http://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Web&PAGE_TYPE=BlastDocs&DOC_TYPE=Download)
  * [fastaq](https://github.com/sanger-pathogens/Fastaq)
### Optional dependencies
  * blastall

Details for installing Farm_blast are provided below. If you encounter an issue when installing Farm_blast please contact your local system administrator. If you encounter a bug please log it [here](https://github.com/sanger-pathogens/Farm_blast/issues) or email us at path-help@sanger.ac.uk.

### Using pip
`pip3 install farm_blast`

### Running the tests
The test can be run from the top level directory:   
`python3 setup.py test`

## Usage
Compare a query and a reference using blast+ blastn:

`farm_blast reference.fasta query.fasta`

Compare a query and a reference using blastall blastn:

`farm_blast --blastall reference.fasta query.fasta`

Run blast+ megablast:

`farm_blast --blast_type megablast reference.fasta query.fasta`

Run blastall tblastx:

`farm_blast --blast_type tblastx --blastall reference.fasta query.fasta`

Set the e-value and word length and do not filter the query sequence:

`farm_blast --no_filter -e 0.1 -W 30 reference.fasta query.fasta`

To get all the options, use `--help`:

`farm_blast --help`

## License
Farm_blast is free software, licensed under [GPLv3](https://github.com/sanger-pathogens/Farm_blast/blob/master/LICENSE).

## Feedback/Issues
Please report any issues to the [issues page](https://github.com/sanger-pathogens/Farm_blast/issues)
