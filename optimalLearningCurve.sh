# This script is part of ASICAKaldiRecipe. It is used to measure how WER changes as
# the size of the training corpus increases. 
#
# Syntax is:
#    learningCurve.sh spkID  
#    Example: learningCurve.sh 002  

# In the present version, the spkIDs for learning are obtained as follows
# 	1) crossLearning.sh is called for spkID
# 	2) bestTest2.sh produces a list of speaker IDs ordered inversely to WER
#	3) ASICA is run n-1 times, each time adding a new set of training files 

# As in other scripts, Speaker IDs are recovered from the audio files as follows. 
# For files ----------------  the ID is ---
# 			CL001QL4_H45.wav 			001
# 			CL034QL4_H45.wav 			034
# etc.
# That is, it gets chars 3, 4 and 5
# If your speakers IDs are different from the above you will have to adapt the code.
# To facilitate this, you will find this comment where the code change is needed:

# ----	Check this if your IDs are different from above 

# The RESULTS will be found in results/learningCurve_spkID.txt 


# NOTE: This script is part fo ASICAKaldiRecipe, developed by:
# Salvador Florido (main programmaer), Ignacio Moreno-Torres and Enrique Nava
# We assume the folder structure in your computer is that described in the Recipe
# and that this file is in the main folder (i.e. ASICAKaldiRecipe)

# Funtion to interrupt program with CTRL-C
trap message INT
 
function message() {
        echo "Ejecución interrumpida manualmente."
        echo "Revise las carpetas train y test de info_user y audios/Experiment1"
        echo "You may want to use restore.sh"
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

# Desordena el array uniq



# Parameter processing
if [ "$1" = "" ]; then
	echo "Wrong syntax. Please use:"
    echo "optimallearningCurve.sh spkID"  
    echo "Example: optimallearningCurve.sh 002"  
    exit
fi

targetID=$1

	all_spk


if [[ "${uniq[*]}" == *"$1"* ]]; then
    spkTarget=$1
    echo "Learning curve requested for speakerk ID: $spkTarget"
    echo "Sets will be add to the training dataset: more similar to target speaker first"
    echo "First, I will obtain a measure of how similar the other speakers are to target"
	bash crosslearn_spk.sh + $targetID
	uniq2=$(bash bestTest2.sh results/crosslearn_spk_${targetID}_tmp.txt ${targetID})


	echo "Order of introduction in train will be: "
    echo "${uniq2[*]}"	

else
    echo "Error: $1 is NOT a valid speaker ID." 
    echo "Valid IDs are:"
    echo "${uniq[@]}"
fi


# Old crossval_spk_IDs files deleted
# rm results/crossval_spk_???.txt # ----	Check this if your IDs are different from above  
removeOldResults="results/learningCurve_${spkTarget}_*.txt"
rm $removeOldResults

# Folder preparation. The original train and testing folders  
# are stored as trainOriginal and testOriginal
mv info_user/test info_user/testOriginal
mv info_user/train info_user/trainOriginal
mv audio/Experiment1/test audio/Experiment1/testOriginal
mv audio/Experiment1/train audio/Experiment1/trainOriginal

# New train and test folders are created
mkdir info_user/train
mkdir info_user/test
mkdir audio/Experiment1/train
mkdir audio/Experiment1/test

# .wav files from spk_ID are copied to test  
cp audio/Experiment1/trainOriginal/??${spkTarget}*.wav audio/Experiment1/test 

# All other are copied to train (Thouse from spk are not neeeded, but it's no problem to have them copied)
cp audio/Experiment1/trainOriginal/*.wav audio/Experiment1/train

# .kal files for target spk_ID are copied to test
cp info_user/trainOriginal/??${spkTarget}*.kal info_user/test


# Main loop calling to ASICA.
step=100 
for spkTrain in ${uniq2[@]}
do
	((step++))
	echo $spkTrain
	reg_expr="info_user/trainOriginal/??${spkTrain}*.kal" # ----	Check this if your IDs are different from above 
	echo Learning curve. New data added to training corpus
	echo Speaker ID: $spkTrain 
	echo Files: $reg_expr
	cp $reg_expr info_user/train
	echo Llamada a ASICA.py 
	python3 ASICA.py 
	echo Guardo los resultados tras incluir $spkTrain 
	resultadosSpk="results/learningCurve_${spkTarget}_${step}_${spkTrain}.txt"
	mv results/global_spk.txt $resultadosSpk
	echo guardados en $resultadosSpk
	outputFilename="results/learningCurve_${spkTarget}_${step}_${spkTrain}_filename.txt"
	salida="Step: ${step}\nLast speaker ID added: ${spkTrain}"
	echo -e $salida >> $outputFilename  
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
allResultsLC="results/learningCurve_${spkTarget}_*.txt"
output=results/optimalLlearningCurve/optimalLearningCurve_${spkTarget}.txt 
cat $allResultsLC > $output # 
rm $allResultsLC


