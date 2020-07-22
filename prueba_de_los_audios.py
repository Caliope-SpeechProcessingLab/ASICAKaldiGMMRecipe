#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 18 08:49:24 2020

@author: andres
"""
import os
from scipy.io import wavfile

folder = 'audio/experiment_lm'
audios_htk = os.listdir(folder)
audios_htk.sort()

list_fs = list()
for wav in audios_htk:
    #if 'S07' in wav:
    if wav.endswith('.wav'):
        fs, audio = wavfile.read(os.path.join(folder,wav))
        list_fs.append(fs)

print(set(list_fs))




# Para cambiar la frecuencia de muestreo con praat
import os
import parselmouth
from parselmouth.praat import call

audio_folder = 'Audios'          # audio files to be annotated
audio_files = os.listdir(audio_folder)


for audio in audio_files:
    if audio.endswith('.wav'): #  and 'S07' in audio:
        sound = parselmouth.Sound(os.path.join(audio_folder, audio))

        # Take each audio file and convert to textGrid with praat
        manipulation = call(sound, "Resample", 44000, 50) # 'silent', 'sounding'
        # type(manipulation)
        text_audio = audio[:-4] + '.TextGrid'
        textgrid_save = call(manipulation, "Save as WAV file", os.path.join(audio_folder, audio))
    # end if
# end for

audio = 'te_S07_T2_Q.wav'

