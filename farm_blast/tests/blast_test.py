#!/usr/bin/env python3

import sys
import os
import filecmp
import unittest
from farm_blast import blast

modules_dir = os.path.dirname(os.path.abspath(blast.__file__))
data_dir = os.path.join(modules_dir, 'tests', 'data')

class TestBlast(unittest.TestCase):
    def test_check_blast_type(self):
        '''Check dies if blast_type not recognised'''
        with self.assertRaises(blast.Error):
            b = blast.Blast('query.fasta', 'ref.fasta', blast_type='oops')
        

    def test_blast_db_exists(self):
        '''Test detection or not of blast database'''
        query_file = 'tmp.test_blast_db_exists.fa'
        b_blastn = blast.Blast(query_file, 'ref.fasta')
        b_blastp = blast.Blast(query_file, 'ref.fasta', blast_type='blastp')

        nuc_suffixes = ['nin', 'nhr', 'nsq']
        nuc_suffixes2 = ['00.' + x for x in nuc_suffixes]
        pro_suffixes = ['pin', 'phr', 'psq']
        pro_suffixes2 = ['00.' + x for x in pro_suffixes]

        open(query_file, 'w').close()
        self.assertFalse(b_blastn.blast_db_exists())
        self.assertFalse(b_blastp.blast_db_exists())

        tuples = [
            (nuc_suffixes, b_blastn, b_blastp),
            (nuc_suffixes2, b_blastn, b_blastp),
            (pro_suffixes, b_blastp, b_blastn),
            (pro_suffixes2, b_blastp, b_blastn)
        ]
                  
        for suffixes, blast1, blast2 in tuples:
            print(suffixes, blast1.blast_type, blast2.blast_type)
            for suff in suffixes:
                open(query_file + '.' + suff, 'w').close()

            self.assertTrue(blast1.blast_db_exists())
            self.assertFalse(blast2.blast_db_exists())
     
            for suff in suffixes:
                missing_file = query_file + '.' + suff
                os.unlink(missing_file)
                self.assertFalse(blast1.blast_db_exists())
                open(missing_file, 'w').close()
                
            for suff in suffixes:
                os.unlink(query_file + '.' + suff)
            
        os.unlink(query_file)


    def test_format_database_command(self):
        '''Test command to format database made correctly for blast+ and blastall'''
        b_all_nuc = blast.Blast('ref.fasta', 'qry.fasta', blastall=True)
        b_all_pro = blast.Blast('ref.fasta', 'qry.fasta', blast_type='blastp', blastall=True)
        b_plus_nuc = blast.Blast('ref.fasta', 'qry.fasta')
        b_plus_pro = blast.Blast('ref.fasta', 'qry.fasta', blast_type='blastp')

        blastall_nuc = 'formatdb -p F -i ref.fasta'
        blastall_pro = 'formatdb -p T -i ref.fasta'
        blastplus_nuc = 'makeblastdb -dbtype nucl -in ref.fasta'
        blastplus_pro = 'makeblastdb -dbtype prot -in ref.fasta'
        
        self.assertEqual(b_all_nuc.format_database_command(), blastall_nuc)
        self.assertEqual(b_all_pro.format_database_command(), blastall_pro)
        self.assertEqual(b_plus_nuc.format_database_command(), blastplus_nuc)
        self.assertEqual(b_plus_pro.format_database_command(), blastplus_pro)

        query_file = 'tmp.test_blast_db_exists.fa'
        b_blastn = blast.Blast(query_file, 'ref.fasta')
        files = [query_file + '.' + x for x in ['nin', 'nhr', 'nsq']]
        for f in files:
            open(f, 'w').close()
        self.assertEqual(b_blastn.format_database_command(), None)
        for f in files:
            os.unlink(f)


    def test_make_options_string(self):
        '''Test options set correctly'''
        test_objs = [
            blast.Blast('ref', 'qry'),
            blast.Blast('ref', 'qry', evalue=0.1),
            blast.Blast('ref', 'qry', word_size=42),
            blast.Blast('ref', 'qry', no_filter=True),
            blast.Blast('ref', 'qry', extra_options='-x 1'),
            blast.Blast('ref', 'qry', blast_type='blastp'),
            blast.Blast('ref', 'qry', blastall=True),
            blast.Blast('ref', 'qry', blastall=True, evalue=0.1),
            blast.Blast('ref', 'qry', blastall=True, word_size=42),
            blast.Blast('ref', 'qry', blastall=True, no_filter=True),
        ]

        correct = [
            '-outfmt 6',
            '-outfmt 6 -evalue 0.1',
            '-outfmt 6 -word_size 42',
            '-outfmt 6 -dust no',
            '-outfmt 6 -x 1',
            '-outfmt 6 -seg yes',
            '-m 8',
            '-m 8 -e 0.1',
            '-m 8 -W 42',
            '-m 8 -F F'
        ]

        for i in range(len(correct)):
            self.assertEqual(correct[i], test_objs[i]._make_options_string())


    def test_make_io_string(self):
        '''Test input/output files string'''
        test_objs = [
            blast.Blast('ref', 'qry'),
            blast.Blast('ref', 'qry', blastall=True),
        ]

        correct = [
            '-db ref -query qry -out blast.out',
            '-d ref -i qry -o blast.out',
        ]
 
        for i in range(len(correct)):
            self.assertEqual(correct[i], test_objs[i]._make_io_string())


    def test_make_blast_type_string(self):
        '''Test blast type string'''
        test_objs = [
            (blast.Blast('ref', 'qry'), 'blastn -task blastn'),
            (blast.Blast('ref', 'qry', blast_type='blastn'), 'blastn -task blastn'),
            (blast.Blast('ref', 'qry', blast_type='blastn-short'), 'blastn -task blastn-short'),
            (blast.Blast('ref', 'qry', blast_type='dc-megablast'), 'blastn -task dc-megablast'),
            (blast.Blast('ref', 'qry', blast_type='megablast'), 'blastn -task megablast'),
            (blast.Blast('ref', 'qry', blast_type='rmblastn'), 'blastn -task rmblastn'),
            (blast.Blast('ref', 'qry', blast_type='blastx'), 'blastx'),
            (blast.Blast('ref', 'qry', blast_type='blastp'), 'blastp -task blastp'),
            (blast.Blast('ref', 'qry', blast_type='blastp-short'), 'blastp -task blastp-short'),
            (blast.Blast('ref', 'qry', blast_type='deltablast'), 'blastp -task deltablast'),
            (blast.Blast('ref', 'qry', blast_type='tblastn'), 'tblastn'),
            (blast.Blast('ref', 'qry', blast_type='tblastx'), 'tblastx'),
            (blast.Blast('ref', 'qry', blastall=True), 'blastall -p blastn'),
            (blast.Blast('ref', 'qry', blastall=True, blast_type='blastn'), 'blastall -p blastn'),
            (blast.Blast('ref', 'qry', blastall=True, blast_type='blastx'), 'blastall -p blastx'),
            (blast.Blast('ref', 'qry', blastall=True, blast_type='blastp'), 'blastall -p blastp'),
            (blast.Blast('ref', 'qry', blastall=True, blast_type='tblastn'), 'blastall -p tblastn'),
            (blast.Blast('ref', 'qry', blastall=True, blast_type='tblastx'), 'blastall -p tblastx'),
            (blast.Blast('ref', 'qry', blastall=True, blast_type='megablast'), 'blastall -p blastn -n T')
        ]
        
        for t in test_objs:
            self.assertEqual(t[1], t[0]._make_blast_type_string())

        with self.assertRaises(blast.Error):
            b = blast.Blast('ref', 'qry', blast_type='oops')

    def test_get_run_command(self):
        '''Test command to run blast made OK'''
        b = blast.Blast('qry.fasta', 'ref.fasta', evalue=0.1)
        expected = ' '.join([
            b._make_blast_type_string(),
            b._make_io_string(),
            b._make_options_string()
        ])

        self.assertEqual(expected, b.get_run_command())

if __name__ == '__main__':
    unittest.main()
