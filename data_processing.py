import re
import scipy.io.wavfile as wav
import sounddevice as sd
import librosa
import soundfile as sf
import pandas as pd
import os
from scipy.io import wavfile

# Convert all wav files to 16kHz
#for audio_wav in os.listdir('audio'):
    #y, s = librosa.load('audio\\' + audio_wav, sr=16000)
    #sf.write('audio\\' + audio_wav, y, s)

# Rules for processing individual rules
    # Pause: \(\.\)
    # Unintelligible: xxx
    # Overlap follows or preceeds: \[<\]|\[>\]
    # Fill missing part: \(s\)
    # Correction of word: \[:.*\] #### TEST REMOVING
    # Mark error: \[\*\]
    # Native language word: \@s
    # Comment (suchs as [% whispers]): \[%\s.*\]
    # Word revision: \[//\] 
    # Best guess: \[\?\]
    # German speech/song: \[\- deu\]
    # Line omitted: ^0
    # Word revisions: \[/\]   #### TEST REMOVING
    # Clarifications (such as 0prep, 0aux): 0(.*?\s)
    # <words>: \<.*\>

# ALSO, ALREADY ADDED TO TRIM RULES
# Trailing off: \+\.\.\. <- Added to line end marker removal
# Interruption: \+\/\. 

# Rules for clearing speaker annotation and everything after line end marker
trimming_rules = [r"\s\.(?=\s).*", r"\s\?(?=\s).*", r"\s\!(?=\s).*", r"\s\+\.\.\.(?=\s).*",
                  r"\s\+\/\.(?=\s).*", r"^\*[A-Z|1-9]{3}:."]

discard_rules = [r"\[<\]|\[>\]", r"\[\- deu\]", r"xxx", r"www",
                 r"^0", r"\[/\]", r"\[\?\]", r"\[:.*\]", r"\<.*\>",r'=\w+']


##################################################
# Start processing files
##################################################



files = ["en111_1", "en111_2", "en111_3", "en111_4", "en111_5",
         "en112_1", "en112_2", "en112_3", "en112_4", "en112_5",
         "en211_1", "en211_2", "en211_3", "en211_4", "en211_5",
         "en212_1", "en212_2", "en212_3", "en212_4"]
df = pd.read_csv('speakers.csv', sep=';')


total_audio_length = 0
id = 0
for file in files:
    # File locations
    audio_loc = 'audio\\' + str(file) + '.wav'
    transcript_loc = 'transcripts\\' + str(file) + '.cha'

    # Get speaker ids
    line = df[df['NAME'] == file][['ID', 'SP1_ID', 'SP2_ID', 'SP1', 'SP2']]
    for index, row in line.iterrows():
            print(f"ID: {row['ID']}")
            sp1 = row['SP1']
            sp1_id = row['SP1_ID']
            sp2_id = row['SP2_ID']

    # Get the wav datafile
    fs, data = wav.read(audio_loc)

    for line in open(transcript_loc, 'r'):
        expression = re.findall(r"^[^|]*", line)[0]

        # Lines with speaker transcripts
        if expression.startswith('*') and not (expression.startswith('*INV:') or expression.startswith('*CAM:')):
            original = expression # For developement

            # Get indices in audio file
            wav_index = re.findall(r"\w+_\w+[0-9]", expression)

            # Process further only if there's matching audio file indices
            if len(wav_index) != 0:

                # Get speaker
                speaker = re.findall(r"^\*[A-Z|1-9]{3}", expression)[0]

                # Trim aways speaker annotation and all after line end
                for trim_rule in trimming_rules:
                    expression = re.sub(trim_rule, "", expression)


                # Discard unusable lines
                skip = False
                for discard_rule in discard_rules:
                    if len(re.findall(discard_rule, expression)) != 0:
                        skip = True
                if skip:
                    #print("Line removed")
                    continue
                
                # Get indices in audio file
                wav_index = wav_index[0].split('_')
                frame_audio = data[int(wav_index[0])*16:int(wav_index[1])*16]

                # Get speaker id

                speaker_id = sp1_id if speaker == sp1 else sp2_id
                
                #if re.findall(r"\(\.\)", expression):
                expression = re.sub(r"\(\.\)|\(\.\.\)", "", expression)
                expression = re.sub(r"\[//\]", "", expression)
                expression = re.sub(r"\[%\s.*\]", "", expression)
                expression = re.sub(r"0(.*?\s)", "", expression)
                expression = re.sub(r"\[\*\]", "", expression)
                expression = re.sub(r"\([a-z]*\)", "", expression)
                expression = re.sub(r"\+", "", expression)
                expression = re.sub(r"\,", "", expression)
                expression = expression.replace("_", " ")
                expression = re.sub(r"([^ ]*)\@s", "<unk>", expression)

                # Save files
                audio_save = 'audio_saves\\' + str(id) + '.wav'
                transcript_save = 'transcript_saves\\' + str(id) + '.txt'

                wavfile.write(audio_save, fs, frame_audio)
                with open(transcript_save, 'w') as f:
                    expression = expression.upper()
                    expression = expression.replace("<UNK>", "<unk>")
                    f.write(expression)

                # Temporary prints instead of saving variables
                print('----------------')
                #print(original)
                #print(expression)
                print("original line:\n", original)
                print("id:", id, "speaker id:", speaker_id, "expression:",
                      expression, "audio length", len(frame_audio),
                      "audio save:", audio_save, "transcript_save:", transcript_save)
                print('----------------')
                total_audio_length += len(frame_audio)

                csv_data = pd.read_csv('data.csv', sep=';')
                    
                new_row = [id, speaker_id, audio_save, transcript_save, expression.replace("  ", " ")]

                csv_data.loc[len(csv_data)] = new_row    

                csv_data.to_csv('data.csv', index=False, header=True, sep=';')
                id += 1 
                

total_audio_length = total_audio_length/16000
print("Total audio length in seconds:", total_audio_length)
mins = total_audio_length / 60
print("In minutes", mins)