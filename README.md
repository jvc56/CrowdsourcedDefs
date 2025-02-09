# Crowdsourced Definitions Tools

The tools assume that definitions files have the following format for each line:

```
<word>\t<definition>
```

## Validate a local definitions file
```
python3 csd.py <definitions_filename>
```

## Create a TSV for crowdsourcing in Google Sheets
```
python3 csd.py <definitions_filename> --create
```

## Download the crowdsourced Google Sheet as a definitions file
```
python3 csd.py
```