import os

class Error (Exception): pass

ref_not_protein_types = set([
    'blastn',
    'blastn-short',
    'dc-megablast',
    'megablast',
    'rmblastn',
    'tblastn',
    'tblastx',
])

ref_protein_types = set([
    'blastp',
    'blastp-short',
    'deltablast',
    'blastx'
])

class Blast:
    def __init__(
         self,
         reference,
         query,
         outfile='blast.out',
         blastall=False,
         blast_type='blastn',
         evalue=None,
         word_size=None,
         no_filter=False,
         extra_options=''):

        self.reference = reference
        self.query = query
        self.outfile = outfile
        self.blastall = blastall
        self.blast_type = blast_type
        self.evalue = evalue
        self.word_size = word_size
        self.no_filter = no_filter
        self.extra_options = extra_options

        if self.blast_type in ref_not_protein_types:
            self.protein_reference = False
        elif self.blast_type in ref_protein_types:
            self.protein_reference = True
        else:
            raise Error('blast_type must be one of ' + ' '.join(list(ref_not_protein_types) + list(ref_protein_types)))

    def blast_db_exists(self):
        if self.protein_reference:
            test_files1 = [self.reference + '.' + e for e in ['phr', 'pin', 'psq']]
            test_files2 = [self.reference + '.00.' + e for e in ['phr', 'pin', 'psq']]
        else:
            test_files1 = [self.reference + '.' + e for e in ['nhr', 'nin', 'nsq']]
            test_files2 = [self.reference + '.00.' + e for e in ['nhr', 'nin', 'nsq']]

        if False not in [os.path.isfile(fname) for fname in test_files1] \
             or False not in [os.path.isfile(fname) for fname in test_files2]:
            return True

        return False
         

    def format_database_command(self):
        if self.blast_db_exists():
            return None

        if self.protein_reference:
            dbtype = 'prot'
            popt = 'T'
        else:
            dbtype = 'nucl'
            popt = 'F'

        if self.blastall:
            return ' '.join(['formatdb -p', popt, '-i', self.reference])
        else:
            return ' '.join(['makeblastdb -dbtype', dbtype, '-in', self.reference])


    def _make_options_string(self):
        opts = []

        if self.blastall:
            opts.extend(['-m', '8'])

            if self.evalue:
                opts.extend(['-e', str(self.evalue)])
            if self.word_size:
                opts.extend(['-W', str(self.word_size)])
            if self.no_filter:
                opts.extend(['-F', 'F'])
        else:
            opts.extend(['-outfmt', '6'])

            if self.evalue:
                opts.extend(['-evalue', str(self.evalue)])
            if self.word_size:
                opts.extend(['-word_size', str(self.word_size)])
            if self.no_filter and not self.protein_reference:
                opts.extend(['-dust', 'no'])
            if self.protein_reference and not self.no_filter:
                opts.extend(['-seg', 'yes'])

        if self.extra_options:
            opts.append(self.extra_options)

        return ' '.join(opts)


    def _make_io_string(self):
        if self.blastall:
            opts = [
                '-d', self.reference,
                '-i', self.query,
                '-o', self.outfile
            ]
        else:
            opts = [
                '-db', self.reference,
                '-query', self.query,
                '-out', self.outfile
            ]

        return ' '.join(opts)
        

    def _make_blast_type_string(self):
        if self.blastall:
            if self.blast_type == 'megablast':
                return 'blastall -p blastn -n T'
            else:
                return 'blastall -p ' + self.blast_type
        else:
            type_to_string = {
                'blastn': 'blastn -task blastn',
                'blastn-short': 'blastn -task blastn-short',
                'dc-megablast': 'blastn -task dc-megablast',
                'megablast': 'blastn -task megablast',
                'rmblastn': 'blastn -task rmblastn',
                'tblastn': 'tblastn',
                'tblastx': 'tblastx',
                'blastp': 'blastp -task blastp',
                'blastp-short': 'blastp -task blastp-short',
                'deltablast': 'blastp -task deltablast',
                'blastx': 'blastx'
            }

            try:
                return type_to_string[self.blast_type]
            except:
                raise Error('Problem with blast type: ' + self.blast_type)


    def get_run_command(self):
        return ' '.join([
            self._make_blast_type_string(),
            self._make_io_string(),
            self._make_options_string()
        ])
