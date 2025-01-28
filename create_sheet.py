import csv
import re
import argparse

# Function to parse the definition and extract the components
def parse_definition(definition):
    root_word = None
    alt_spellings = None
    part_of_speech = None
    conjugations = None
    
    definition = definition.strip()

    # Extract root word if it exists
    root_word_match = re.search(r'^([A-Z]+),', definition)
    if root_word_match:
        root_word = root_word_match.group(1)
        definition = definition[len(root_word) + 1:].strip()

    # Extract part of speech and conjugations if they exist
    pos_and_conj_match = re.search(r'\[([^]]+)\]', definition)
    if pos_and_conj_match:
        pos_and_conj = pos_and_conj_match.group(1)
        split_by_pos = pos_and_conj.split(" ", 1)
        part_of_speech = split_by_pos[0]
        if len(split_by_pos) > 1:
            conjugations = split_by_pos[1].split(",")
            conjugations = [x.strip() for x in conjugations]
        definition = definition[:definition.find('[')].strip()
    else:
        raise ValueError(f"definition does not contain part of speech: {definition}")

    # Extract alternate spellings if they exist
    alt_spellings_match = re.search(r', also ([^[]+)', definition)
    if alt_spellings_match:
        alt_spellings_str = alt_spellings_match.group(1)
        alt_spellings = [x.strip() for x in alt_spellings_str.split(",")]
        definition = definition[:definition.find(', also ')].strip()

    return root_word, definition, alt_spellings, part_of_speech, conjugations

# Function to parse the TSV file
def parse_tsv(file_path):
    result = {}
    adj_list = {}
    with open(file_path, 'r', newline='', encoding='utf-8') as tsv_file:
        reader = csv.reader(tsv_file, delimiter='\t')
        for row in reader:
            word = row[0]
            definitions = row[1].split(' / ')

            for definition in definitions:
                root_word, def_text, alt_spellings, pos, conj = parse_definition(definition)
                entry = {
                    'root_word': root_word,
                    'definition': def_text,
                    'alternate_spellings': alt_spellings,
                    'part_of_speech': pos,
                    'conjugations': conj
                }
                if word not in result:
                    result[word] = []
                result[word].append(entry)
                node = root_word
                if node is None:
                    node = word
                node = node + ":" + pos
                neighbors = set()
                if alt_spellings is not None:
                    for alt_spelling in alt_spellings:
                        neighbors.add(alt_spelling + ":" + pos)
                adj_list[node] = {
                    'neighbors': neighbors,
                    'def': def_text,
                    'vis': False
                }

    # Make the graph undirected and remove dead end neighbors
    for node, data in adj_list.items():
        data['neighbors'] = {neighbor for neighbor in data['neighbors'] if neighbor in adj_list}
        for neighbor in data['neighbors']:
            adj_list[neighbor]['neighbors'].add(node)

    return result, adj_list

def dfs(adj_list, node, current_group):
    if adj_list[node]['vis']:
        return
    adj_list[node]['vis'] = True
    current_group.append({'word': node, 'def': adj_list[node]['def']})
    neighbors = adj_list[node]['neighbors']
    for neighbor in neighbors:
        dfs(adj_list, neighbor, current_group)

# Main entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse a TSV file of words and definitions.")
    parser.add_argument("file", help="Path to the input TSV file.")
    args = parser.parse_args()

    parsed_data, adj_list = parse_tsv(args.file)
    all_groups = []
    for node in adj_list:
        if not adj_list[node]['vis']:
            current_group = []
            dfs(adj_list, node, current_group)
            all_groups.append(current_group)

    for group in all_groups:
        words = [x['word'] for x in group]
        sorted_words = sorted(words)
        print(",".join(sorted_words))