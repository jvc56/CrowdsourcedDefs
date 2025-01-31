import argparse
import re

def validate_lines(filename):
    valid_pos = {'n', 'v', 'adj', 'adv', 'interj', 'pron', 'prep', 'conj'}  # Set of valid parts of speech

    valid_words = {}

    with open(filename, 'r') as file:
        for line in file:
            word = line.split('\t', 1)[0].strip()
            
            if not word.isupper():  # Check if the word is not in uppercase
                raise ValueError(f"'{word}' is not in all uppercase")
            
            valid_words[word] = True  # Add the valid word to the dictionary

    with open(filename, 'r') as file:
        for line_number, line in enumerate(file, 1):
            line = line.rstrip()  # Remove trailing newline or spaces
            count_open = line.count('[')
            count_close = line.count(']')
            count_slash = line.count(' / ')

            # Check for invalid parts of speech after '['
            invalid_pos_found = False
            for match in re.finditer(r'\[([a-z\-]+)', line):
                part_of_speech = match.group(1)
                if part_of_speech not in valid_pos:
                    print("invalid pos: " + part_of_speech)
                    invalid_pos_found = True
                    break
            
            for match in re.finditer(r', also ([^[]+)', line):
                alt_spellings_str = match.group(1)
                alt_spellings = [x.strip() for x in alt_spellings_str.split(",")]
                for alt_spelling in alt_spellings:
                    if not alt_spelling.isupper():
                        raise ValueError(f"alt spelling '{word}' is not in all uppercase")
                    if alt_spelling not in valid_words:
                        raise ValueError(f"alt spelling '{word}' is not a valid word")

            # Perform the checks
            if (
                not line.endswith(']') or          # Check if line ends with ']'
                count_open != count_close or       # Check if '[' and ']' counts are equal
                count_open != count_slash + 1 or   # Check if '[' count is one more than '/' count
                invalid_pos_found                  # Check for invalid parts of speech
            ):
                print(f"Line {line_number}: {line}")  # Print the line if it fails any check

def main():
    parser = argparse.ArgumentParser(description="Validate lines in a file based on specific criteria.")
    parser.add_argument("input_file", help="Path to the input file")
    args = parser.parse_args()

    validate_lines(args.input_file)

if __name__ == "__main__":
    main()