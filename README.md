# Crowdsourced Definitions

This repo contains all of the resources for the CSW Crowdsourcing project.

## Links

[Contributors' Guide](https://docs.google.com/document/d/1ZPDaUxzdBAhBfuN1Hg8OK1_tw5pbt020p4X4Stjww80)
[Definitions Spreadsheet](https://docs.google.com/spreadsheets/d/1Msy6NKnhxCoBF23IwlfemSCZpgacJND4sWTQpvi7LZ4)

## Installing the word list into Zyzzyva

### Overwrite the existing CSW db file

holp

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