# rf_scanner

This repository contains code to control the signalhound BB60c spectrum analyzer used to monitor the physical environment at LIGO laboratory sites.

The following scripts use the API provided by signalhound which must be installed in the proper path (or by setting the environment variable LD_LIBRARY_PATH).
The script bb_api.py contains functions which are python wrappers for the API routines.
The script rf_sweep.py contains the specific programs used to make sweeps of the rf spectrum at the LIGO labs.
If called with no arguments, it will collect sweeps until the next minute divisible by 10; save the collected sweeps; then make a spectrogram plot.
Therefore, for continuous coverage, rf_sweep.py should be called every 10 minutes (such as with cron: */10 * * * * /path/to/rf_sweep.py 1> /path/to/output/file 2> /path/to/error/file)
