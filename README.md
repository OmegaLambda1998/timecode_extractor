# Timecode Extractor

Extract timecodes from a video.

## Install

```
python -m venv ./venv

source venv/bin/activate

pip install opencv-python scikit-image
```

There are two ways to do this, either video a command, or through an input csv file.

## Command

```
python timecode_extractor.py -v path/to/sequence.mp4 -t "HH:MM:SS:FF" "HH:MM:SS:FF" -s "source"
```

Here "HH" is the hour, "MM" is the minute, "SS" is the second, and "FF" is the frame, e.g. "00:01:43:17". Assumes there are 25 frames / second.

`source` is the source of the clip, currently only "Nat Geo" is supported.

You can pass as many times as you want to the code, and it will print out the results.

## CSV

If you want to bulk extract timecodes, you may instead want to use the CSV method:
```
python timecode_extractor.py -i path/to/input.csv -o path/to/output.csv
```

`input.csv` must include "Sequence Name" containing the path to the sequence to extract from, "Sequence In", and "Sequence Out", containing the times you want to extract (in `HH:MM:SS:FF` format), and "Source Reel Name", containing the source of the clip.

This will produce (or overwrite) the "Source In", and "Source Out" columns with corrected timecodes, and save it to output.csv.
