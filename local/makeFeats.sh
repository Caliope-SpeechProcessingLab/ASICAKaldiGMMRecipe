#!/bin/bash

#------------------------------------------------------------------SETTING GLOBAL PATHS---------------------------------------------------------------------------------------------------

#./path.sh

bash path.sh

#------------------------------------------------------------------- EXTRACT FEATURES ---------------------------------------------------------------------------------------------
train_cmd="utils/run.pl"
decode_cmd="utils/run.pl"

nj=4
# DATA PREPARATION.
mfccdir=mfcc
if [ ! -d $mfccdir ]
then
    mkdir $mfccdir
fi

x=$1
utils/data/fix_data_dir.sh data/$x


# MAKE MFCC PARAMETERS.
steps/make_mfcc.sh --cmd "$train_cmd" --nj $nj data/$x exp/make_mfcc/$x $mfccdir || exit 1;
steps/compute_cmvn_stats.sh data/$x exp/make_mfcc/$x $mfccdir || exit 1;

# CHECK DATA DIR
utils/validate_data_dir.sh data/$x
