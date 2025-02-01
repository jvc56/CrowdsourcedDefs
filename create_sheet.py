import csv
import re
import argparse

VALID_POS = {'n', 'v', 'adj', 'adv', 'interj', 'pron', 'prep', 'conj'}
WHITESPACE_PLACEHOLDER = '*'
KEY_DELIMITER = '###'

def parse_definition(defi, valid_words, word):
    if defi.count('[') != 1:
        raise ValueError("Definition does not have exactly one '[' character: " + defi)
    if defi.count(']') != 1:
        raise ValueError("Definition does not have exactly one ']' character: " + defi)
    if not defi.endswith(']'):
        raise ValueError("Definition does not end with ']' character: " + defi)

    for match in re.finditer(r'\[(^[^\]\s]+)', defi):
        part_of_speech = match.group(1)
        if part_of_speech not in valid_pos:
            raise ValueError("Definition contains invalid part of speech: " + defi)

    root_word = None
    alt_spellings = set()
    part_of_speech = None
    conjugations = None

    defi = defi.strip()

    word_is_root_word = False
    root_word_match = re.search(r'^([A-Z]+),', defi)
    if root_word_match:
        root_word = root_word_match.group(1)
        if word == root_word:
            raise ValueError(f"Definition lists word as its own root word: " + defi)
        defi = defi[len(root_word) + 1:].strip()
    else:
        root_word = word
        word_is_root_word = True

    pos_and_conj_match = re.search(r'\[([^]]+)\]', defi)
    if pos_and_conj_match:
        pos_and_conj = pos_and_conj_match.group(1)
        split_by_pos = pos_and_conj.split(" ", 1)
        part_of_speech = split_by_pos[0]
        if len(split_by_pos) > 1:
            if not word_is_root_word:
                raise ValueError("Definition lists conjugations for nonroot word: " + defi)
            conjugations = split_by_pos[1].split(",")
            conjugations = [x.strip() for x in conjugations]
            # FIXME: fix the 'or' cases
            # for conj in conjugations:
            #     if not conj.isupper():
            #         raise ValueError(f"Definition contains a conjugation that is not uppercase: " + defi)
        defi = defi[:defi.find('[')].strip()
    else:
        raise ValueError("Definition does not contain part of speech: " + defi)

    alt_spellings_match = re.search(r', also ([^[]+)', defi)
    if alt_spellings_match:
        alt_spellings_str = alt_spellings_match.group(1)
        alt_spellings = {x.strip() for x in alt_spellings_str.split(",")}
        for alt_spelling in alt_spellings:
            if not alt_spelling.isupper():
                raise ValueError(f"Definition contains an alt spelling that is not uppercase: " + defi)
            if alt_spelling not in valid_words:
                raise ValueError(f"Definition contains an alt spelling that is not a valid word: " + defi)
        defi = defi[:defi.find(', also ')].strip()

    def_words = defi.split()
    misspelled = []
    for word in def_words:
        if len(word) > 1 and len(word) <= 15 and word.isalpha() and word.islower() and word.upper() not in valid_words:
            misspelled.append(word.upper())

    return root_word, defi, alt_spellings, part_of_speech, conjugations, misspelled

def create_key(word, pos):
    return word + KEY_DELIMITER + pos

def decompose_key(key):
    return key.split(KEY_DELIMITER)

# Function to parse the TSV file
def parse_tsv(file_path):
    valid_words = set()

    word_def_lines = []
    with open(file_path, 'r') as file:
        for line in file:
            word_and_all_defis = line.split('\t')
            if len(word_and_all_defis) != 2:
                raise ValueError("Line does not have exactly one tab: " + line)
            word = word_and_all_defis[0].strip()
            all_defis = word_and_all_defis[1].strip()
            if word == '':
                raise ValueError("Word is empty: " + line)
            if all_defis == '':
                raise ValueError("Definition is empty: " + line)
            if not word.isupper():
                raise ValueError("Word is not uppercase: " + line)

            valid_words.add(word)
            word_def_lines.append((word, all_defis))

    parsed_definitions = []

    for word, all_defis in word_def_lines:
        all_defis_split = all_defis.split(' / ')
        for defi in all_defis_split:
            root_word, defi, alt_spellings, part_of_speech, conjugations, misspelled = parse_definition(defi, valid_words, word)
            parsed_definitions.append([root_word, defi, alt_spellings, part_of_speech, conjugations, misspelled, word])

    parsed_tsv = {}
    root_def_set = set()
    for root_word, def_text, alt_spellings, pos, conj, mis, word in parsed_definitions:
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
        if root_word == word:
            sanitized_def = re.sub(r'\s+', WHITESPACE_PLACEHOLDER, def_text)
            root_def_key = create_key(root_word, sanitized_def)
            print("Adding key: " + root_def_key)
            root_def_set.add(root_def_key)

    # Set all conjugation definitions to the root word definition
    for word in parsed_tsv:
        for entry in parsed_tsv[word]:
            sanitized_def = re.sub(r'\s+', WHITESPACE_PLACEHOLDER, entry['def'])
            root_def_key = create_key(entry['root'], sanitized_def)
            if root_def_key not in root_def_set:
                print("Cound not find key of: " + root_def_key)
                print(f"Mismatched def for: '{entry['root']}' ({entry['pos']})")

    exit(0)


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
        _, pos = decompose_key(node_key)
        for salt in sorted_alt_spellings:
            completed_groups[create_key(salt, pos)] = {
                'pdef': plurality_def,
                'alts': sorted_alt_spellings,
            }
    
    for word in parsed_tsv:
        for entry in parsed_tsv[word]:
            root = entry['root']
            adj_list_key = create_key(root, entry['pos'])
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