#!/bin/bash

train_cmd="utils/run.pl" 
decode_cmd="utils/run.pl"

kalFileDirectory=$1

#------------------------------------------------- Calculate jobs number -----------------------------------------------------------------------------------------------------------------------

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

NtestKal=$(ls $kalFileDirectory*.kal | wc -l)
# If ntest_kal is not greater or equal than number of processors, then nj is ntest_kal
if [ ! $NtestKal -ge $nj ]
then
	njTest=$NtestKal
else
	njTest=$nj
fi

# Ad-hoc solution for the apparently problema that kaldi has errors with nj>8. 
# This occurs in laptop with 8 cores (but for which sysctl -n hw.ncpu returns 16).
# So maybe the problem is that kaldi has problems with multithreading 
# A more general solution should be found
if [ $njTest -ge 8 ]
then
	njTest=8
fi

#-------------------------------------------------------GMM DECODING--------------------------------------------------------------------------------------------------------

dir=exp/tri1
steps/decode.sh --cmd "$decode_cmd" --nj $njTest exp/tri1/graph data/test $dir/decode


printf "\n#### BEGIN SCORING ####\n"
    
local/score.sh --cmd "$decode_cmd" data/test exp/tri1/graph $dir/decode || exit 1;

printf "\n#### END SCORING ####\n"


#-------------------------------------------------------NNET2 DECODING--------------------------------------------------------------------------------------------------------

# 2 decoding methods:
#Usage: $0 [options] <graph-dir> <data-dir> <am-model-file> <unknown_phone> <silence_phone> <decode-dir>
#steps/nnet2/decode_simple.sh --num-threads "$num_threads" --beam 8 --max-active 500 --lattice-beam 3 exp/tri1/graph data/test $dir/final.mdl $unknown_phone $silence_phone $experiment_dir/decode \
#|| exit 1;

#Usage: $0 [options] <graph-dir> <data-dir> <decode-dir>

dir=exp/nnet2/nnet2_simple
steps/nnet2/decode.sh --cmd "$decode_cmd" --nj $njTest exp/tri1/graph data/test $dir/decode


printf "\n#### BEGIN SCORING ####\n"
    
local/score.sh --cmd "$decode_cmd" data/test exp/tri1/graph $dir/decode || exit 1;

printf "\n#### END SCORING ####\n"

