# Crowdsourced Definitions changelog

## Under development
- Verify Autosuggestion tags
- Verify alternate spellings


## Edition 2 (2025-06-09)

- Identify malformed and expurgated definitions, misspelled words, missing conjugations, and missing alternative spellings
- Write script to tag (at least) 20,996 definitions that may need to be updated
- Create [2nd Edition CSW24 Crowdsourced Definitions Contributor’s Guide](https://docs.google.com/document/d/1ZPDaUxzdBAhBfuN1Hg8OK1_tw5pbt020p4X4Stjww80/edit?usp=sharing)
- Create [2nd Edition CSW24 Crowdsourced Definitions](https://docs.google.com/spreadsheets/d/1Msy6NKnhxCoBF23IwlfemSCZpgacJND4sWTQpvi7LZ4/edit?usp=sharing) spreadsheet with the tags:
  - Autosuggestion
    - Collapse conjugations if verb inflections are just appended to root word. For a missing conjugation that cannot be collapsed, spell out all conjugations
    - Alphabetize alternate spellings
    - Delete alternate spellings if they do not match the part of speech
    - Add alternate spellings using a [connected components aglorithm](https://en.wikipedia.org/wiki/Component_(graph_theory)) where the words are the nodes and the alternate spellings for the word are the neighboring nodes
    - Make definitions for all alternate spellings of a word consistent
  - Two Roots
    - Remove one root for words with two roots
    - Update definition and part of speech as necessary
  - Missing/Invalid Conjugations
    - Fix definitions with missing conjugations, misspelled conjugations, or conjugations using the wrong definition
    - Remove semicolons and "or" separating comparitives and superlatives from adverbs within the part of speech
  - Invalid Words
    - Fix lowercase words that are not in CSW24 (e.g. "vcr", "eg", and "km")
  - MultiPOSDef Root
    - Fix missing/invalid conjugations for words with multiple definitions for the same part of speech
    - Ensure conjugations have the correct root definition
  - Invalid/Incorrect POS Collapse
    - Fix parts of speech collapsed incorrectly
    - Normalize parts of speech order 
- Create Filter Views for
    - all tags
    - all words ending in -NESS and -NESSES
    - all alternate spellings
    - all unverified words
    - all unverified words for each tag
- Start maintaining a changelog
- Create Errors sheet with remaining validation issues
- Create Autosug sheet with new autosuggested definitions
- Create .db file for the 2nd edition
- Update README.md with Zyzzyva mobile app instructions
- Fix README.md instructions for python CLI script
- Update add_defs_app.py to default to .tsv files


## Edition 1.1 (2025-02-09)

- Preprocess Edition 1 definitions for [connected components algorithm]((https://en.wikipedia.org/wiki/Component_(graph_theory))) and error tagging
- Validate Edition 1 definitions
- Fix misspellings from Edition 1
- Fix misspellings from CSW19
- Fix root words
- Specify language of origin for words (e.g. "Greek" or "Latin" instead of 'historical')
- Add indefinite articles ("a"/"an") to non-specific or non-particular nouns
- Normalize part of speech information
  - Normalize conjugation order (i.e., -S, -ING, -ED)
  - Fix part of speech formatting errors (e.g. "[n -S]" instead of "[n-S]" or "[n]")
  - Fix incorrect/invalid conjugations
  - Spell out part of speech as per precedence
- Add/remove punctuation marks and symbols (";",  ".",  "*") as per precedence
- Remove noun definitions redundant with verb definitions
- Change spellings of base word in defintions to match that of the prefixed words (e.g. DELICENSE/license, MEGALITER/liter, TECHNICOLOUR/colour)
- Create README.md for Crowdsourced Definitions project
- Add editions .db files to repo

## Edition 1 (2024-12-16)

- Create [1st Edition CSW24 Crowdsourced Definitions Contributor's Guide](https://docs.google.com/document/d/1Lg6T4ub1-CZnOGJG6XAxPAzAmz1NBRKypce80uvNnlo/edit?usp=sharing)
- Create [Definitions to Update](https://docs.google.com/spreadsheets/d/1t4XMJiW684soWcETFBbA0ae2T00gOxhq-CARGCR00yc/edit?usp=sharing) spreadsheet
- Use CSW19 definitions
  - Fix 216 definitions (likely) referencing an expurgated word by capitalizing it, removing it, or using a different word to indicate that it is not acceptable in CSW24
  - Delete 6 words expurgated from CSW21
- Fix 1816 additions to CSW24
  - Include starting article ("a", "an", "the") when appropriate
  - Include usage labels (e.g. "obsolete", "historical", "slang") in parentheses at the beginning of the definition
  - Change spellings of base words in defintion to match that of the prefixed words (e.g. DELICENSE/license, MEGALITER/liter, TECHNICOLOUR/colour)
  - For words with the format ``<lowercase word\ (<explanation>) [<part of speech>]``, use the CSW21 definition for lowercased word, and add the CSW21 word as alternate spelling
  - Add alternate spellings in alphabetical order
  - Fix parts of speech
    - Remove incorrect parts of speech where appropriate
    - Remove adjectives redundant with noun definitions and nouns redundant with verb definitions
  - Fix inflections
    - Replace root word with dash when verb inflections are all appended letters
    - Separate multiple plurals by "or" instead of commas
    - Write out multiple plurals in their entirety
- Fix 218 CSW21 definitions with additional inflections
- Add any missing words needing to be updated (e.g. new alternate spellings for existing words)





