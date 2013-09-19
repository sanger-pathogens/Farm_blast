set -e
n=`ls query.split.* | grep -v coords | wc -l`
array_job |  awk '{print substr($2,2,length($2)-2)}' > 02.array.id
array_id=`cat 02.array.id`
combine_id=`cat 03.combine.sh.id`
bmod -w "done($array_id)" $combine_id
