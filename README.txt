#PACKAGES NEEDED#
python version used = 3.11.7
packages: soundfile, pandas, numpy, matplotlib, torch, cuda, transformers, datasets, evaluate, jiwer

##FILES NEEDED##
Our dataset audio files were not included as they were too heavy to do so. However, the fine_tuning.ipynb should be understandable withouth those.

Dresden Corpus: https://sla.talkbank.org/TBB/slabank/English/Dresden

#######REMOVING SOME ERRORS IN EXPRESSION######
Please do not run the dara_processing.py file since the data used for the model would be overwritten. Our preprocessing file is not perfect and therefore some modifications need to be done after running the python file by hand.

This modifications were done using a csv reader like Microsoft Excel and Notepad++. In Notepad, paste the expression column from Excel and with the replace tool:
	"\r -> for nothing
	"<whitespace> -> "
	" -> for nothing
	<whitespace><whitespace> -> <whitespace>

Then paste again this text in the column expression in Excel.
Finally, run the delete_unk.py file to remove noisy data.

NOTE: other weird characters may be there, just remove those rows.
	
