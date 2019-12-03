import os
import sys
import argparse
import time
import glob
from farmpy import lsf
from farm_blast import blast, utils

class Error (Exception): pass

parser = argparse.ArgumentParser(
    description = 'Run BLAST in parallel on the farm',
    usage = '%(prog)s [options] <reference> <query>')

parser.add_argument('--no_bsub', action='store_true', help=argparse.SUPPRESS)
parser.add_argument('--fix_coords_in_blast_output', action='store_true', help=argparse.SUPPRESS)
parser.add_argument('--split_bases_tolerance', type=int, default=1000, help=argparse.SUPPRESS)
parser.add_argument('--test', action='store_true', help=argparse.SUPPRESS)

common_blast_group = parser.add_argument_group('Common BLAST options')
common_blast_group.add_argument('--blastall', action='store_true', help='Use blastall instead of the default blast+')
common_blast_group.add_argument('-p', '--blast_type', help='Type of blast to run [%(default)s]', choices=sorted(list(blast.ref_not_protein_types)) + sorted(list(blast.ref_protein_types)), default='blastn')
common_blast_group.add_argument('-e', '--evalue', help='Set the evalue cutoff')
common_blast_group.add_argument('-W', '--word_size', help='Set the word size')
common_blast_group.add_argument('--no_filter', action='store_true', help='Do not filter query sequence (equivalent to -F F in blastall, -dust no in blast+). By default, the query will be filtered')

bsub_group = parser.add_argument_group('Bsub options')
bsub_group.add_argument('-q', '--bsub_queue', help='Queue in which all jobs are run [%(default)s]', default = 'normal', metavar='Queue_name')
bsub_group.add_argument('--blast_mem', type=float, help='Memory limit in GB for the farm jobs that run BLAST. Default is 0.5, except set to 5 if blastall tblastx is used. Defaults doubled if --no_filter used', metavar='FLOAT', default=None)
bsub_group.add_argument('--bsub_name_prefix', help='Set the prefix of the names of the bsub jobs', default=None)


advanced_opts_group = parser.add_argument_group('Advanced options')
advanced_opts_group.add_argument('--act', action='store_true', help='Make ACT-friendly blast file, by concatenating all reference sequences together and all query sequences together before blasting.')
advanced_opts_group.add_argument('--blast_options', help='Put any extra options to the blast call (i.e. blastall, blastn, blastx ...etc) in quotes. e.g. --blast_options "-r 2". Whatever you put in here is NOT sanity checked.', default = '', metavar='"options in quotes"')
advanced_opts_group.add_argument('--debug', action='store_true', help='Just make scripts etc but do not run anything')
advanced_opts_group.add_argument('--outdir', help='Name of output directory (must not exist already)', metavar='output directory', default=None)
advanced_opts_group.add_argument('--split_bases', type=int, help='Number of bases in each split file of query. Default is 500000, except set to 200000 if blastall tblastx is used', metavar='INT', default=None)

parser.add_argument('reference', help='Name of reference file. Does not need to be indexed already. If not indexed, can be any format from FASTA, FASTQ, GFF3, EMBL, Phylip, GBK', metavar='reference')
parser.add_argument('query', help='Name of query file. Can be any format from FASTA, FASTQ, GFF3, EMBL, Phylip, GBK', metavar='query')

def get_opts(args=None):
    return parser.parse_args(args=args)


class Pipeline:
    def __init__(self, options, farm_blast_script):
        if options.outdir is None:
            if options.blastall:
                version = 'blastall'
            else:
                version = 'blast_plus'

            options.outdir = '.'.join(['Farm_blast', os.path.basename(options.reference), os.path.basename(options.query), version, options.blast_type, 'out'])

        self.outdir = os.path.abspath(options.outdir)
        self.reference = os.path.abspath(options.reference)
        self.query = os.path.abspath(options.query)
        self.bsub_queue = options.bsub_queue
        self.farm_blast_script = farm_blast_script
        self.test = options.test
        self.union_for_act = options.act

        self.blast = blast.Blast(
            self.reference,
            'query.split.INDEX',
            outfile='tmp.array.out.INDEX',
            blastall=options.blastall,
            blast_type=options.blast_type,
            evalue=options.evalue,
            word_size=options.word_size,
            no_filter=options.no_filter,
            extra_options=options.blast_options
        )

        self.setup_script = '01.setup.sh'
        self.start_array_script = '02.run_array.sh'
        self.combine_script = '03.combine.sh'
        if options.bsub_name_prefix is None:
            self.bsub_name_prefix = 'farm_blast:' + self.outdir
        else:
            self.bsub_name_prefix = options.bsub_name_prefix

        if options.no_bsub:
            self.no_bsub = True
            self.memory_units = 'MB'
        else:
            self.no_bsub = False
            self.memory_units = None

        self.debug = options.debug
        self.split_bases_tolerance = options.split_bases_tolerance

        self.files_to_delete = [
            'tmp.array.*',
            'query.split.*',
            'blast.out.tmp.gz',
            '02.array.id',
            '03.combine.sh.id',
        ]

        if not options.blast_mem:
            if self.blast.blastall and self.blast.blast_type == 'tblastx':
                self.array_mem = 5
            else:
                self.array_mem = 0.5

            if self.blast.no_filter:
                self.array_mem *= 2
        else:
            self.array_mem = options.blast_mem

        if not options.split_bases:
            if self.blast.blastall and self.blast.blast_type == 'tblastx':
                self.split_bases = 200000
            else:
                self.split_bases = 500000
        else:
            self.split_bases = options.split_bases


    def _make_setup_script(self, script_name=None):
        if script_name is None:
            script_name = self.setup_script
        try:
            f = open(script_name, 'w')
        except:
            raise Error('Error opening setup script "' + script_name + '" for writing')

        print('set -e', file=f)
        if not self.blast.blast_db_exists() or self.union_for_act:
            if self.union_for_act:
                print('fastaq merge', self.reference, '- |',
                      'fastaq to_fasta -s - reference.fa', file=f)
            else:
                print('fastaq to_fasta -s', self.reference, 'reference.fa', file=f)
            self.reference = 'reference.fa'
            self.blast.reference = self.reference
            print(self.blast.format_database_command(), file=f)
            self.files_to_delete.append('reference.*')

        # blast strips off everything after the first whitespace, so do this
        # before chunking so names stay consistent with query fasta and in blast output
        if self.union_for_act:
            print('fastaq merge', self.query, '- |',
                  'fastaq to_fasta -s - - |', end=' ', file=f)
        else:
            print('fastaq to_fasta -s', self.query, '- |', end=' ', file=f)

        print('fastaq chunker --skip_all_Ns', '-', 'query.split', self.split_bases, self.split_bases_tolerance, file=f)
        f.close()


    def _make_setup_job(self):
        self.setup_job = lsf.Job(
            self.setup_script + '.o',
            self.setup_script + '.e',
            self.bsub_name_prefix + '.setup',
            self.bsub_queue,
            1,
            'bash ' + self.setup_script,
            memory_units=self.memory_units,
        )


    def _make_array_job(self):
        self.array_job = lsf.Job(
            'tmp.array.o',
            'tmp.array.e',
            self.bsub_name_prefix + '.array',
            self.bsub_queue,
            self.array_mem,
            self.blast.get_run_command(),
            array_start=1,
            array_end=r'''$n''',
            memory_units=self.memory_units,
            max_array_size=100
        )


    def _make_start_array_job(self):
        self.start_array_job = lsf.Job(
            self.start_array_script + '.o',
            self.start_array_script + '.e',
            self.bsub_name_prefix + '.start_array',
            'small',
            0.1,
            'bash ' + self.start_array_script,
            no_resources=True  # we have to do this otherwise bmod fails! LSF bug?
        )


    def _make_start_array_script(self, script_name=None):
        if script_name is None:
            script_name = self.start_array_script
        try:
            f = open(script_name, 'w')
        except:
            raise Error('Error writing script "' + script_name + '"')
        print('set -e', file=f)
        print(r'''n=`ls query.split.* | grep -v coords | wc -l`''', file=f)
        print(str(self.array_job) + r''' |  awk '{print substr($2,2,length($2)-2)}' > 02.array.id''', file=f)
        print(r'''array_id=`cat 02.array.id`
combine_id=`cat ''' + self.combine_script + r'''.id`
bmod -w "done($array_id)" $combine_id''', file=f)
        f.close()


    def _make_combine_job(self):
        self.combine_job = lsf.Job(
            self.combine_script + '.o',
            self.combine_script + '.e',
            self.bsub_name_prefix + '.combine',
            self.bsub_queue,
            0.5,
            'bash ' + self.combine_script,
            memory_units=self.memory_units,
            threads=2
        )


    def _make_combine_script(self, script_name=None):
        if script_name is None:
            script_name = self.combine_script
        try:
            f = open(script_name, 'w')
        except:
            raise Error('Error writing script "' + script_name + '"')

        if not self.no_bsub:
            print('set -e', file=f)

        print(r'''cat tmp.array.e.* > 02.array.e
cat tmp.array.o.* > 02.array.o
cat tmp.array.out.* | gzip -9 -c > blast.out.tmp.gz''', file=f)
        if self.test:
            p = os.path.dirname(self.farm_blast_script)
            p = os.path.join(p, os.pardir)
            p = os.path.normpath(p)
            print('PYTHONPATH=' + p + ':$PYTHONPATH', file=f)
        if self.test:
            print(self.farm_blast_script, '--test --fix_coords_in_blast_output x x', file=f)
        else:
            print('farm_blast --fix_coords_in_blast_output x x', file=f)
        print('rm', ' '.join(self.files_to_delete), file=f)
        print('touch FINISHED', file=f)
        f.close()


    def run(self):
        '''Runs the whole blast pipeline'''
        # Here's the fun part: the first job splits the query file into
        # chunks. Don't know the number of chunks until that job has finished.
        # Therefore don't know the size of the job array until the chunking
        # job has finished.
        #
        # Here's what's going to happen:
        # 1. Submit chunking job.
        # 2. Submit job to submit an array, to run when Job1 finishes.
        #      - this is NOT the array itself!
        # 3. Submit job that combines the results of the job array and tidies
        # up files. It is initially set to run when the job that starts
        # the array finishes.
        # 4. When the job that starts the array actually runs, it does this:
        #       - figures out the size of the job array and submits it
        #       - changes the dependency of the last combine job, so that
        #         the combien job runs when the array has finished
        # 5. When the array finishes, Job3 will then run.

        try:
            os.mkdir(self.outdir)
        except:
            print('Error making output directory', self.outdir, file=sys.stderr)
            sys.exit(1)

        original_dir = os.getcwd()
        os.chdir(self.outdir)
        self._make_setup_script()
        self._make_setup_job()
        self._make_array_job()
        self._make_start_array_script()
        self._make_start_array_job()
        self._make_combine_script()
        self._make_combine_job()

        if self.debug:
            sys.exit()

        if self.no_bsub:
            self.setup_job.run_not_bsubbed()
            # get size of job array
            files_count = len(glob.glob('query.split.*')) - 1
            self.array_job.array_end = files_count
            print(self.array_job)
            print(self.array_job.array_start)
            print(self.array_job.array_end)
            print(self.array_job._make_command_string().replace('\$LSB_JOBINDEX', '$LSB_JOBINDEX'))
            self.array_job.run_not_bsubbed()

            # a little hack here to make the farm_blast script run
            this_script = os.path.realpath(__file__)
            this_script_dir = os.path.dirname(this_script)
            module_root_dir = os.path.join(this_script_dir, '..')
            module_root_dir = os.path.normpath(module_root_dir)
            os.environ["PATH"] = os.path.join(module_root_dir, 'scripts:') + os.environ["PATH"]
            os.environ["PYTHONPATH"] = module_root_dir + ':' + os.environ["PYTHONPATH"]
            self.combine_job.run_not_bsubbed()
        else:
            self.setup_job.run()
            time.sleep(1)
            self.start_array_job.add_dependency(self.setup_job.job_id)
            self.start_array_job.run()
            time.sleep(1)
            self.combine_job.add_dependency(self.start_array_job.job_id)
            self.combine_job.run()
            time.sleep(1)
            try:
                f = open(self.combine_script + '.id', 'w')
            except:
                raise Error('Error opening file "' + self.combine_script + '.id' + '" for writing')
            print(self.combine_job.job_id, file=f)
            f.close()
            print('Jobs submitted to the farm.')
            print('Final job id is', self.combine_job.job_id)
            print('\nPipeline finished OK when this file is written:\n   ', os.path.join(self.outdir, 'FINISHED'))
            print('\nFinal file will be called:\n   ', os.path.join(self.outdir, 'blast.out.gz'))

        os.chdir(original_dir)
