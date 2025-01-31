import csv
import re
import argparse

WHITESPACE_PLACEHOLDER = '*'
ADJ_LIST_KEY_DELIMITER = '-'

# Function to parse the definition and extract the components
def parse_definition(definition, valid_words):
    root_word = None
    alt_spellings = set()
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
        alt_spellings = {x.strip() for x in alt_spellings_str.split(",")}
        definition = definition[:definition.find(', also ')].strip()

    def_words = definition.split()
    misspelled = []
    for word in def_words:
        if len(word) > 1 and len(word) <= 15 and word.isalpha() and word.islower() and word.upper() not in valid_words:
            misspelled.append(word.upper())

    return root_word, definition, alt_spellings, part_of_speech, conjugations, misspelled

def get_valid_words(file_path):
    valid_words = set()
    with open(file_path, 'r') as file:
        for line in file:
            word = line.split('\t', 1)[0].strip()
            if not word.isupper():  # Check if the word is not in uppercase
                raise ValueError(f"'{word}' is not in all uppercase")
            valid_words.add(word)
    return valid_words

def get_adj_list_key(word, pos):
    return word + ADJ_LIST_KEY_DELIMITER + pos

def decompose_adj_list_key(key):
    word, pos = key.split(ADJ_LIST_KEY_DELIMITER)
    return word, pos

# Function to parse the TSV file
def parse_tsv(file_path):
    valid_words = get_valid_words(file_path)
    parsed_tsv = {}
    adj_list = {}
    with open(file_path, 'r', newline='', encoding='utf-8') as tsv_file:
        reader = csv.reader(tsv_file, delimiter='\t')
        for row in reader:
            word = row[0]
            definitions = row[1].split(' / ')
            for definition in definitions:
                root_word, def_text, alt_spellings, pos, conj, mis = parse_definition(definition, valid_words)
                if not root_word:
                    root_word = word
                elif word == root_word:
                    raise ValueError(f"Word lists itself as a root: '{word}'")

                if conj and len(conj) == 3:
                    conj_set = set(conj)
                    conj_ed = word + 'ED'
                    conj_ing = word + 'ING'
                    conj_s = word + 'S'
                    conj_es = word + 'ES'
                    uses_es = False
                    if conj_ed in conj_set:
                        conj_set.remove(conj_ed)
                    if conj_ing in conj_set:
                        conj_set.remove(conj_ing)
                    if conj_s in conj_set and conj_es not in conj_set:
                        conj_set.remove(conj_s)
                    if conj_es in conj_set and conj_s not in conj_set:
                        conj_set.remove(conj_es)
                        uses_es = True

                    if len(conj_set) == 0:
                        if uses_es:
                            conj = ['-ED', '-ING', '-ES']
                        else:
                            conj = ['-ED', '-ING', '-S']

                entry = {
                    'root': root_word,
                    'def': def_text,
                    'alts': alt_spellings,
                    'pos': pos,
                    'conjs': conj,
                    'mis': mis,
                }
                if word not in parsed_tsv:
                    parsed_tsv[word] = []
                parsed_tsv[word].append(entry)
                neighbors = set()
                for alt in alt_spellings:
                    neighbors.add(get_adj_list_key(alt, pos))
                node_key = get_adj_list_key(root_word, pos)
                if node_key in adj_list:
                    node_val = adj_list[node_key]
                    node_val['defs'].append(def_text)
                    node_val['neighbors'].update(neighbors)
                else:
                    adj_list[node_key] = {
                        'root': root_word,
                        'defs': [def_text],
                        'neighbors': neighbors,
                        'vis': False
                    }

    # Make the graph undirected and remove dead end neighbors
    for node_key, node_val in adj_list.items():
        for neighbor in list(node_val['neighbors']):
            if neighbor not in adj_list:
                node_val['neighbors'].remove(neighbor)
            else:
                adj_list[neighbor]['neighbors'].add(node_key)

    return parsed_tsv, adj_list

def dfs(adj_list, node_key, current_group):
    node_val = adj_list[node_key]
    if node_val['vis']:
        return
    node_val['vis'] = True
    current_group['defs'].extend(node_val['defs'])
    current_group['words'].append(node_val['root'])
    for neighbor in node_val['neighbors']:
        dfs(adj_list, neighbor, current_group)

def print_parsed_tsv(parsed_tsv):
    for word in parsed_tsv:
        print(word)
        for entry in parsed_tsv[word]:
            print("  " + entry['pos'] + ": " + ",".join(entry['alts']))

def print_adj_list(adj_list):
    for node_key, node_val in adj_list.items():
        print(node_key)
        print("  root: " + node_val['root'])
        print("  defs: " + " / ".join(node_val['defs']))
        print("  neighbors: " + ",".join(node_val['neighbors']))

# Main entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse a TSV file of words and definitions.")
    parser.add_argument("file", help="Path to the input TSV file.")
    args = parser.parse_args()

    parsed_tsv, adj_list = parse_tsv(args.file)

    # print_adj_list(adj_list)

    completed_groups = {}
    for node_key in adj_list:
        current_group = {'defs': [], 'words': []}
        dfs(adj_list, node_key, current_group)
        if len(current_group['words']) == 0:
            continue
        def_counts = {}
        for root_def in current_group['defs']:
            sanitized_def = re.sub(r'\s+', WHITESPACE_PLACEHOLDER, root_def)
            if sanitized_def not in def_counts:
                def_counts[sanitized_def] = 0
            def_counts[sanitized_def] += 1
        plurality_def = max(def_counts, key=def_counts.get)
        plurality_def = plurality_def.replace(WHITESPACE_PLACEHOLDER, ' ')
        sorted_alt_spellings = sorted(current_group['words'])
        _, pos = decompose_adj_list_key(node_key)
        for salt in sorted_alt_spellings:
            completed_groups[get_adj_list_key(salt, pos)] = {
                'pdef': plurality_def,
                'alts': sorted_alt_spellings,
            }
    
    for word in parsed_tsv:
        for entry in parsed_tsv[word]:
            root = entry['root']
            adj_list_key = get_adj_list_key(root, entry['pos'])
            if adj_list_key not in completed_groups:
                raise ValueError(f"Key '{adj_list_key}' not found in alt spelling groups")
            completed_alts = completed_groups[adj_list_key]['alts']
            plurality_def = completed_groups[adj_list_key]['pdef']
            entry['alts'] = [x for x in completed_alts if x != root]
            entry['def'] = plurality_def
    
    # print_parsed_tsv(parsed_tsv)
    output_file = "to.tsv"

    with open(output_file, 'w', newline='', encoding='utf-8') as tsv_out:
        writer = csv.writer(tsv_out, delimiter='\t')

        for word, entries in parsed_tsv.items():
            definitions = []
            for entry in entries:
                definition_str = ""

                if entry['root'] and entry['root'] != word:
                    definition_str += f"{entry['root']}, "

                definition_str += entry['def']

                if entry['alts']:
                    definition_str += f", also {', '.join(entry['alts'])}"

                pos_str = f"[{entry['pos']}"
                if entry['conjs']:
                    pos_str += f" {', '.join(entry['conjs'])}"
                pos_str += "]"
                definition_str += " " + pos_str

                definitions.append(definition_str)

            writer.writerow([word, " / ".join(definitions)])