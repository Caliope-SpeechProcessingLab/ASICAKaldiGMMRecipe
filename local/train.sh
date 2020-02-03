#!/bin/bash

# Training mono and tri GMM's plus a nnet.

#------------------------------------------------- Calculate number jobs -----------------------------------------------------------------------------------------------------------------------

kalFileDirectory=$1

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
NtrainKal=$(ls $kalFileDirectory*.kal | wc -l)
# If ntest_kal is not greater or equal than number of processors, then nj is ntest_kal
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
if [ $NtrainKal -ge 8 ]
then
  njTrain=8
fi

#------------------------------------------------- Configuration variables -----------------------------------------------------------------------------------------------------------------------

echo
echo

train_cmd="utils/run.pl"
decode_cmd="utils/run.pl"


#----------------------------------------------------------MONOPHONE STAGE--------------------------------------------------------------------------------------------------------------

steps/train_mono.sh --nj $njTrain --boost-silence 1.25 --cmd "$train_cmd" data/train data/lang exp/mono || exit 1;
#Mono-graph
utils/mkgraph.sh --mono data/lang exp/mono exp/mono/graph
#Mono-decoding
#steps/decode.sh --config conf/decode.config --nj $njTrain --cmd "$decode_cmd" exp/mono/graph data/test exp/mono/decode
#Mono-ali
steps/align_si.sh --nj $njTrain --cmd "$train_cmd" data/train data/lang exp/mono exp/mono_ali

#----------------------------------------------------------TRIPHONE STAGE---------------------------------------------------------------------------------------------------------------

steps/train_deltas.sh --cmd "$train_cmd" 2000 11000 data/train data/lang exp/mono_ali exp/tri1 || exit 1;
#Tri-graph
utils/mkgraph.sh data/lang exp/tri1 exp/tri1/graph || exit 1;
#tri-decoding
#steps/decode.sh --config conf/decode.config --nj $njTrain --cmd "$decode_cmd" exp/tri1/graph data/test exp/tri1/decode
#steps/align_si.sh --nj $njTrain --cmd "$train_cmd" data/train data/lang exp/tri1 exp/tri1_ali

#---------------------------------------------------------------NNET2 TRAINING---------------------------------------------------------------------------------------------------------

# COMENTAMOS EL NNET2 TRAINING PARA USAR ÚNICAMENTE EMPLEAR EL GMM
#dir=exp/nnet2/nnet2_simple
#Methods to try:
#steps/nnet2/nnet2_pnorm_simple.sh $dir
#bash steps/nnet2/nnet2_tanh_simple.sh $dir

# bash steps/nnet2/nnet2_tanh_simple.sh exp/nnet2/nnet2_simple