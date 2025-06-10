# Crowdsourced Definitions

This repo contains all of the resources for the CSW Crowdsourcing project.

## Links

[Contributors' Guide](https://docs.google.com/document/d/1ZPDaUxzdBAhBfuN1Hg8OK1_tw5pbt020p4X4Stjww80)<br>
[Definitions Spreadsheet](https://docs.google.com/spreadsheets/d/1Msy6NKnhxCoBF23IwlfemSCZpgacJND4sWTQpvi7LZ4)

## Installing the word list into Zyzzyva Desktop


You can directly update your Zyzzyva by overwriting the local lexicon file with the most recent crowdsourced definitions file.

  1. <b> Download the CSW24.zip file. </b>
     1. From the ```editions``` folder, navigate to the most recent edition and download CSW24.zip.
     2. Unzip to extract the CSW24.db file  to a location that you can easily find (like your Downloads folder). This file contains the most recent crowdsourced definitions.
  2. <b> Locate your current Zyzzyva lexicon. </b>

      The CSW24.db file is stored in different locations depending on your operating system:

     - Windows (Collins Zyzzyva):
          ```C:\Users\<your name>\.collinszyzzyva\lexicons```
     - Windows (NASPA Zyzzyva):
          ```C:\Users\<your name>\Zyzzyva\lexicons```
     - MacOS and Linux (Collins Zyzzyva):
          ```~/.collinszyzzyva/lexicons```
     - MacOS and Linux (NASPA Zyzzyva):
          ```~/Zyzzyva/lexicons```

  4. <b> Replace the old CSW24.db file.</b>
      1. Navigate to the lexicons folder and locate the existing CSW24.db file.
      2. (Optional) Rename the file (e.g. CSW24_old.db) in case you need to restore it later.
      3. Copy and paste the new CSW24.db file into the lexicons folder.
         
  5. <b> Restart Zyzzyva </b>
      1. Close Zyzzyva if it was open and reopen it.
      2. Wait for your Zyzzyva to rebuild its CSW24 database.
      3. Verify that the crowdsourced definitions are being used by searching for a word (e.g. GUAC).

## Installing the word list into Zyzzyva Mobile

1. <b>Ensure the Zyzzyva mobile app is connected to your Dropbox</b>
    1. In the Zyzzyva mobile app, navigate to Settings
    2. Link your Dropbox email under 'Data Synchronization'

2. <b> Download the CSW24.zip file. </b>
     1. From the ```editions``` folder, navigate to the most recent edition and download CSW24.zip.
     2. Unzip to extract the CSW24.db file to a location that you can easily find (like your Downloads folder). This file contains the most recent crowdsourced definitions.
     3. You can unzip the file directly on your [iOS](https://support.apple.com/en-us/102532) or [Android](https://support.google.com/files/answer/9048509?hl=en) device.

3. <b>Add the unzipped CSW24.db file to your Dropbox</b>
    1. Copy the unzipped CSW24.db file.
    2. In your Dropbox, go to ```Apps > Zyzzyva > lexicons``` and paste the CSW24.db file.
    3. Make sure to sync your Dropbox so that your Zyzzyva app can access the database file. If you used Dropbox on your desktop to carry out these steps, ensure that you synced your Dropbox app on both your desktop and your phone.

5. <b> Load the lexicon in the Zyzzyva mobile app</b>
    1. In the Zyzzyva app, go to Settings.
    2. Under 'Data Synchronization', press Sync Now. 
    3. Close Zyzzyva if it was open and reopen it.
    4. Verify that the crowdsourced definitions are being used by searching for a word (e.g. GUAC).
    

### Install with the python TK app

This is an optional step to manually update your current CSW24.db file with the crowdsourced CSW24.tsv file. These instructions assume you have the python TK module installed.

Download the add_defs_app.py script and save it to some accessible location. For some operating systems, you may be able to go to the file in your default file explorer application and double click to launch it. If double clicking doesn't work, navigate to the same directory as the file on the command line and run the following command:

```
python add_defs_app.py
```

Once the application starts, follow the instructions.

### Install with python CLI script

Download the add_defs.py script and save it to some accessible location. Navigate to the same directory as the script on the command line and run the following command:

```
python add_defs.py <definitions_file> <database_file>
```

The definitions file is the tab separated definitions file (CSW24.tsv) which lists the word followed by its definition. The .tsv files are provided in the editions directory in this repo. <b>If you would like to download the definitions directly from the crowdsourced Google Sheet, follow the instructions in the Developer Tools section.</b>

The database file argument is the name of the the SQLite database file that contains the words and definitions for Zyzzyva. It should look something like 'CSW24.db' and can usually be found in ```C:\\Users\\<name>\\.collinszyzzyva\\lexicons``` for Collins Zyzzyva or ```C:\\Users\\<name>\\Zyzzyva\\lexicons``` for NASPA Zyzzyva. For MacOS and Linux users it can be found in ```~/.collinszyzzyva/lexicons``` for Collins Zyzzyva or ```~/Zyzzyva/lexicons``` for NASPA Zyzzyva.

## Developer Tools

The tools assume that definitions files have the following format for each line:

```
<word>\t<definition>
```

### Validate a local definitions file
```
python3 csd.py <definitions_filename>
```

### Create a TSV for crowdsourcing in Google Sheets
```
python3 csd.py <definitions_filename> --create
```

### Download the crowdsourced Google Sheet as a definitions file
```
python3 csd.py
```
