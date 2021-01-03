# This script is part of ASICAKaldiRecipe. It is used to test recognition of control files.
# That is the system is trained with a subset of the training files, and it is tested with 
# remaining training files. 
#
# You have three options:
#    crossval_spk all           (to test ALL spk IDs. That is, complete cross evaluation)
#    crossval_spk + 001 123 ... (to test specific spk IDs, 001 and 123 in this example)
#    crossval_spk - 041 034 ... (to test ALL spk IDs except specified)"

# Speaker's ID are recovered from the audio files as follows. 
# For files ----------------  the ID is ---
# 			CL001QL4_H45.wav 			001
# 			CL034QL4_H45.wav 			034
# etc.
# That is, it gets chars 3, 4 and 5
# If your speakers IDs are different from the above you will have to adapt the code.
# To facilitate this, you will find this comment where the code change is needed:

# ----	Check this if your IDs are different from above 

# The RESULTS will be found in results/crossval_spk_all.txt 
# You will also find temporal files such as: 
# crossval_spk_001.txt
# crossval_spk_034.txt
# But the latter are deleted at the very begining of this script 


# NOTE: This script is part fo ASICAKaldiRecipe, developed by:
# Salvador Florido (main programmaer), Ignacio Moreno-Torres and Enrique Nava
# We assume the folder structure in your compuer is that described in the Recipe
# and that this file is in the main folder (i.e. ASICAKaldiRecipe)

# Funtion to interrupt program with CTRL-C
trap message INT
 
function message() {
        echo "Ejecución interrumpida manualmente."
        echo "Se va a proceder a recuperar la estructura de archivos original"
        bash restore.sh
        exit;
        # command for clean up e.g. rm and so on goes below
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
    echo "crossval_spk all           (to test ALL spk IDs)"
    echo "crossval_spk + 001 123 ... (to test specific spk IDs, in the example 001 and 123)"
    echo "crossval_spk - 041 034 ... (to test ALL spk IDs except specified)"

	all_spk
    echo "List of IDs:"
	echo ${uniq[@]}
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
rm results/crossval_spk_???.txt # ----	Check this if your IDs are different from above  


# Folder preparation. The original train and testing folders  
# are stored as trainOriginal and testOriginal

# .kal files, all are placed in train, none in test. They will be moved in the main loop
mv info_user/test info_user/testOriginal
mv info_user/train info_user/trainOriginal
mkdir info_user/test
mkdir info_user/train
cp info_user/trainOriginal/*.kal info_user/train

# .wav files are copied both to train and test  
mv audio/Experiment1/test audio/Experiment1/testOriginal
mv audio/Experiment1/train audio/Experiment1/trainOriginal

mkdir audio/Experiment1/test
mkdir audio/Experiment1/train

cp audio/Experiment1/trainOriginal/*.wav audio/Experiment1/test
echo Audios trainOriginales copiados a test
cp audio/Experiment1/trainOriginal/*.wav audio/Experiment1/train
echo Audios trainOriginales copiados a train

# Borro los informes previos
rm -r results/final/*.csv

# Main loop calling to ASICA.PY 
for spk in ${uniq[@]}
do
	echo $spk
	reg_expr="info_user/train/??${spk}*.kal" # ----	Check this if your IDs are different from above 
	echo Speaker ID: $spk 
	echo File: $reg_expr
	echo Muevo los *.kal de $spk a test
	mv $reg_expr info_user/test
	echo Llamada a ASICA.py 
	python3 ASICA.py 
	echo Guardo los resultados de $spk 
	resultadosSpk="results/crossval_spk_${spk}.txt"
	mv results/global_spk.txt $resultadosSpk
	echo guardados en $resultadosSpk
	echo devuelvo los *.kal de $spk a su sitio
	mv info_user/test/*.kal info_user/train
	python3 result_format.py "global" $spk # zzz añadido
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
cat results/crossval_spk_???.txt > results/crossval_per_spk.txt # ----	Check this if your IDs are different from above 
