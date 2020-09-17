#!/usr/bin/env python3
#
# Este script se ejecuta desde la carpeta donde estén almacenados los audios. Crea dos carpetas /kal/ y /textgrid/ con las anotaciones realizadas.
#
# python3 anotar_audio.py
#
#

import os
import shutil
from scipy.io import wavfile


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


def main():
    """Main script

    :returns: None.
    """
    tgrid_example = ['File type = "ooTextFile"\n','Object class = "TextGrid"\n','\n','xmin = 0\n','xmax = END\n','tiers? <exists>\n','size = 2\n','item []:\n','    item [1]:\n','\tclass = "IntervalTier"\n','\tname = "1"\n','\txmin = 0\n','\txmax = END\n','\tintervals: size = 1\n','\tintervals [1]:\n','\t    xmin = 0\n','\t    xmax = END\n','\t    text = "LETTER"\n', '    item [2]:\n','\tclass = "IntervalTier"\n','\tname = "2"\n','\txmin = 0\n','\txmax = END\n','\tintervals: size = 1\n','\tintervals [1]:\n','\t    xmin = 0\n','\t    xmax = END\n','\t    text = "LETTER"']

    path = os.getcwd()
    kal_path = os.path.join(path,'kal')
    tgrid_path = os.path.join(path,'textgrid')

    create_data_path(kal_path)
    create_data_path(tgrid_path)

    for audio in os.listdir(path):
        if audio.endswith('.wav'):

                spk_name = audio[:-4]
                if 'DEC' in spk_name:
                    letter = 'D'
                elif 'INT' in spk_name:
                    letter = 'I'
                elif 'EXC' in spk_name:
                    letter = 'E'


                ## Anotación audios archivo .kal
                fs, x = wavfile.read(audio)
                end = str(len(x)/fs)

                kal_file = open(kal_path+'/'+spk_name+'.kal','w')
                kal_file.write('0'+'\t'+end+'\t'+letter+'\t'+letter)
                kal_file.close()

                ## Anotación audios archivo .textgrid
                tgrid_file = open(tgrid_path+'/'+spk_name+'.TextGrid','w')
                for line in tgrid_example:
                    if 'END' in line:
                        line = line.replace('END', end)
                    elif 'LETTER' in line:
                        line = line.replace('LETTER', letter)
                    # end if
                    tgrid_file.write(line)
                #end for
                tgrid_file.close()

        # end if
    # end for

# end main


# ----------------------------- MAIN SECTION -------------------------------- #
if __name__ == "__main__":
   # main(sys.argv)
   main()
# end if



