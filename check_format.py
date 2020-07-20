#!/usr/bin/env python3
#
# This script check format of .kal files with annotations in info_user/train or / test
#

import os

# ----------------------------- FUNCTIONS  ---------------------------------- #
def checker(path):
    """Takes path_name and create a folder with that path. If exits, removes it before creation.

    :param path: path name when .kal files are stored, e.g., infor_user/train
    :returns: None.
    """
    info_files = list()
    for file in os.listdir(path):
        if file.endswith(".kal") and not(file.startswith(".")) and not(file.startswith("_")):
            info_files.append(file)
        # end if

    cnt = 0
    for file in info_files:

        reader = open(path+file,'r',encoding='utf8', errors='ignore')
        lines = reader.readlines()
        x = lambda a : a.replace('\x00','')
        lines = list(map(x, lines))

        k = 0
        for line in lines:
            k = k + 1
            items = list(line.split('\t'))
            it = 0

            #Cheking errors in each item of the line
            for item in items:
                it = it + 1
                if item.startswith(' '):
                    raise ValueError('ERROR FORMAT in item: '+ item +' from ' +file+ ' at line '+str(k)+' Starts with : \" \"')
                if item.endswith(' '):
                    raise ValueError('ERROR FORMAT in item: '+ item +' from ' +file+ ' at line '+str(k)+' Ends with : \" \"')
                if it == 3:
                    nWord = item.find('  ')
                    if nWord != -1:
                        raise ValueError('ERROR FORMAT in item: '+ item +' from ' +file+ ' at line '+str(k)+' In word section there is a double space')
                if it == 4:
                    nPhonemes = item.find('  ')
                    if nPhonemes != -1:
                        raise ValueError('ERROR FORMAT in item: '+ item +' from ' +file+ ' at line '+str(k)+' In Phoneme section there is a double space')
                # end if
            # end for

            #Cheking semantic content on 3º and 4º item:
            words3 = items[2]
            phonemes4 = items[3]

            itemsWords = list(words3.split(' '))
            itemsPhonemes = list(phonemes4.split(' '))
            x = lambda s : s.replace('_','')
            y = lambda s : s.replace('\n','')
            itemsPhonemes = list(map(x, itemsPhonemes))
            itemsPhonemes = list(map(y, itemsPhonemes))

            if itemsWords != itemsPhonemes:
                cnt = cnt + 1
                print('ERROR FORMAT:  word items DIFFERENT from phonemes items --> Word items = '+ ' '.join(itemsWords) +' Phonemes items = ' + ' '.join(itemsPhonemes) + ' from ' +file+ ' at line '+str(k))
            # end if
        # end for
    # end for

    if cnt == 0:
        print("ALL CORRECT for " + path)
    else:
        print("You've got " + str(cnt) + " errors in your .kal files")
    # end if
# end checker

# ----------------------------- MAIN SECTION -------------------------------- #
if __name__ == "__main__":
    path_train = 'info_user/train/'
    path_test = 'info_user/test/'

    checker(path_train)
    checker(path_test)
# end if

