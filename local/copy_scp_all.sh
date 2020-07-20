#!/bin/bash
# This script is always called by python files: "bash copy_scp_all.sh train" ( o test)

# Copia de combined_features los archivos .scp y los combina para guardarlos en data/train/feats.scp

x=$1

rm -f data/$x/feats.scp
for n in $(seq 8); do
    [ -r combined_features/raw_data_${x}.$n.scp ] && cat combined_features/raw_data_${x}.$n.scp || exit 1;
done > data/$x/feats.scp


# nj=1
#nj=$1
# echo $2
#for x in test; do
#    rm -f data/$x/feats.scp
#    for n in $(seq $nj); do
#        cat combined_features/raw_data_${x}.$n.scp || exit 1;
#    done > data/$x/feats.scp
#done

# nj=8
#nj=$2
#for x in train; do
#    rm -f data/$x/feats.scp
#    for n in $(seq $nj); do
#        cat combined_features/raw_data_${x}.$n.scp || exit 1;
#    done > data/$x/feats.scp
#done
