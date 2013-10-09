cat tmp.array.e.* > 02.array.e
cat tmp.array.o.* > 02.array.o
cat tmp.array.out.* | gzip -9 -c > blast.out.tmp.gz
farm_blast --fix_coords_in_blast_output x x
rm tmp.array.* query.split.* blast.out.tmp.gz 02.array.id 03.combine.sh.id
touch FINISHED
