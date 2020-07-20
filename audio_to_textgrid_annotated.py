#!/usr/bin/env python3
#
# This script takes an audio file and annotates it automatically in kaldi .kal
# format and .TextGrid praat format.
#
# Folder prerequisistes:
#   audio/experiment_lm/    contains audio data for training Kaldi
#   info_user/test/         must be empty
#   info_user/train/        contains .kal files for training Kaldi
#   audio_no_annotated/     audio files with no .kal associated to be automatically annotated
#
# Speaker's ID are recovered from the audio files as follows.
# For files ----------------  the ID is ---
#               CL001QL4_H45.wav                 001
#               CL034QL4_H45.wav                 034
# etc.
# That is, it gets chars 3, 4 and 5
# If your speakers IDs are different from the above you will have to adapt the code.
# To facilitate this, you will find this comment where the code change is needed:
#
# ----    Check this if your IDs are different from above
#
#
# Use:
#   python3 audio_to_textgrid_annotated.py train    trains the model and performs annotation
#   python3 audio_to_textgrid_annotated.py test     only performs annotation
#
#
# Outputs:
#   audio/experiment_lm/no_kal_audio/       folder with all audio files in audio/experiment_lm with no .kal in info_user/train
#   audio_annotated/kaldi_annotated         .kal files annotated
#   audio_annotated/textgrid_annotated      .TextGrid files annotated
#
# IMPORTANT: After annotation, .TextGrid files must be reviwed manually and reconvert to .kal files for ensuring accuracy.
#
# Packages:
#   pandas:         pip3 install pandas
#   parselmouth:    pip3 install praat-parselmouth
#       https://github.com/YannickJadoul/Parselmouth
#       https://billdthompson.github.io/assets/output/Jadoul2018.pdf
#
# Funtion to interrupt program with CTRL-C
#

import os
import re
import sys
import shutil
import subprocess
import parselmouth
from parselmouth.praat import call
#import pandas as pd
#import result_format
import crossval_spk_functions

# ----------------------------- FUNCTIONS  ---------------------------------- #
def create_data_path(path_name):
    """Takes path_name and create a folder with that path. If exits, removes it before creation.

    :param path_name: name of the path to create.
    :returns: None.
    """
    if os.path.exists(path_name):
        shutil.rmtree(path_name)
    # end if
    os.makedirs(path_name)
#end create_data_path


def audio_to_textgrid(audio_no_annot_path, textgrid_path):
    """Generates .TextGrid files from audio using Praat.

    :param audio_no_annot_path: path with audio not annotated.
    :param textgrid_path: path with textgrid generated.
    :returns: None.
    """
    create_data_path(textgrid_path)

    audio_files = os.listdir(audio_no_annot_path)
    print("Procesing " + str(len(audio_files)) + " audio files with Praat, can take a while...")

    data_mod = round(len(audio_files)/10)
    index_mod = 1

    for audio in audio_files:

        sound = parselmouth.Sound(os.path.join(audio_no_annot_path, audio))

        # Take each audio file and convert to textGrid with praat
        noise_reduction = call(sound, "Remove noise", 0.0, 1.0, 0.025, 80, 10000, 40, 'Spectral subtraction') # 'silent', 'sounding'
        manipulation = call(noise_reduction, "To TextGrid (silences)", 100, 0.0, -65.0, 0.8, 0.2, '', 'sounding') # 'silent', 'sounding'   # 0.8, 0.2
                                                                                       # minimun silent and sound intervals
        text_audio = audio[:-4] + '.TextGrid'
        call(manipulation, "Save as text file", os.path.join(textgrid_path, text_audio))

        # Show progresion
        try:
            if index_mod % data_mod == 0:  # it means 10%, 20%, ...
                print(str(int(index_mod/data_mod * 10))+"% ",end="\r")
        except:
            print('',end="\r")
        #end try
        index_mod += 1
    # end for

    # Modelate audio and make corrections to TextGrid created
    # !!: separation_between_words gives the times between word, i.e. duration of the silences
    #    separation_between_words = modelate_audio(info_user_train_path)
    #
    #    mean_sepa = np.mean(separation_between_words)
    #    std_sepa = np.std(separation_between_words)
    #    min_separation_silences = mean_sepa - 3*std_sepa
# end audio_to_textgrid


def modelate_audio(path_name):
    """Takes a path with manually generated kaldi files and calculates diferent metric.

    :param path_name: path with audio not annotated.
    :param textgrid_path: path with annotations.
    :returns separation_between_words: Separations between words in order to identify wrong silents.
    """
    # path_name = info_user_train_path

    # Calculate separation between words in order to identify wrong silents
    separation_between_words = []    # save length of 'sounding' period separation
    # kal_file ='CA562QL1_H50.kal'
    for kal_file in os.listdir(path_name):
        if kal_file.endswith('.kal') and not kal_file.endswith("00.kal"):
            kaldi_text = open(os.path.join(path_name, kal_file))
            kaldi_text = kaldi_text.read()
            kaldi_text = re.split(r'[\n\t]+', kaldi_text)

            if kaldi_text[-1] == '':    # check if last field is empty
                kaldi_text = kaldi_text[:-1]

            num_words = len(kaldi_text)/4

            for i in range(int(num_words)-1):
                separation_between_words.append(float(kaldi_text[(i+1)*4]) - float(kaldi_text[i*4]))
         # end if
    # end for

    return separation_between_words
# end modelate_audio


def textgrid_to_kal(textgrid_path, kaldi_path):
    """Takes textgrid and convert to kal.

    :param textgrid_path: path with textgrid annotations.
    :param kaldi_path: folder when saving kaldi files.
    :returns: None.
    """
    create_data_path(kaldi_path)

    for file in os.listdir(textgrid_path):

        textgrid_file = open(os.path.join(textgrid_path, file))
        kaldi_file = open(os.path.join(kaldi_path, file[:-9]+".kal"),'a')

        # Variables for textgrid structure
        line_kaldi = list()
        actual = []
        prev = []
        prev_prev = []

        for i, line in enumerate(textgrid_file):
            # refresh variable values
            prev_prev = prev
            prev = actual
            actual = line

            if "sounding" in actual:
                # Found "sounding" text
                time_start = prev_prev.split()
                line_kaldi.append(time_start[-1] + '\t')

                time_end = prev.split()
                line_kaldi.append(time_end[-1] + '\t')

                line_kaldi.append("so so so\t")
                line_kaldi.append("s_o s_o s_o\n")

                # Write in text and delete list
                kaldi_file.writelines(line_kaldi)
                line_kaldi = list()
            # end if
        # end for
        textgrid_file.close()
        kaldi_file.close()
    # end for
# end textgrid_to_kal


def results_to_kal_annot(results_raw_path,kaldi_path,kaldi_annotated_path):
    """Save results to kaldi format file annotations.

    :param results_raw_path: folder with results/raw after testing.
    :param kaldi_path: folder with kaldi files.
    :param kaldi_annotated_path: folder when saving kaldi files.
    :returns: None.
    """
    create_data_path(kaldi_annotated_path)

    for file in os.listdir(results_raw_path):

        raw_file = open(os.path.join(results_raw_path, file))
        kal_file = open(os.path.join(kaldi_path, file[:-8]+".kal"),'r')
        kal_annotated_file = open(os.path.join(kaldi_annotated_path, file[:-8]+".kal"),'a')

        list_kal_annotated = [None] * sum(1 for line in open(os.path.join(kaldi_path, file[:-8]+".kal"),'r'))

        kal_lines = kal_file.readlines()
        for i, line in enumerate(raw_file):
            if "hyp" in line :

                word_kaldi = line.split()
                word_kaldi = word_kaldi[2:]

                line_index = line.replace('hyp', '   ')
                line_index = line_index.replace(file[:-8]+'-utt', '')
                line_index = int(line_index[:4])
                # print(line_index)

                line_kal_file = kal_lines[line_index]

                # Fix manuaaly the letters to avoid symbols like ' " [ ] ...
                line_to_file = ''
                for words in word_kaldi:
                    if words != "***":    # ***
                        line_to_file = line_to_file + words + ' '
                line_to_file = line_to_file[:-1]
                line_kal_file = line_kal_file.replace('so so so', line_to_file)

                vowels = ['a','e','i','o','u']
                vowels_mod = ['_a','_e','_i','_o','_u']
                for i in range(0,len(vowels)):
                    line_to_file = line_to_file.replace(vowels[i],vowels_mod[i])

                line_kal_file = line_kal_file.replace('s_o s_o s_o', line_to_file)

                list_kal_annotated[line_index] = line_kal_file
            # end if
        # end for
        list_kal_annotated = list(filter(None, list_kal_annotated))

        for line in list_kal_annotated:
            kal_annotated_file.write(line)

    raw_file.close()
    kal_file.close()
    kal_annotated_file.close()
    # end for
# end results_to_kal_annot


def kal_annot_to_textgrid_annot(kaldi_annotated_path, textgrid_path, textgrid_annotated_path):
    """Save annotations in kaldi format to textgrid format.

    :param kaldi_annotated_path: path to kaldi annotations folder.
    :param textgrid_path: textgrid orginal path.
    :param textgrid_annotated_path: textgrid with annotated path.
    :returns: None.
    """
    create_data_path(textgrid_annotated_path)

    for file in os.listdir(kaldi_annotated_path):

        kaldi_annotated_file = open(os.path.join(kaldi_annotated_path, file))
        kaldi_annotated_file_tier2 = open(os.path.join(kaldi_annotated_path, file))
        textgrid_file = open(os.path.join(textgrid_path, file[:-4]+".TextGrid"),'r')
        textgrid_annotated_file = open(os.path.join(textgrid_annotated_path, file[:-4]+".TextGrid"),'w')

        tier2 = list()
        for i, line in enumerate(textgrid_file):
            line_aux = line
            line_aux_tier2 = line

            # Need to create another file with tier2
            if i > 7:
                if "sounding" in line:
                    fonol_kaldi = kaldi_annotated_file_tier2.readline()
                    fonol_kaldi = fonol_kaldi.split()
                    fonol_kaldi = fonol_kaldi[-int((len(fonol_kaldi)-2)/2):]

                    # Fix manuaaly the letters to avoid symbols like ' " [ ] ...
                    line_to_file = ''
                    for words in fonol_kaldi:
                        line_to_file = line_to_file + words + ' '
                    line_to_file = line_to_file[:-1]

                    tier2.append(line_aux_tier2.replace('sounding', line_to_file))
                elif "silences" in line:
                    tier2.append(line_aux_tier2.replace('silences', "fonol."))
                elif "item [1]" in line:
                    tier2.append(line_aux_tier2.replace('item [1]', "item [2]"))
                else:
                    tier2.append(line_aux_tier2)
            # end if i > 7

            if "sounding" in line:
                word_kaldi = kaldi_annotated_file.readline()
                word_kaldi = word_kaldi.split()
                word_kaldi = word_kaldi[2:2+int((len(word_kaldi)-2)/2)]

                # Fix manuaaly the letters to avoid symbols like ' " [ ] ...
                line_to_file = ''
                for words in word_kaldi:
                    line_to_file = line_to_file + words + ' '
                line_to_file = line_to_file[:-1]

                textgrid_annotated_file.write(line_aux.replace('sounding', line_to_file))
            elif "silences" in line:
                textgrid_annotated_file.write(line_aux.replace('silences', "Transcripción"))
            elif "size = 1" in line:
                textgrid_annotated_file.write(line_aux.replace('1', "2"))
            else:
                textgrid_annotated_file.write(line_aux)
           # end if
        # end for

        for line in tier2:
            textgrid_annotated_file.write(line)

        kaldi_annotated_file.close()
        textgrid_file.close()
        textgrid_annotated_file.close()
    # end for
# end kal_annot_to_textgrid_annot


def main(argv):
    """Main script

    :param argv: arguments of script.
    :returns: None.
    """

    # ----------------------- ARGUMENT PARSING -------------------------------#
    modeTrain = True
    if len(sys.argv) == 1:
        print("\nNo argument indicated. Kaldi ASR is performing train.\n")
    elif sys.argv[1] == 'test':
        modeTrain = False
    else:
        print("\nWrong argument indicated. Kaldi ASR is performing train.\n")
    # end if


    # Path path with data
    audio_path = 'audio/experiment_lm'
    no_kal_path = 'audio/experiment_lm/no_kal_audio'
    audio_no_annot_path = 'audio_no_annotated'    # audio files to be annotated
    audio_annot_path = 'audio_annotated'          # audio files to be annotated

    textgrid_path = os.path.join(audio_annot_path,'textgrid')                       # textgrid generated by praat
    kaldi_path = os.path.join(audio_annot_path,'kaldi')                             # kaldi from praat
    results_raw_path = 'results/raw'
    kaldi_annotated_path = os.path.join(audio_annot_path,'kaldi_annotated')         # kal generated by kaldi
    textgrid_annotated_path = os.path.join(audio_annot_path,'textgrid_annotated')

    info_user_test_path = 'info_user/test'
    info_user_train_path = 'info_user/train'


    # Check for audio files with no .kal
    train_spks_info = list()
    for file in os.listdir(info_user_train_path):
        if file.endswith(".kal") and not(file.startswith(".")) and not(file.startswith("_")):
            train_spks_info.append(file)
    crossval_spk_functions.clean_wave_files(train_spks_info, audio_path, no_kal_path)


    # path to save results
    create_data_path(audio_annot_path)
    create_data_path(results_raw_path)


    # From audio .wav to .TextGrid with praat
    audio_to_textgrid(audio_no_annot_path, textgrid_path)

    # From .TextGrid to .kal
    textgrid_to_kal(textgrid_path, kaldi_path)


    # If train is indicated we train the GMM/Nnet defined in the path

    # Copy audio no-annotated into audio path
    audio_list = os.listdir(audio_no_annot_path)
    for f in audio_list:
        shutil.copy(os.path.join(audio_no_annot_path,f), audio_path)

    # Train model if indicated
    if modeTrain:
        bashCommand = "python3 run.py --train"
        process = subprocess.Popen(bashCommand,shell=True)
        output, error = process.communicate()

    # Test after training using
    # Copy kal generated to info_user/test
    kal_list = os.listdir(kaldi_path)
    for f in kal_list:
        shutil.copy(os.path.join(kaldi_path,f), info_user_test_path)

        bashCommand = "python3 run.py --test"
        process = subprocess.Popen(bashCommand,shell=True)
        output, error = process.communicate()

        # Result format from raw
        #results_decode_path = 'exp/tri1/decode/scoring_kaldi/wer_details/'

        try:
            results_decode_path = 'exp/nnet2/nnet2_simple/decode/scoring_kaldi/wer_details/'
            speaker = crossval_spk_functions.save_raw_result(results_decode_path)
        except:
            results_decode_path = 'exp/tri1/decode/scoring_kaldi/wer_details/'
            speaker = crossval_spk_functions.save_raw_result(results_decode_path)

        # result_format.extract_results(True, speaker)
        os.remove(os.path.join(info_user_test_path,f))
    # end for


    # Delete audio and kal moved previous
    for f in audio_list:
        os.remove(os.path.join(audio_path,f))

    # From results/raw to kaldi annotated
    results_to_kal_annot(results_raw_path,kaldi_path,kaldi_annotated_path)

    # From kaldi annotated to textgrid annotated
    kal_annot_to_textgrid_annot(kaldi_annotated_path, textgrid_path, textgrid_annotated_path)

# end main


# ----------------------------- MAIN SECTION -------------------------------- #
if __name__ == "__main__":
   main(sys.argv)
# end if



