from fastaq import utils

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
        data = line.rstrip().split('\t')
        if data[0] in coords_offset:
            data[6] = str(int(data[6]) + coords_offset[data[0]][1])
            data[7] = str(int(data[7]) + coords_offset[data[0]][1])
            data[0] = coords_offset[data[0]][0]
            line = '\t'.join(data)

        print(line.rstrip(),file=fout)

    utils.close(fin)
    utils.close(fout)

