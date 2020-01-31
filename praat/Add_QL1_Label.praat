###################################################
# This script will detect the intervals with a "Sounding" label and 
# replace the "sounding" text with a specified text. It is meant to be used
# to annotate audios in which the speaker participates in a Repetition task
# This specific file has the annotations for task QL1 used in ASICA project.

# Before you start:
# You must have one audio file in which the only utterances correspond to the 
# items in the specified repetition task (there should be nothing else; for instance
# no Name of speaker, date... at the start of the audio file.

# To run this script:
# Select in Praat, the audio file and clic Run
# If you are lucky, a TextGrid file will be created that can be easily 
# saved as a Kaldi annotations file. 
# However, if the speaker missed one item or produces twice or more a single
# utterance, the annotations might be displaced. 


soundname$ = selected$ ("Sound", 1)
To TextGrid (silences): 100, 0, -35, 0.3, 0.15, "", "sounding"
Rename: "textgrid1"
Copy: "textgrid2"

selectObject: "TextGrid textgrid1"
plusObject: "TextGrid textgrid2"
Merge

Rename: soundname$

textgrid$ = selected$ ("TextGrid", 1)

selectObject: "TextGrid textgrid1"
plusObject: "TextGrid textgrid2"
Remove

tier1 = 1
tier2 = 2

selectObject: "TextGrid 'soundname$'"
ni = Get number of intervals... tier1


# Annotations for sylables (Tier 1) and phonemes (Tier 2)
# PENDIENTE REVISAR!!!

sylbs$[1] = "ya te"
sylbs$[2] = "no lu"
sylbs$[3] = "ba ze"
sylbs$[4] = "ti tu lo"
sylbs$[5] = "mo de"
sylbs$[6] = "pe no"
sylbs$[7] = "xe ra"
sylbs$[8] = "pa le ti ya"
sylbs$[9] = "ka rro fa"
sylbs$[10] = "ma po"
sylbs$[11] = "chu lo"
sylbs$[12] = "pa ba ri no"
sylbs$[13] = "ko pa di"
sylbs$[14] = "li ga"
sylbs$[15] = "be yo lu"
sylbs$[16] = "so te to"
sylbs$[17] = "ma re xa za"
sylbs$[18] = "nu me ro"
sylbs$[19] = "ka pi tu bo"
sylbs$[20] = "bi ka"
sylbs$[21] = "ti bo"
sylbs$[22] = "ka yi"
sylbs$[23] = "fo bo xe ma"
sylbs$[24] = "pa ne"
sylbs$[25] = "tu fo"
sylbs$[26] = "sa te li to"
sylbs$[27] = "fe cha"
sylbs$[28] = "pe mi"
sylbs$[29] = "di ne so"
sylbs$[30] = "ka ba ye te"
sylbs$[31] = "ko li za"
sylbs$[32] = "ka rro ma do"
sylbs$[33] = "gi nyo"
sylbs$[34] = "ma nya da"
sylbs$[35] = "za ze lu di"
sylbs$[36] = "la ro"
sylbs$[37] = "ci ne"
sylbs$[38] = "se nyo ri ta"
sylbs$[39] = "no fe"
sylbs$[40] = "pe li ku la"
sylbs$[41] = "ku xo ba"
sylbs$[42] = "fu xo"
sylbs$[43] = "se ku"
sylbs$[44] = "to rre"
sylbs$[45] = "do fe"
sylbs$[46] = "ba rre nyo"
sylbs$[47] = "me la ni to"
sylbs$[48] = "ta le go"

phonemes$[1] = "y_a t_e"
phonemes$[2] = "n_o l_u"
phonemes$[3] = "b_a z_e"
phonemes$[4] = "t_i t_u l_o"
phonemes$[5] = "m_o d_e"
phonemes$[6] = "p_e n_o"
phonemes$[7] = "x_e r_a"
phonemes$[8] = "p_a l_e t_i y_a"
phonemes$[9] = "k_a rr_o f_a"
phonemes$[10] = "m_a p_o"
phonemes$[11] = "ch_u l_o"
phonemes$[12] = "p_a b_a r_i n_o"
phonemes$[13] = "k_o p_a d_i"
phonemes$[14] = "l_i g_a"
phonemes$[15] = "b_e y_o l_u"
phonemes$[16] = "s_o t_e t_o"
phonemes$[17] = "m_a r_e x_a z_a"
phonemes$[18] = "n_u m_e r_o"
phonemes$[19] = "k_a p_i t_u b_o"
phonemes$[20] = "b_i k_a"
phonemes$[21] = "t_i b_o"
phonemes$[22] = "k_a y_i"
phonemes$[23] = "f_o b_o x_e m_a"
phonemes$[24] = "p_a n_e"
phonemes$[25] = "t_u f_o"
phonemes$[26] = "s_a t_e l_i t_o"
phonemes$[27] = "f_e ch_a"
phonemes$[28] = "p_e m_i"
phonemes$[29] = "d_i n_e s_o"
phonemes$[30] = "k_a b_a y_e t_e"
phonemes$[31] = "k_o l_i z_a"
phonemes$[32] = "k_a rr_o m_a d_o"
phonemes$[33] = "g_i ny_o"
phonemes$[34] = "m_a ny_a d_a"
phonemes$[35] = "z_a z_e l_u d_i"
phonemes$[36] = "l_a r_o"
phonemes$[37] = "c_i n_e"
phonemes$[38] = "s_e ny_o r_i t_a"
phonemes$[39] = "n_o f_e"
phonemes$[40] = "p_e l_i k_u l_a"
phonemes$[41] = "k_u x_o b_a"
phonemes$[42] = "f_u x_o"
phonemes$[43] = "s_e k_u"
phonemes$[44] = "t_o rr_e"
phonemes$[45] = "d_o f_e"
phonemes$[46] = "b_a rr_e ny_o"
phonemes$[47] = "m_e l_a n_i t_o"
phonemes$[48] = "t_a l_e g_o"

# Sounding is replaced by a silable in tier 1 and phonemes in tier 2
    select TextGrid 'textgrid$'
	utteranceN = 1
        for i to ni
			labelActual$ = Get label of interval... tier1 i
			if (labelActual$ = "sounding")  
				sylables$=sylbs$[utteranceN]
				phones$ = phonemes$[utteranceN]
		        Set interval text... tier1 i 'sylables$'
		        Set interval text... tier2 i 'phones$'
				utteranceN = utteranceN + 1
				endif
		  endif
        endfor



