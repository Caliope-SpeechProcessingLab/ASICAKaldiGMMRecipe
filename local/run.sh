
#!/bin/bash

#--------------------------------------------------------------------USER VARIABLES---------------------------------------------------------------------------------------------


# ----------------------------------------------------------- FUNCTIONS -------------------------------------------------

stage=-7 #Only data preparation is done
# stage=-1 # Data preparation and Language preparation is done
# stage=-2 # Data preparation, Language preparation and Language model creation is done
# stage=-3 # Data preparation, Language preparation, Language model creation, and monophone training is done
# stage=-4 # Data preparation, Language preparation, Language model creation, monophone and triphone training is done
# stage=-5 # Data preparation, Language preparation, Language model creation, monophone, triphone and neet2 training is done
# stage=-6 # Data preparation, Language preparation, Language model creation, monophone, triphone, nnet2 training and nnet2 decoding is done


# Enable-section variable
resetDirectory=true
dataPreparation=true
langModelPreparation=true
langModelCreation=true
train_mono=true
train_tri=true
train_nnet2=true
decode_mono=true
decode_tri=true
decode_nnet=true
ali_mono=true
ali_tri=true



#--------------------------------------------------------------------SETTING DIRECTORY STRUCTURE---------------------------------------------------------------------------------------------


if $resetDirectory; then
    #Se borra la carpeta mfcc, data y exp
    rm -rf mfcc
    rm -rf exp
    rm -rf data

    #Se genera las carpetas vacias mfcc, data (y sus compartimentos), y exp
    cp -vr data_init data
    mkdir mfcc
    mkdir exp
fi



#--------------------------------------------------------------------SETTING PROCEDURE ENGINES---------------------------------------------------------------------------------------------

#. ./cmd.sh
. utils/parse_options.sh  # e.g. this parses the --stage option if supplied.
train_cmd="utils/run.pl"
decode_cmd="utils/run.pl"

#-------------------------------------------------------------------NUMBER OF JOBS CALCULATION---------------------------------------------------------------------------------------------

# Calculo el número de procesadores y lo guardo en nj
if [[ "$OSTYPE" == "linux-gnu" ]]; then
	nj=$(nproc) 
elif [[ "$OSTYPE" == "darwin"* ]]; then
	nj=$(sysctl -n hw.ncpu) 
else    # ...
	echo Lo siento, tu SO no lo he estudidado aún. 
	echo Asumo Número de procesos paralelos = 1
	nj=1
fi

NtestKal=$(ls info_user/test/*.kal | wc -l)
NtrainKal=$(ls info_user/train/*.kal | wc -l)
# If ntest_kal is not greater or equal than number of processors, then nj is ntest_kal
if [ ! $NtestKal -ge $nj ]
then
	njTest=$NtestKal
else
	njTest=$nj
fi

if [ ! $NtrainKal -ge $nj ]
then
	njTrain=$NtrainKal
else
	njTrain=$nj
fi

# Ad-hoc solution for the apparently problema that kaldi has errors with nj>8. 
# This occurs in laptop with 8 cores (but for which sysctl -n hw.ncpu returns 16).
# So maybe the problem is that kaldi has problems with multithreading 
# A more general solution should be found
if [ $njTest -ge 8 ]
then
	njTest=8
fi

if [ $NtrainKal -ge 8 ]
then
	njTrain=8
fi



# DATA PREPARATION.
mfccdir=mfcc
mkdir $mfccdir
for x in train test; do
	#CHECK and FIX the structure of data files PRIOR feature extraction
	utils/data/fix_data_dir.sh data/$x

	# MAKE MFCC PARAMETERS.
	steps/make_mfcc.sh --cmd "$train_cmd" --nj 3 data/$x exp/make_mfcc/$x $mfccdir || exit 1;
	steps/compute_cmvn_stats.sh data/$x exp/make_mfcc/$x $mfccdir || exit 1;

	# CHECK DATA DIR
	utils/validate_data_dir.sh data/$x
done


#-------------------------------------------------------------------PREPARING LANGUAGE------------------------------------------------------------------------------------------------------



if [ $stage -le -1 ]; then
	if $langModelPreparation; then
	    # LANGUAGE PREPARATION: Crea data/lang en función de data/local/dict
	    utils/prepare_lang.sh data/local/dict "<SIL>" data/local/lang data/lang
	fi
fi

#------------------------------------------------------------------CREATING LANGUAGE MODEL--------------------------------------------------------------------------------------------------


if [ $stage -le -2 ]; then

	if $langModelCreation; then
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

	fi
fi


#----------------------------------------------------------MONOPHONE STAGE--------------------------------------------------------------------------------------------------------------

if [ $stage -le -3 ]; then
  if $train_mono; then
    steps/train_mono.sh --nj $njTrain --boost-silence 1.25 --cmd "$train_cmd" data/train data/lang exp/mono || exit 1;
  fi
  if $decode_mono; then
    #Mono-graph
    utils/mkgraph.sh --mono data/lang exp/mono exp/mono/graph
    #Mono-decoding
    steps/decode.sh --config conf/decode.config --nj $njTest --cmd "$decode_cmd" exp/mono/graph data/test exp/mono/decode
  fi
  if $ali_mono; then
    #Mono-ali
    steps/align_si.sh --nj $njTrain --cmd "$train_cmd" data/train data/lang exp/mono exp/mono_ali
  fi
fi

#----------------------------------------------------------TRIPHONE STAGE---------------------------------------------------------------------------------------------------------------


if [ $stage -le -4 ]; then

  if $train_tri; then
    steps/train_deltas.sh --cmd "$train_cmd" 2000 11000 data/train data/lang exp/mono_ali exp/tri1 || exit 1;
  fi

  if $decode_tri; then
    #Tri-graph
    utils/mkgraph.sh data/lang exp/tri1 exp/tri1/graph || exit 1;
    #tri-decoding
    steps/decode.sh --config conf/decode.config --nj $njTest --cmd "$decode_cmd" exp/tri1/graph data/test exp/tri1/decode
  fi

  if $ali_tri; then
    steps/align_si.sh --nj $njTest --cmd "$train_cmd" data/train data/lang exp/tri1 exp/tri1_ali
  fi

fi

#---------------------------------------------------------------NNET2 TRAINING---------------------------------------------------------------------------------------------------------

dir=exp/nnet2/nnet2_simple

if [ $stage -le -5 ]; then

	if $train_nnet2; then
	    #Methods to try:
	    #steps/nnet2/nnet2_pnorm_simple.sh $dir
	    steps/nnet2/nnet2_tanh_simple.sh $dir
	fi

fi

#---------------------------------------------------------------NNET2 DECODING--------------------------------------------------------------------------------------------------------


if [ $stage -le -6 ]; then

    # 2 decoding methods:
    #Usage: $0 [options] <graph-dir> <data-dir> <am-model-file> <unknown_phone> <silence_phone> <decode-dir>
    #steps/nnet2/decode_simple.sh --num-threads "$num_threads" --beam 8 --max-active 500 --lattice-beam 3 exp/tri1/graph data/test $dir/final.mdl $unknown_phone $silence_phone $experiment_dir/decode \
            #|| exit 1;

    #Usage: $0 [options] <graph-dir> <data-dir> <decode-dir>
    steps/nnet2/decode.sh --cmd "$decode_cmd" --nj $njTest exp/tri1/graph data/test $dir/decode
fi


if [ $stage -le -7 ]; then

    printf "\n#### BEGIN SCORING ####\n"
    
    local/score.sh --cmd "$decode_cmd" data/test exp/tri1/graph $dir/decode || exit 1;

    printf "\n#### END SCORING ####\n"

fi

exit 0;
