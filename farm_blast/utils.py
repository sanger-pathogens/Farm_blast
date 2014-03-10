from fastaq import utils
import sys

class Error (Exception): pass


def offset_coords_file_to_dict(filename):
    f = utils.open_file_read(filename)
    offsets = {}

    for line in f:
        (seq, ref, offset) = line.rstrip().split('\t')
        assert seq not in offsets
        offsets[seq] = (ref, int(offset))

    utils.close(f)
    return offsets


def fix_blast_coords(blast_file, coords_file, outfile):
    coords_offset = offset_coords_file_to_dict(coords_file)
    fin = utils.open_file_read(blast_file)
    fout = utils.open_file_write(outfile)
    for line in fin:
        # blastn sticks a bunch of header lines in the tabulated
        # output file. Need to ignore them
        if '\t' not in line:
            continue

        # Lines are supposed to be tab delimited. Sometimes they
        # have a space character following a tab character, so
        # split on whitespace. This is OK because the pipeline has already
        # removed whitespace from sequence names
        data = line.rstrip().split()
        if data[0] in coords_offset:
            data[6] = str(int(data[6]) + coords_offset[data[0]][1])
            data[7] = str(int(data[7]) + coords_offset[data[0]][1])
            data[0] = coords_offset[data[0]][0]

        # always reconstruct the line, because of spaces bug mentioned above
        line = '\t'.join(data)

        print(line.rstrip(),file=fout)

    utils.close(fin)
    utils.close(fout)

