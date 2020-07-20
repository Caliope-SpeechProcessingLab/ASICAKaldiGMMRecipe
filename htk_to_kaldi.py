#!/usr/bin/env python3
#
# This script generates audios files and annotations for kaldi processing.
# It needs a folder strcuture:
#       - /Audios: .wav audios in HTK format ba_S01_T1.wav
#       - /HTK_anotaciones: HTK annotations ba_S01_T1.lab
#            FORMATO HTK (.lab)
#            000000000 000083416 silence
#            000083416 000334706 zu
#            000334706 000470833 silence
#       - /Kaldi_anotaciones: kaldi annotations CAS01Sil_M99.kal
#            FORMATO KALDI (.kal)
#            0.083416 0.334706 zu z_u
#       - /Kaldi_Audios: .wav audios in Kaldi format CAS01Sil_M99.wav
#
#  - If conversion_kind is equal to "all": the annotations and audios are generated for each .wav file in Audio folder.
#
#  - If conversion_kind is not equal to "speaker": the annotations and audios are generated grouped by speaker id.
#
# Variables:
#   Inputs:
#     * folder_HTK: folder /Audio/ where are the HTK audio.
#     * folder_HTK_anot: folder /HTK_anotaciones/ where are the HTK annotations.
#
#   Outputs:
#     * folder_Kaldi: folder /Kaldi_Audios/ where audios are saved with kaldi format name
#     * folder_Kaldi_anot: folder /Kaldi_anotaciones/ where are the KAldi annotations.
#
#
# Authors:
#   - Main programmer: Andres Lozano Duran
#   - Main Supervisor: Ignacio Moreno Torres
#   - Second Supervisor: Enrique Nava Baro
#
# To make all audios and annotations transformation (terminal):
#                         "python3 htk_to_kaldi.py -s all"
# To make audios and annotations transformation grouped by speaker id (terminal):
#                         "python3 htk_to_kaldi.py -s speaker"
# To make audios and annotations using only selected consonants, it only uses ba,be,bi...pa,pe,pi... annotations.
#                         "python3 htk_to_kaldi.py -w b p"
# To make audios and annotations using only selected consonants and using only consonant clases e.g., ba be bi bo bu = ba, pa pe pi po pu = pa. Using this only takes in consideration differences betwwen 'p'+vowel and 'b'+vowel.
#                         "python3 htk_to_kaldi.py -w b p - c True"
#

import os
import sys
import wave
import shutil
import argparse
import numpy as np

# -------------------------------- FUNCTIONS ----------------------------------
def get_time(file):
    """Get duration of every .wav file loaded.

    :param file: .wav file.
    :returns: Duration ins seconds.
    """
    frames = file.getnframes()
    rate = file.getframerate()
    return (frames / float(rate)) # duration in secs
#end get_time


def generate_anotation_kaldi(file, dest, classes):
    """Generate kaldi annotation file.

    :param file: annotation file to convert to kaldi.
    :param dest: folder to save kaldi annotations.
    :param classes: if true it considers ba=be=bi=bo=bu -> ba, if not takes ba,be,bi,.. independently.
    :returns final_text: text to be save as .kal fiel.
    """
    # dest = folder_HTK_anot
    # Generate format for kaldi .kal
    f = open(dest+file[:-3]+'lab','r')
    lines = f.readlines()
    f.close()

    # Ajuste para las anotaciones que vienen en dos líneas vocal y consonante.
    phoneme = ['','','']
    phone_aux = lines[1].split()
    phoneme[0] = phone_aux[0]
    phoneme[2] = phone_aux[2]
    phone_aux = lines[2].split()
    phoneme[1] = phone_aux[1]
    if classes:
        phoneme[2] = phoneme[2]+'a'
    else:
        phoneme[2] = phoneme[2]+phone_aux[2]
    #lines.split()

    final_text = ['','','','']

    # Adjust of text from htk anotation format .lab
    aux_var = phoneme[0]
    aux_var = aux_var[2:]
    aux_var = aux_var[0] + "." + aux_var[1:]
    final_text[0] = aux_var

    aux_var = phoneme[1]
    aux_var = aux_var[2:]
    aux_var = aux_var[0] + "." + aux_var[1:]
    final_text[1] = aux_var

    aux_var = phoneme[2]
    final_text[2] = aux_var

    if len(aux_var) == 2:
        aux_var = aux_var[0] + "_" + aux_var[1]
    elif len(aux_var) == 1:
        aux_var
    else:
        aux_var = aux_var[0:2] + "_" + aux_var[2]
    final_text[3] = aux_var

    return final_text
# end generate_anotation_kaldi

def save_anotation_kaldi(file, dest):
    """Get duration of every .wav file loaded.

    :param file: .kal annotation file.
    :param dest: destination folder to be saved.
    :returns: None.
    """
    fk = open(dest,"w+")
    for line in file:
        i = 0
        max_elements = len(line);
        for word in line:
            fk.write(word)
            i = i + 1
            if i < max_elements:
                fk.write("\t")
        fk.write("\n")
    fk.close();
# end save_anotation_kaldi

# ------------------------------------ MAIN --------------------------------- #
def main(argv):
    """Main script

    :param argv: argument described at top of script.
    :returns: None.
    """

    # --------------------------------- ARGUMENT PARSING ----------------------
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--conversion_kind', help='String to choose the kind of conversion procedure')
    parser.add_argument('-w', '--word_kind', nargs='+', help='Words to be used in kaldi generation')
    parser.add_argument('-c', '--classes', help='Words to be used in kaldi generation')
    args = parser.parse_args()

    if args.conversion_kind == None:
        print("\nNo argument indicated. CrossVal mode set to \"speaker\"")
        conversion_kind = "speaker"
    else:
        # Parsing crossVal mode argument:
        conversion_kind = args.conversion_kind

    if args.word_kind == None:
        print("\nNo letter indicated indicated. Using all")
        word_kind = []
    else:
        # Parsing crossVal mode argument:
        word_kind = list(args.word_kind)
        print("\nUsing words:" + str(word_kind))

    if args.classes == None:
        print("No class indicated.\n")
        classes = False
    else:
        # Parsing crossVal mode argument:
        classes = True
    # ------------------------------ USER VARIABLES ---------------------------

    folder_cwd = os.getcwd()
    # Audio folder
    folder_HTK = folder_cwd + "/Audios/"
    folder_Kaldi = folder_cwd + "/Kaldi_Audios/"
    # Anotations folder
    folder_HTK_anot = folder_cwd + "/HTK_anotaciones/"
    folder_Kaldi_anot = folder_cwd + "/Kaldi_anotaciones/"

    # ------------------------------ MAIN -------------------------------------

    # Generate new folder with kaldi audios, if exists removes content
    try:
        os.mkdir(folder_Kaldi)
        os.mkdir(folder_Kaldi_anot)
    except:
        print('Folder exists. Deleting content.')

        file_list = os.listdir(folder_Kaldi)
        for f in file_list:
            os.remove(folder_Kaldi+f)

        file_list = os.listdir(folder_Kaldi_anot)
        for f in file_list:
            os.remove(folder_Kaldi_anot+f)

    list_files = os.listdir(folder_HTK)
    list_files.sort()

    if conversion_kind  == "speaker":
        # Search for number os subjects in audio files format ba_S01_T1.wav
        tsujs = []
        for file in list_files:
            if ('b' in file or 'd' in file) and not(file.startswith(".")):
                # if not(file.startswith(".")):
                speaker = file.split('_')
                tsujs.append(speaker[1])

        tsujs = np.array(tsujs)
        tsujs = np.unique(tsujs)
        # len_tsujs = len(tsujs)

        for s in tsujs:

            audio_wav = []
            anot_kal = []

            audio_wav = []
            anot_kal = []
            time = []       # duration of .wav audios
            out_name = folder_Kaldi + 'CA' + s + 'Sil_M99.wav'
            out_anotation = folder_Kaldi_anot + 'CA' + s + 'Sil_M99.kal'

            for file in list_files:
                if (word_kind==None or any(ext in file for ext in word_kind)) and (s in file and not(file.startswith(".")) and not(file.startswith("_"))):
                # if s in file and not(file.startswith(".")) and not(file.startswith("_")):

                    w = wave.open(folder_HTK+file, 'rb')
                    audio_wav.append( [w.getparams(), w.readframes(w.getnframes())] )
                    time.append(get_time(w))
                    w.close()

                    # Also generate kaldi anotation
                    anot = generate_anotation_kaldi(file,folder_HTK_anot,classes) # adjust termination name
                    # end if
                    anot_kal.append(anot)

            output = wave.open(out_name, 'wb')
            output.setparams(audio_wav[0][0])

            for params,frames in audio_wav:
                output.writeframes(frames)

            output.close()

            # Adjust time in kal file
            anot_kal = np.asarray(anot_kal)
            columns = anot_kal[:,0:2].astype(float)
            time_cum_sum = np.cumsum(time)

            for i in range(len(time[:-1])):         # last element not necessary
                columns[i+1][:] = columns[i+1][:] + time_cum_sum[i]

            columns = columns.astype(str)
            anot_kal[:,0:2] = columns
            anot_kal = anot_kal.tolist()

            save_anotation_kaldi(anot_kal, out_anotation)
    else:
        # ALL
        # Generate audio file in kaldi format. One for earch audio in HTK format _T1.wav
        for file in list_files:
            if file.endswith("T1.wav") and not(file.startswith(".")) and not(file.startswith("_")):

                speaker = file.split('_')
                sillable = speaker[0]
                speaker = speaker[1][1:3]

                name_kaldi = 'CAS'+speaker+sillable+'_M99.wav'
                shutil.copyfile(folder_HTK+file, folder_Kaldi+name_kaldi)

            #mkdir /tf/Custom_App_backups/Custom_App_2017-12-21 # prepare the target location
            #cp -R /tf/Custom_app/. /tf/Custom_App_backups/Custom_App_2017-12-21 # copy

        list_files = os.listdir(folder_HTK_anot)

        for file in list_files:
            if file.endswith("T1.lab") and not(file.startswith(".")) and not(file.startswith("_")):
                f = open(folder_HTK_anot+file,'r')
                lines = f.readline()
                lines = f.readline()
                f.close()

                phoneme = lines.split()

                final_text = ['','','','']

                # Adjust of data
                aux_var = phoneme[0]
                aux_var = aux_var[2:]
                aux_var = aux_var[0] + "." + aux_var[1:]
                final_text[0] = aux_var

                aux_var = phoneme[1]
                aux_var = aux_var[2:]
                aux_var = aux_var[0] + "." + aux_var[1:]
                final_text[1] = aux_var

                aux_var = phoneme[2]
                final_text[2] = aux_var

                if len(aux_var) == 2:
                    aux_var = aux_var[0] + "_" + aux_var[1]
                else:
                    aux_var = aux_var[0:2] + "_" + aux_var[2]
                final_text[3] = aux_var

                speaker = file.split('_')
                sillable = speaker[0]
                speaker = speaker[1][1:3]

                name_kaldi = 'CAS'+speaker+sillable+'_M99.kal'

                fk = open(folder_Kaldi_anot+name_kaldi,"w+")
                max_elements = 4
                i = 0
                for word in final_text:
                    fk.write(word)
                    i = i + 1
                    if i < max_elements:
                        fk.write("\t")
                fk.close();


    print('Generado los archivos en ' + folder_Kaldi)
    print('Generado los archivos en ' + folder_Kaldi_anot)
# end if


# --------------------------- MAIN SECTION ---------------------------------- #
if __name__ == "__main__":
   main(sys.argv)
# end if


















