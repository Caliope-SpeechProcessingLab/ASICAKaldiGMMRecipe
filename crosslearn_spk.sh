# This script is part of ASICAKaldiRecipe. It is used to measure how much kaldi learns when
# a new speaker is added to the training corpus. The script is identical to crosseval_spk
# except that in each iteration:
# In crossval:
#  - train: all speakers except one
#  - testing: one speaker
# In crosslearn:
#  - training: one speaker
#  - testing: all speakers 
# The RESULTS will be found in results/crossval_learn.txt 


# NOTE: This script is part fo ASICAKaldiRecipe, developed by:
# Salvador Florido (main programmer), Ignacio Moreno-Torres and Enrique Nava
# We assume the folder structure in your computer is that described in the Recipe
# and that this file is in the main folder (i.e. ASICAKaldiRecipe)

# Funtion to interrupt program with CTRL-C
trap message INT
 
function message() {
        echo "Ejecución interrumpida manualmente."
        echo "Se va a proceder a recuperar la estructura de archivos original"
        bash restore.sh
        exit;
}
 


# Aux function to obtain the full list of IDs. They are stored in the array: uniq
all_spk()
{
	declare -a spk_id=()
	i=0;
	for f in info_user/train/*.kal
	do
		((i++))
		spk_id[$i]=${f:18:3} # ----	Check this if your IDs are different from above 
	done;
	uniq=($(printf "%s\n" "${spk_id[@]}" | sort -u))
}


# Parameter processing

# Case 1. All files are processed
if [ "$1" = "all" ]; then
	all_spk
    echo "All files will be processed"

# Case 2. Only specified files are processed
elif [ "$1" = "+" ]; then
    i=0
	for arg in $*
	do
		((i++))
		if [ $i -gt 1 ]; then
			uniq[$i-1]=$arg
		fi
	done

# Case 3. All except specified are processed
elif [ "$1" = "-" ]; then
	all_spk
	i=0
	for arg in $*
	do
		((i++))
		if [ $i -gt 1 ]; then
			echo "Se excluye:" $arg
			uniq=("${uniq[@]/$arg}")
		fi
	done

else
    echo "Syntax should be one of these:"
    echo "crosslearn_spk all           (to test ALL spk IDs)"
    echo "crosslearn_spk + 001 123 ... (to test specific spk IDs, in the example 001 and 123)"
    echo "crosslearn_spk - 041 034 ... (to test ALL spk IDs except specified)"
    exit
fi

echo These speaker IDs will be processed
echo ${uniq[@]}


echo "Processgin in 5 seconds..." 
echo "Press CTRL-C to cancel NOW or just wait..."
for i in {1..5}; do
    # TODO: Insert work here #
    sleep 1
    echo -n "."
done

# select yn in "Yes" "No"; do
#    case $yn in
#        Yes ) echo "Great, here we go!"; break;;
#        No ) exit;;
#    esac
# done

# Old crossval_spk_IDs files deleted
rm results/crosslearn_spk_???.txt # ----	Check this if your IDs are different from above  


# Folder preparation. The original train and testing folders  
# are stored as trainOriginal and testOriginal

# .kal files, all are placed in TEST, none in TRAIN. They will be moved in the main loop
mv info_user/test info_user/testOriginal
mv info_user/train info_user/trainOriginal
mkdir info_user/test
mkdir info_user/train
cp info_user/trainOriginal/*.kal info_user/test

# .wav files are copied both to train and test  
mv audio/Experiment1/test audio/Experiment1/testOriginal
mv audio/Experiment1/train audio/Experiment1/trainOriginal

mkdir audio/Experiment1/test
mkdir audio/Experiment1/train

cp audio/Experiment1/trainOriginal/*.wav audio/Experiment1/test
echo Audios trainOriginales copiados a test
cp audio/Experiment1/trainOriginal/*.wav audio/Experiment1/train
echo Audios trainOriginales copiados a train


# Main loop calling to ASICA.PY 
for spk in ${uniq[@]}
do
	echo $spk
	reg_expr="info_user/test/??${spk}*.kal" # ----	Check this if your IDs are different from above 
	echo Speaker ID: $spk 
	echo File: $reg_expr
	echo Muevo los *.kal de $spk a train
	cp $reg_expr info_user/train
	echo Llamada a ASICA.py 
	python3 ASICA.py 
	echo Guardo los resultados de $spk 
	resultadosSpk="results/crosslearn_spk_${spk}_tmp.txt"
	mv results/global_spk.txt $resultadosSpk
	echo guardados en $resultadosSpk

	outputFilename="results/crosslearn_spk_${spk}_filename.txt"
	salida="Training file:	${spk}"
	echo -e $salida >> $outputFilename  

	echo elimino los *.kal de $spk de train
	rm -r info_user/train/*.kal
done

# Folders restored

rm -r info_user/test
rm -r info_user/train
mv info_user/testOriginal info_user/test 
mv info_user/trainOriginal info_user/train

rm -r audio/Experiment1/test
rm -r audio/Experiment1/train
mv audio/Experiment1/testOriginal audio/Experiment1/test
mv audio/Experiment1/trainOriginal audio/Experiment1/train

# Final output file obtained
cat results/crosslearn_spk_*.txt > results/crosslearn_per_spk.txt # ----	Check this if your IDs are different from above 
