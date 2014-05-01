#JMdict2Anki

This Python 3 script was used to generate the
'[JMdict/EDICT readings of common words](https://ankiweb.net/shared/info/1352308220)'
shared [Anki](http://ankisrs.net/) deck from the [JMdict](http://www.edrdg.org/jmdict/edict_doc.html)
XML file.

It can be modified to extract and format other data from the JMdict file.

## Usage

1. Download this repository.
2. Download the [JMdict file](http://www.edrdg.org/jmdict/edict_doc.html)
   gzip file and extract it to get the XML file.
3. In the Python program, change the source and target paths to point to the
   JMdict XML file and the target CSV file respectively.
4. Run the Python program with Python 3.
5. Import the resulting CSV file into Anki.

### Caveat

* I've tried to run this only with the English-language JMdict file. Running this
  with the multi-lingual JMdict file may or may not use up all your memory,
  causing your computer to freeze.
* This script was written for Python 3. It may or may not work in Python 2.

## Modifying the code

The program can be modified to extract other data from JMdict or output other file
formats.

For some useful pointers, see the comments in the Python script and the DTD in
the JMdict file.
