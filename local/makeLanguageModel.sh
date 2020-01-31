
#!/bin/bash

#------------------------------------------------------------------SETTING GLOBAL PATHS and VARIABLES---------------------------------------------------------------------------------------------------

./path.sh

#-------------------------------------------------------------------PREPARING LANGUAGE------------------------------------------------------------------------------------------------------



# LANGUAGE PREPARATION: Crea data/lang en función de data/local/dict
utils/prepare_lang.sh data/local/dict "<SIL>" data/local/lang data/lang

#------------------------------------------------------------------CREATING LANGUAGE MODEL--------------------------------------------------------------------------------------------------



# LAGUAGE MODEL CREATION
# Making lm.arpa
loc=`which ngram-count`;
if [ -z $loc ]; then
    # Locating srilm
    srilmBinFolders=$(ls -d ../../tools/srilm/bin/*/)
    numSrilmBinFolders=${#srilmBinFolders[@]}
    if [ $numSrilmBinFolders != 1 ]; then
            echo WARNING: SRILM folder cannot be computed automatically because 
            echo the number of folders in tools/srilm/bin/ is not exactly 1
            echo You should specify the sdir varriable manually in run.sh 
            echo For Mac, it should be:
            echo #sdir=`pwd`/../../tools/srilm/bin/macosx
            echo For Win64 it should be:
            echo #sdir=`pwd`/../../tools/srilm/bin/i686-m64
    fi
    temp=`pwd`/$srilmBinFolders
    sdir=${temp%?}

    if [ -f $sdir/ngram-count ]; then
    echo "Using SRILM language modelling tool from $sdir"
    export PATH=$PATH:$sdir
    else
    echo "SRILM toolkit is probably not installed.
    Instructions: tools/install_srilm.sh"
    exit 1
    fi
fi

#Crea la carpeta data/local/tmp con el archivo lm.arpa
local=data/local
ngram-count -order 2 -write-vocab $local/tmp/vocab-full.txt -wbdiscount -text $local/corpus.txt -lm $local/tmp/lm.arpa

#Making G.fst
# RECUERDA te dio error por las minusculas del corpus.txt
# Rellena carpeta data/lang
lang=data/lang
cat $local/tmp/lm.arpa | `pwd`/../../src/lmbin/arpa2fst -| `pwd`/../../tools/openfst-1.6.7/bin/fstprint | utils/eps2disambig.pl | utils/s2eps.pl | `pwd`/../../tools/openfst-1.6.7/bin/fstcompile --isymbols=$lang/words.txt --osymbols=$lang/words.txt --keep_isymbols=false --keep_osymbols=false | `pwd`/../../tools/openfst-1.6.7/bin/fstrmepsilon | `pwd`/../../tools/openfst-1.6.7/bin/fstarcsort --sort_type=ilabel > $lang/G.fst

