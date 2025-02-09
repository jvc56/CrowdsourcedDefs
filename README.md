# Crowdsourced Definitions

This repo contains all of the resources for the CSW Crowdsourcing project.

## Links

[Contributors' Guide](https://docs.google.com/document/d/1ZPDaUxzdBAhBfuN1Hg8OK1_tw5pbt020p4X4Stjww80)<br>
[Definitions Spreadsheet](https://docs.google.com/spreadsheets/d/1Msy6NKnhxCoBF23IwlfemSCZpgacJND4sWTQpvi7LZ4)

## Installing the word list into Zyzzyva

### Overwrite the existing CSW db file

You can directly update your Zyzzyva by replacing the local lexicon file with the most recent crowdsourced definitions file.

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

<b>NOTE</b>: You can follow these instructions to update the definitions on your Zyzzyva mobile app as well. First, ensure that your Zyzzyva mobile app is connected to your Dropbox. Then, navigate to ```Apps > Zyzzyva > lexicons``` in your Dropbox and paste the new CSW24.db file there. Close and reopen your Zyzzyva mobile app. You may need to sync your app with Dropbox and rebuild the database for it to work.
    

### Install with the python TK app

These instructions assume you have the python TK module installed.

Download the add_defs_app.py script and save it to some accessible location. For some operating systems, you may be able to go to the file in your default file explorer application and double click to launch it. If double clicking doesn't work, navigate to the same directory as the file on the command line and run the following command:

```
./add_defs_app.py
```

Once the application starts, follow the instructions.

### Install with python CLI script

Download the add_defs.py script and save it to some accessible location. Navigate to the same directory as the file on the command line and run the following command:

```
./add_defs_app.py --defs <definitions_file> --db <database_file>
```

The definitions file is the tab separated definitions file which lists the word followed by its definition. These are provided in the editions directory in this repo. If you would like to download the definitions directly from the crowdsourced Google Sheet, follow the instructions in the Developer Tools section.

The database file argument is the name of the the SQLite database file that contains the words and definitions for Zyzzyva. It should look something like 'CSW24.db' and can usually be found in C:\\Users\\<name>\\.collinszyzzyva\\lexicons for Collins Zyzzyva or C:\\Users\\<name>\\Zyzzyva\\lexicons for NASPA Zyzzyva. For MacOS and Linux users it can be found in ~/.collinszyzzyva/lexicons for Collins Zyzzyva or ~/Zyzzyva/lexicons for NASPA Zyzzyva.

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
