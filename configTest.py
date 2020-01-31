import os
import shutil
import errno
import csv
import pandas as pd
import subprocess
import re

# ----------------------------------------- auxiliar function utils ---------------------------------------------

def check_kal_names(filenames):
    for filename in filenames:
        if not re.match(r"[a-zA-Z0-9]+_[a-zA-Z0-9]+", filename):
            raise ValueError('FILENAME FORMAT ERROR IN: ' + filename + ' It MUST consists on \"CHARACTERS_CHARACTERS\"')
#        else:
#            print('Correct format name for: ' + filename)

def silentDirectory_remove(filename):
    try:
        shutil.rmtree(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred

def silentFile_remove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred

def search_by_subject(id,path):
    filenames = os.listdir(path)
    for ifile in filenames:
        if ifile.startswith(id):
            return ifile



def getColumns(filename,path):
#    print("Path: ")
#    print(path)
#    print("Filename: ")
#    print(filename)
#    print(path + filename)
    data = pd.DataFrame(columns=('Start', 'End', 'Word Transcription', 'Phoneme Transcription'))
    reader = open(path + filename, 'r', errors='ignore')
    lines = reader.readlines()

    for line in lines:
        line = bytes(line, 'utf-8').decode('utf-8', 'ignore')
        items = line.split('\t')
        data.loc[len(data)] = items

    return data

def hexa2dec(L_in):
    L_out = list()

    for item in L_in:
        L_out.append(item.replace('\x00',''))

    return L_out

def make_uttID(recording_id, nRows):

    s = list()
    for i in range(nRows):
        s.append(recording_id + '-utt' + str(i))

    return s

def unique(list1):

    unique_list = []

    # traverse for all elements
    for x in list1:
        if x not in unique_list:
            unique_list.append(x)

    return unique_list

def check_WAV_KAL(wav_path,kal_filenames,train):
    wav_filenames = os.listdir(wav_path)

    x = lambda filename : filename[:-4]
    wav_filenames = list(map(x,wav_filenames))
    kal_filenames = list(map(x,kal_filenames))

    if train == 'yes':
        for kal_file in kal_filenames:
            if kal_file not in wav_filenames:
                raise ValueError('A .kal file does not have its .wav file correspondence. Specifically: ' + kal_file + '  You need to insert it in the train folder a .WAV file with that name.')
    if train == 'no':
        for kal_file in kal_filenames:
            if kal_file not in wav_filenames:
                raise ValueError('A .kal file does not have its .wav file correspondence. Specifically: ' + kal_file + '  You need to insert it in the test folder a .WAV file with that name.')

def check_path_names(path_list):
    for path in path_list:
        if path[-1] != '/':
            raise ValueError('Path name: ' + path + '  NOT contains a / character at the end.')


# ----------------------------------------- auxiliar file creators ---------------------------------------------
def makeSegments(dataDict, path):
    s = ''
    for rec_id, df in dataDict.items():
        for index, row in df.iterrows():
            s = s + row['utterance ID'] + ' ' + rec_id + ' ' + row['Start']  + ' ' + row['End'] + '\n'


    writer = open(path + 'segments','+w')
    writer.write(s)
    writer.close()

def makeWav(dataDict, path, audios_path):
    print(audios_path)
    w = ''
    for rec_id, df in dataDict.items():
        w = w + rec_id + ' ' + audios_path + rec_id + '.wav' + '\n'
    print(w)
    print(path)
    writer = open(path + 'wav.scp','+w')
    writer.write(w)
    writer.close()

def makeText(dataDict, path):

    t = ''
    for rec_id, df in dataDict.items():
        for index, row in df.iterrows():
            t = t + row['utterance ID'] + ' ' + row['Word Transcription'] + '\n'

    writer = open(path + 'text','+w')
    writer.write(t)
    writer.close()

def makeUtt2spk(dataDict, path):

    u = ''
    for rec_id, df in dataDict.items():
        for index, row in df.iterrows():
            speaker = row['utterance ID'].split('-')
            u = u + row['utterance ID'] + ' ' + speaker[0] + '\n'

    writer = open(path + 'utt2spk','+w')
    writer.write(u)
    writer.close()


def lexiconDict(dataDict):
    words =list()
    phonemes =list()
    for rec_id, df in dataDict.items():
        word_phoneme = df[['Word Transcription','Phoneme Transcription']]
        for index, row in word_phoneme.iterrows():
            irowWord = str(row['Word Transcription'])
            irowPhonemes = str(row['Phoneme Transcription'])
            if len(irowWord.split(' ')) != len(irowPhonemes.split(' ')):
                raise ValueError('Format error in line: ' + str(index))
            for iword in irowWord.split(' '):
                words.append(iword)
            for iphoneme in irowPhonemes.split(' '):
                phonemes.append(iphoneme)

    phonemes = list(map(lambda s: s.strip('\n'),phonemes))

    x = ''
    new_dict = {}
    for i in range(len(words)):
        if words[i] not in new_dict.keys():
            new_dict[words[i]] = x.join(list(map(lambda s: s.replace('_',' '),phonemes[i])))
    if len(words) != len(phonemes):
        raise ValueError('Words: '+ str(len(words)) +'Phonemes: '+str(len(phonemes)))


    return new_dict,new_dict.values()



def uniquePhonemes(phonemes_per_word):

    phonemes = list()
    for iphonemes in phonemes_per_word:
        for iphoneme in iphonemes.split():
            phonemes.append(iphoneme)
    phonemes = unique(phonemes)

    return phonemes



def makeLexicon(lexDict,path):

    l = '<SIL> SIL\n'
    for word, phonemes in lexDict.items():
        l = l + word + ' ' + phonemes + '\n'


    writer = open(path + 'lexicon.txt','+w')
    writer.write(l)
    writer.close()

def makeLexiconP(lexDict, path):

    l = '<SIL> 1.0 SIL\n'
    for word, phonemes in lexDict.items():
        l = l + word + ' ' + '1.0' + ' ' + phonemes + '\n'

    writer = open(path + 'lexiconp.txt','+w')
    writer.write(l)
    writer.close()


def makeNonSilencePhones(phonemes,path):

    n = ''
    for iphoneme in phonemes:
        n = n + iphoneme + '\n'


    writer = open(path + 'nonsilence_phones.txt','+w')
    writer.write(n)
    writer.close()

def makeOptionalSilence(path):

    o = 'SIL\n'
    writer = open(path + 'optional_silence.txt','+w')
    writer.write(o)
    writer.close()



def makeSilencePhones(path):

    o = 'SIL\n'
    writer = open(path + 'silence_phones.txt','+w')
    writer.write(o)
    writer.close()


def makeCorpus(words, path):

    c = ''
    for iword in words:
        c = c + iword + '\n'

    writer = open(path + 'corpus.txt','+w')
    writer.write(c)
    writer.close()







def main(test_ID, audiosTest_path, testInfo_path):

# ------------------------------------------- SETTING UP VARIABLES ---------------------------------------------

    dataTest_path = 'data/test/'

    check_path_names([testInfo_path,dataTest_path,audiosTest_path])


# --------------------------------------------- MAIN PROCEDURES ---------------------------------------------

# Setting up folders

    #Extract ids recording information:

    tsDataDict = {}

    silentDirectory_remove(dataTest_path)
    os.mkdir(dataTest_path)

    #Check .kal filename format:
    check_kal_names(test_ID)

    #Check exact same filenames from .kal files to .wav files:
    check_WAV_KAL(audiosTest_path,test_ID, 'no')

    #print('Test files: ')
    for id in test_ID:

        filename = search_by_subject(id,testInfo_path)
        cols = getColumns(filename,testInfo_path)
        cols['Start'] = hexa2dec(list(cols['Start']))
        cols['End'] = hexa2dec(list(cols['End']))
        cols['Word Transcription'] = hexa2dec(list(cols['Word Transcription']))
        cols['Phoneme Transcription'] = hexa2dec(list(cols['Phoneme Transcription']))
        utt_id = make_uttID(filename[:-4], len(cols['Start']))
        cols.insert(0, 'utterance ID', utt_id)
        tsDataDict[filename[:-4]] = cols

    #print('Test Dictionary')
    #print(tsDataDict)


#Make segment files
    makeSegments(tsDataDict, dataTest_path)

#Make wavs.scp file
    makeWav(tsDataDict, dataTest_path, audiosTest_path)

#Make text file
    makeText(tsDataDict, dataTest_path)


#Make utt2spk file
    makeUtt2spk(tsDataDict, dataTest_path)

#Make spk2utt file

    from subprocess import Popen
    bashCommand = "utils/utt2spk_to_spk2utt.pl data_init/test/utt2spk > data_init/test/spk2utt"
    process = Popen(bashCommand,shell=True)
    output, error = process.communicate()


