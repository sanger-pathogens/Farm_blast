#!/usr/bin/env python3

import sys
import os
import filecmp
import unittest
from farm_blast import utils


modules_dir = os.path.dirname(os.path.abspath(utils.__file__))
data_dir = os.path.join(modules_dir, 'tests', 'data')

class TestUtils(unittest.TestCase):
    def test_offset_coords_file_to_dict(self):
        '''Test coords offsets load into dict from file'''
        correct_coords = {
            'seq1': ('ref1', 0),
            'seq2': ('ref1', 10),
            'seq3': ('ref2', 0),
            'seq4': ('ref2', 42)
        }

        d = utils.offset_coords_file_to_dict(os.path.join(data_dir, 'utils_test_coords_offset.tsv'))
        self.assertDictEqual(d, correct_coords)


    def test_fix_blast_coords(self):
        '''Test blast coords fixed correctly'''
        blast_file = os.path.join(data_dir, 'utils_test_fix_blast_coords.blast')
        coords_file = os.path.join(data_dir, 'utils_test_coords_offset.tsv')
        outfile = 'tmp.fix_blast_coords.out'
        utils.fix_blast_coords(blast_file, coords_file, outfile)
        self.assertTrue(filecmp.cmp(os.path.join(data_dir, 'utils_test_fix_blast_coords.blast.fixed'), outfile))
        os.unlink(outfile)

if __name__ == '__main__':
    unittest.main()
