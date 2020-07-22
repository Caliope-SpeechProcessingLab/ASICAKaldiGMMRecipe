#!/bin/bash

#------------------------------------------------------------------SETTING GLOBAL PATHS---------------------------------------------------------------------------------------------------

#./path.sh

bash path.sh

#------------------------------ EXTRACT FEATURES ---------------------------- #
train_cmd="utils/run.pl"
decode_cmd="utils/run.pl"





x=$1
nj=$2 # used to be nj=4 nº of split in scp

# x == train or test
utils/data/fix_data_dir.sh data/$x

# DATA PREPARATION.
#echo ${@:3}
for f in ${@:3}; do
    #echo $f
    featuredir=$f
    if [ ! -d $featuredir ]
    then
        mkdir $featuredir
    fi

    # Make parameters
    steps/make_$featuredir.sh --cmd "$train_cmd" --nj $nj data/$x exp/make_$featuredir/$x $featuredir || exit 1;
done

# merge features
python3 merge_kaldi_features.py ${@:3} combined_features
bash local/copy_scp_all.sh $x

# Compute cepstral mean and variance normalization statistics
steps/compute_cmvn_stats.sh data/$x exp/make_combined_features/$x combined_features || exit 1;

# CHECK DATA DIR
utils/validate_data_dir.sh data/$x

# Se borran los resultados parciales
for f in ${@:3}; do
    rm -rf $f
done
# ----------------------------------- Old script used only for mfcc calculation
# DATA PREPARATION.
#mfccdir=mfcc
#if [ ! -d $mfccdir ]
#then
#    mkdir $mfccdir
#fi

# MAKE MFCC PARAMETERS.
#steps/make_mfcc.sh --cmd "$train_cmd" --nj $nj data/$x exp/make_mfcc/$x $mfccdir || exit 1;
#steps/compute_cmvn_stats.sh data/$x exp/make_mfcc/$x $mfccdir || exit 1;

# CHECK DATA DIR
# utils/validate_data_dir.sh data/$x
# ----------------------------------- Old script used only for mfcc calculation

