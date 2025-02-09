# Crowdsourced Definitions

This repo contains all of the resources for the CSW Crowdsourcing project.

## Links

[Contributors' Guide](https://docs.google.com/document/d/1ZPDaUxzdBAhBfuN1Hg8OK1_tw5pbt020p4X4Stjww80)
[Definitions Spreadsheet](https://docs.google.com/spreadsheets/d/1Msy6NKnhxCoBF23IwlfemSCZpgacJND4sWTQpvi7LZ4)

## Installing the word list into Zyzzyva

### Overwrite the existing CSW db file

### Install with the python TK app

These instructions assume you have the python TK module installed.

Download the add_defs_app.py script and save it to some accessible location. For some operating systems, you may be able to go to the file in your default file explorer application and double click to launch it. If double clicking doesn't work, navigate to the same directory as the file on the command line and run the following command:

```
./add_defs_app.py
```

Once the application starts, follow the instructions.

### Install with python CLI script



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