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

    iroot_word = None
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

    iroot_word_match = re.search(r'^([A-Z]+),', defi)
    if iroot_word_match:
        iroot_word = iroot_word_match.group(1)
        if word == root_word:
            raise ValueError(f"Definition lists word as its own intermediate root word: " + defi)
        defi = defi[len(iroot_word) + 1:].strip()
        iroot_word, root_word = root_word, iroot_word

    pos_and_conj_match = re.search(r'\[([^]]+)\]', defi)
    if pos_and_conj_match:
        pos_and_conj = pos_and_conj_match.group(1)
        split_by_pos = pos_and_conj.split(" ", 1)
        part_of_speech = split_by_pos[0]
        if len(split_by_pos) > 1:
            if not word_is_root_word:
                raise ValueError("Definition lists conjugations for nonroot word: " + defi)
            tenses = split_by_pos[1].split(",")
            tenses = [x.strip() for x in tenses]
            conjugations = []
            loo = None
            for tense in tenses:
                tense_conjs_split = tense.strip().replace("or", " ").split()
                tense_conjs = []
                for conj in tense_conjs_split:
                    conj = conj.strip()
                    if conj[0] == '(' and conj[-1] == ')':
                        if loo is not None:
                            raise ValueError("Conjugation lists multiple languages of origin: " + defi)
                        loo = conj
                        continue
                    if not conj.isupper():
                        print("conj is " + conj)
                        raise ValueError("Definition contains a conjugation '' that is not uppercase: " + defi)
                    tense_conjs.append([conj, loo])
                    loo = None
                conjugations.append(tense_conjs)
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

    return  iroot_word, root_word, defi, alt_spellings, part_of_speech, conjugations, misspelled

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
            iroot_word, root_word, defi, alt_spellings, part_of_speech, conjugations, misspelled = parse_definition(defi, valid_words, word)
            parsed_definitions.append([iroot_word, root_word, defi, alt_spellings, part_of_speech, conjugations, misspelled, word])

    parsed_tsv = {}
    root_def_to_entry = {}
    for iroot_word, root_word, def_text, alt_spellings, pos, conjugations, mis, word in parsed_definitions:
        conjugations_exp = set()
        if conjugations:
            total_conjs = 0
            for tenses in conjugations:
                for tense in tenses:
                    conjugations_exp.add(tense[0].replace('-', word))
                    total_conjs += 1
            if len(conjugations) == 3 and total_conjs == 3:
                wl = len(word)
                abrev_conjs = set()
                for tense in conjugations:
                    if len(tense[0][0]) <= wl:
                        break
                    abrev_conjs.add(tense[0][0][wl:])
                if abrev_conjs == {'ED', 'ING', 'S'} or abrev_conjs == {'ED', 'ING', 'ES'}:
                    for tense in conjugations:
                        tense[0][0] = '-' + tense[0][0][:wl]

        entry = {
            'iroot': iroot_word,
            'root': root_word,
            'def': def_text,
            'alts': alt_spellings,
            'pos': pos,
            'conjs': conjugations,
            'conjs_exp': conjugations_exp,
            'mis': mis,
        }
        if word not in parsed_tsv:
            parsed_tsv[word] = []
        parsed_tsv[word].append(entry)
        if root_word == word:
            root_def_key = create_key(root_word, def_text)
            root_def_to_entry[root_def_key] = entry

    # Set all conjugation definitions to the root word definition
    for word in parsed_tsv:
        for entry in parsed_tsv[word]:
            root = entry['root']
            root_def_key = create_key(root, entry['def'])
            if root_def_key not in root_def_to_entry:
                raise ValueError("Definition does not match root word definition: " + word)
            root_entry = root_def_to_entry[root_def_key]
            if word != root and word not in root_entry['conjs_exp']:
                print("conjs exp: " + str(root_entry['conjs_exp']))
                raise ValueError("Conjugation not listed as a conjugation for the root word: " + word)

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