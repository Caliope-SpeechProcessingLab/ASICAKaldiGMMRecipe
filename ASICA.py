#!/usr/bin/env python3

import os
import run_iteration
import time
import pandas as pd
import config

# ----------------------------------------------------- MAIN FUNCTION ------------------------------------------------------------------------------#

def main(crossVal_mode, path_kal_test, path_kal_train):

	# config.silentFile_remove('results/global_spk.txt')
	test_spks = list()
	train_spks = list()

	for file in os.listdir(path_kal_test):
	    if file.endswith(".kal") and not(file.startswith(".")) and not(file.startswith("_")):
	    	test_spks.append(file)
	for file in os.listdir(path_kal_train):
	    if file.endswith(".kal") and not(file.startswith(".")) and not(file.startswith("_")):
	    	train_spks.append(file)

	start = time.time()

	#Run each iteration:
	test = test_spks
	train = train_spks

	print('Train set: ')
	print(train)
	print('Test set: ')
	print(test)

	if crossVal_mode == True:
		resume, speaker = run_iteration.main(test, train, True)
		#Results resume:

		print(resume)

		resume.to_csv('results/global_spk.txt', header=None, index=None, sep=' ', mode='a')

		end = time.time()
		print('  ')
		print('--------------------------------------------')
		print('|EXECUTION TIME --> ' + str(end - start)+ ' secs |')
		print('--------------------------------------------')
		print('  ')

		print('  ')
		print('--------------------------------------------')
		print('|EXECUTION TIME --> ' + str((end - start)/60)+ ' min  |')
		print('--------------------------------------------')
		print('  ')

		return speaker

	else:

		resume = run_iteration.main(test, train, False)

		#Results resume:

		print(resume)

		resume.to_csv('results/global_spk.txt', header=None, index=None, sep=' ', mode='a')

		end = time.time()
		print('  ')
		print('--------------------------------------------')
		print('|EXECUTION TIME --> ' + str(end - start)+ ' secs |')
		print('--------------------------------------------')
		print('  ')

		print('  ')
		print('--------------------------------------------')
		print('|EXECUTION TIME --> ' + str((end - start)/60)+ ' min  |')
		print('--------------------------------------------')
		print('  ')


	

	

              

# ----------------------------------------------------- USER VARIABLES ------------------------------------------------------------------------------#


if __name__ == "__main__":


	path_kal_test = "info_user/test"
	path_kal_train = "info_user/train"
	main(False, path_kal_test, path_kal_train)