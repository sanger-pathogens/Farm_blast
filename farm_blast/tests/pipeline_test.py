#!/usr/bin/env python3

import sys
import os
import filecmp
import subprocess
import shutil
import unittest
from farm_blast import pipeline

modules_dir = os.path.dirname(os.path.abspath(pipeline.__file__))
data_dir = os.path.join(modules_dir, 'tests', 'data')

class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.ref = os.path.join(data_dir, 'pipeline_test.ref.fa')
        self.qry = os.path.join(data_dir, 'pipeline_test.qry.fa')
        options = pipeline.get_opts(args=[
            '--no_bsub',
            '--split_bases_tolerance', '1',
            '--split_bases', '100',
            '--outdir', 'tmp.Farm_blast_test',
            '--bsub_name_prefix', 'name',
            '--test',
            self.ref,
            self.qry])
        self.p = pipeline.Pipeline(options, os.path.abspath('scripts/farm_blast'))


    def test_make_setup_script_ref_already_indexed(self):
        expected_script = 'tmp.make_setup_script_expected'
        test_script = 'tmp.make_setup_script_test'
        ref = os.path.join(data_dir, 'pipeline_test.ref.indexed.fa')
        options = pipeline.get_opts(args=[
            '--no_bsub',
            '--split_bases_tolerance', '1',
            '--split_bases', '100',
            '--outdir', 'tmp.Farm_blast_test',
            '--bsub_name_prefix', 'name',
            ref,
            self.qry])
        self.p = pipeline.Pipeline(options, os.path.abspath('scripts/farm_blast'))
        self.p._make_setup_script(script_name=test_script)

        f = open(expected_script, 'w')
        print('set -e', file=f)
        print('fastaq to_fasta -s', os.path.abspath(self.qry), '- |',
              'fastaq chunker --skip_all_Ns - query.split 100 1', file=f)
        f.close()
        self.assertTrue(filecmp.cmp(expected_script, test_script))
        os.unlink(expected_script)
        os.unlink(test_script)


    def test_make_setup_script_convert_ref(self):
        expected_script = 'tmp.make_setup_script_expected'
        test_script = 'tmp.make_setup_script_test'
        self.p._make_setup_script(script_name=test_script)

        f = open(expected_script, 'w')
        print('set -e', file=f)
        print('fastaq to_fasta -s', os.path.abspath(self.ref), 'reference.fa', file=f)
        print('makeblastdb -dbtype nucl -in reference.fa', file=f)
        print('fastaq to_fasta -s', os.path.abspath(self.qry), '- |',
              'fastaq chunker --skip_all_Ns - query.split 100 1', file=f)
        f.close()
        self.assertTrue(filecmp.cmp(expected_script, test_script))
        os.unlink(expected_script)
        os.unlink(test_script)


    def test_make_setup_script_with_union_for_act(self):
        expected_script = 'tmp.make_setup_script_expected'
        test_script = 'tmp.make_setup_script_test'
        self.p.union_for_act = True
        self.p._make_setup_script(script_name=test_script)

        f = open(expected_script, 'w')
        print('set -e', file=f)
        print('fastaq merge', os.path.abspath(self.ref), '- |',
              'fastaq to_fasta -s - reference.fa', file=f)
        print('makeblastdb -dbtype nucl -in reference.fa', file=f)
        print('fastaq merge', os.path.abspath(self.qry), '- |',
              'fastaq to_fasta -s - - |',
              'fastaq chunker --skip_all_Ns - query.split 100 1', file=f)
        f.close()
        self.assertTrue(filecmp.cmp(expected_script, test_script))
        os.unlink(expected_script)
        os.unlink(test_script)


    def test_make_setup_job(self):
        self.p._make_setup_job()
        # the bsub call has a check for home directory, so check everthing after this is ok
        expected = r'''-R "select[mem>1000] rusage[mem=1000]" -M1000 -o 01.setup.sh.o -e 01.setup.sh.e -J name.setup bash 01.setup.sh'''
        self.assertTrue(str(self.p.setup_job).endswith(expected))


    def test_make_start_array_job(self):
        self.p._make_start_array_job()
        # the bsub call has a check for home directory, so check everthing after this is ok
        expected = r'''-o 02.run_array.sh.o -e 02.run_array.sh.e -J name.start_array bash 02.run_array.sh'''
        self.assertTrue(str(self.p.start_array_job).endswith(expected))


    def test_make_array_job(self):
        self.p._make_array_job()
        # the bsub call has a check for home directory, so check everthing after this is ok
        expected = r'''-R "select[mem>500] rusage[mem=500]" -M500 -o tmp.array.o.%I -e tmp.array.e.%I -J "name.array[1-$n]%100" blastn -task blastn -db ''' + self.ref + ''' -query query.split.\$LSB_JOBINDEX -out tmp.array.out.\$LSB_JOBINDEX -outfmt 6'''
        self.assertTrue(str(self.p.array_job).endswith(expected))


    def test_make_start_array_script(self):
        expected_script = os.path.join(data_dir, 'pipeline_test.02.array.sh')
        test_script = 'tmp.make_start_array_script_test'
        self.p.array_job = 'array_job'
        self.p._make_start_array_script(script_name=test_script)
        self.assertTrue(filecmp.cmp(expected_script, test_script))
        os.unlink(test_script)


    def test_make_combine_job(self):
        self.p._make_combine_job()
        # the bsub call has a check for home directory, so check everthing after this is ok
        expected = r'''-n 2 -R "span[hosts=1] select[mem>500] rusage[mem=500]" -M500 -o 03.combine.sh.o -e 03.combine.sh.e -J name.combine bash 03.combine.sh'''
        self.assertTrue(str(self.p.combine_job).endswith(expected))


    def test_make_combine_script(self):
        expected_script = os.path.join(data_dir, 'pipeline_test.03.combine.sh')
        test_script = 'tmp.make_combine_array_script_test'
        self.p._make_combine_script(script_name=test_script)
        expected = [
            'cat tmp.array.e.* > 02.array.e',
            'cat tmp.array.o.* > 02.array.o',
            'cat tmp.array.out.* | gzip -9 -c > blast.out.tmp.gz',
            'PYTHONPATH=',
            '--fix_coords_in_blast_output x x',
            'rm tmp.array.* query.split.* blast.out.tmp.gz 02.array.id 03.combine.sh.id',
            'touch FINISHED'
        ]

        try:
            f = open(test_script)
        except:
            sys.exit('Error opening file', test_script)

        got = [x.rstrip() for x in f.readlines()]
        f.close()

        # the script has the absolute path to farm_blast in it. We don't know
        # where that will be, so ignore that part
        self.assertEqual(len(got), len(expected))
        self.assertTrue(got[3].startswith('PYTHONPATH'))
        self.assertTrue('farm_blast' in got[4])
        got[4] = got[4].split(None,1)[1]
        self.assertListEqual(got[:2], expected[:2])
        self.assertListEqual(got[5:], expected[5:])
        os.unlink(test_script)

    def test_pipeline(self):
        self.p.run()
        expected = os.path.join(data_dir, 'pipeline_test.blast.out')
        subprocess.call('gunzip ' + os.path.join(self.p.outdir, 'blast.out.gz'), shell=True)
        expected_list = []
        with open(expected,'r') as f:
            for line in f:
                row = line.split()
                expected_list.append([row[0:2],row[3:9],row[11]])
        gotten = os.path.join(self.p.outdir, 'blast.out')
        gotten_list = []
        with open(gotten, 'r') as f:
            for line in f:
                row = line.split()
                gotten_list.append([row[0:2],row[3:9],row[11]])
        self.assertEqual(expected_list, gotten_list)

    def tearDown(self):
        if os.path.exists(self.p.outdir):
            shutil.rmtree(self.p.outdir)
