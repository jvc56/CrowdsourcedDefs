import csv
import re
import argparse

VALID_POS = {'n', 'v', 'adj', 'adv', 'interj', 'pron', 'prep', 'conj'}
KEY_DELIMITER = '###'
VALID_MISSPELLINGS = {'etc'}

def parse_definition(defi, valid_words, word):
    if defi.count('[') != 1:
        raise ValueError("Definition does not have exactly one '[' character: " + defi)
    if defi.count(']') != 1:
        raise ValueError("Definition does not have exactly one ']' character: " + defi)
    if not defi.endswith(']'):
        raise ValueError("Definition does not end with ']' character: " + defi)

    for match in re.finditer(r'\[(^[^\]\s]+)', defi):
        part_of_speech = match.group(1)
        if part_of_speech not in VALID_POS:
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
        if len(word) > 1 and len(word) <= 15 and word.isalpha() and word.islower() and word.upper() not in valid_words and word not in VALID_MISSPELLINGS:
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
    word_def_dict = {}
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
            word_def_dict[word] = all_defis

    parsed_definitions = []

    for word, all_defis in word_def_lines:
        all_defis_split = all_defis.split(' / ')
        for defi in all_defis_split:
            iroot_word, root_word, defi, alt_spellings, part_of_speech, conjugations, misspelled = parse_definition(defi, valid_words, word)
            parsed_definitions.append([iroot_word, root_word, defi, alt_spellings, part_of_speech, conjugations, misspelled, word])

    parsed_tsv = {}
    root_def_to_entry = {}
    num_word_pos = {}
    adj_list = {}
    for iroot_word, root_word, def_text, alt_spellings, pos, conjugations, mis, word in parsed_definitions:
        conjugations_exp = None
        if conjugations:
            conjugations_exp = set()
            total_conjs = 0
            for tenses in conjugations:
                for tense in tenses:
                    conjugations_exp.add(tense[0].replace('-', word))
                    total_conjs += 1
            if len(conjugations) == 3 and total_conjs == 3:
                wl = len(word)
                abrev_conjs = set()
                for tense in conjugations:
                    if len(tense[0][0]) <= wl or tense[0][0][:wl] != word:
                        break
                    abrev_conjs.add(tense[0][0][wl:])
                if abrev_conjs == {'ED', 'ING', 'S'} or abrev_conjs == {'ED', 'ING', 'ES'}:
                    for tense in conjugations:
                        tense[0][0] = '-' + tense[0][0][wl:]

        entry = {
            'iroot': iroot_word,
            'root': root_word,
            'def': def_text,
            'alts': alt_spellings,
            'pos': pos,
            'conjs': conjugations,
            'conjs_exp': conjugations_exp,
            'mis': mis,
            'mis_conj': [],
        }
        if word not in parsed_tsv:
            parsed_tsv[word] = []
        parsed_tsv[word].append(entry)

        word_pos_key = create_key(word, pos)
        if word_pos_key not in num_word_pos:
            num_word_pos[word_pos_key] = 0
        num_word_pos[word_pos_key] += 1
        root_pos_key = create_key(root_word, pos)
        if root_pos_key not in adj_list:
            adj_list[root_pos_key] = {
                'root': root_word,
                'def': def_text,
                'neighbors': set(),
                'vis': False,
            }
        adj_list[root_pos_key]['neighbors'] = adj_list[root_pos_key]['neighbors'].union([create_key(x, pos) for x in alt_spellings])
        if root_word == word:
            root_def_key = create_key(root_word, def_text)
            root_def_to_entry[root_def_key] = entry

    multiple_identical_word_pos = {key for key, value in num_word_pos.items() if value > 1}
    reserved_nodes = set()

    for word in parsed_tsv:
        for entry in parsed_tsv[word]:
            word_pos_key = create_key(word, entry['pos'])
            root_word = entry['root']
            if word_pos_key in multiple_identical_word_pos:
                reserved_nodes.add(create_key(root_word, entry['pos']))
            root_def_key = create_key(root_word, entry['def'])
            if root_def_key not in root_def_to_entry:
                raise ValueError("Definition does not match root word definition: " + word)
            root_entry = root_def_to_entry[root_def_key]
            if entry['iroot'] is None and word != root_word and (root_entry['conjs_exp'] is None or word not in root_entry['conjs_exp']):
                root_entry['mis_conj'].append(word)

    # Make the graph undirected and remove dead end neighbors
    for node_key, node_val in adj_list.items():
        for neighbor in list(node_val['neighbors']):
            if neighbor not in adj_list:
                node_val['neighbors'].remove(neighbor)
            else:
                adj_list[neighbor]['neighbors'].add(node_key)

    return parsed_tsv, adj_list, reserved_nodes, word_def_dict

def dfs(adj_list, node_key, current_group):
    node_val = adj_list[node_key]
    if node_val['vis']:
        return
    node_val['vis'] = True
    if isinstance(current_group, set):
        current_group.add(node_key)
    else:
        current_group['defs'].append(node_val['def'])
        current_group['words'].append(node_val['root'])
    for neighbor in node_val['neighbors']:
        dfs(adj_list, neighbor, current_group)

def has_language_of_origin(root_def: str) -> bool:
    match = re.match(r"^\(.*?\)", root_def.strip())
    return match is not None

# Main entry point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse a TSV file of words and definitions.")
    parser.add_argument("file", help="Path to the input TSV file.")
    parser.add_argument("--validate", action="store_true", default=False, help="Just validates the input without making a new TSV or printing.")
    args = parser.parse_args()

    parsed_tsv, adj_list, start_reserved_nodes, word_def_dict = parse_tsv(args.file)

    # Run the DFS on reserved nodes to mark them as visited
    reserved_nodes = start_reserved_nodes.copy()
    for node_key in start_reserved_nodes:
        if node_key in adj_list:
            dfs(adj_list, node_key, reserved_nodes)

    reserved_words = set()
    for node_key in reserved_nodes:
        word, _ = decompose_key(node_key)
        reserved_words.add(word)

    completed_groups = {}
    for node_key in adj_list:
        current_group = {'defs': [], 'words': []}
        dfs(adj_list, node_key, current_group)
        if len(current_group['words']) == 0:
            continue
        def_counts = {}
        for root_def in current_group['defs']:
            if root_def not in def_counts:
                def_counts[root_def] = 0
            has_loo = 0
            if has_language_of_origin(root_def):
                has_loo = 1
            def_counts[root_def] += 1000000 * has_loo + 1000 + len(root_def)
        plurality_def = max(def_counts, key=def_counts.get)
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
            if adj_list_key not in completed_groups and adj_list_key not in reserved_nodes:
                raise ValueError("Key not found in alt spelling groups: " + adj_list_key)
            if adj_list_key in completed_groups and adj_list_key not in reserved_nodes:
                completed_alts = completed_groups[adj_list_key]['alts']
                plurality_def = completed_groups[adj_list_key]['pdef']
                entry['alts'] = [x for x in completed_alts if x != root]
                entry['def'] = plurality_def

    if args.validate:
        exit(0)

    output_file = "out.tsv"
    new_defs_log = "New Definitions:\n"
    total = 0
    with open(output_file, 'w', newline='', encoding='utf-8') as tsv_out:
        writer = csv.writer(tsv_out, delimiter='\t')

        for word, entries in parsed_tsv.items():
            definitions = []
            tags = ""
            for entry in entries:
                definition_str = ""

                if entry['iroot']:
                    definition_str += f"{entry['iroot']}, "

                if entry['root'] and entry['root'] != word:
                    definition_str += f"{entry['root']}, "

                definition_str += entry['def']

                if entry['alts']:
                    definition_str += f", also {', '.join(entry['alts'])}"

                pos_str = f"[{entry['pos']}"
                if entry['conjs']:
                    tense_strs = []
                    for tense_conjs in entry['conjs']:
                        conj_forms = []
                        current_loo = None
                        for conj, loo in tense_conjs:
                            if loo:
                                current_loo = loo
                            conj_forms.append(conj)
                        tense_str = " or ".join(conj_forms)
                        if current_loo:
                            tense_str += f" {current_loo}"
                        tense_strs.append(tense_str)
                    pos_str += f" {', '.join(tense_strs)}"
                pos_str += "]"
                definition_str += " " + pos_str

                definitions.append(definition_str)

                if entry['iroot']:
                    if tags != "":
                        tags += ", "
                    tags += f"Two Roots ({entry['root']} and {entry['iroot']})"
                if len(entry['mis_conj']) > 0:
                    if tags != "":
                        tags += ", "
                    tags += "Missing/Invalid Conjugations (" + ", ".join(entry['mis_conj']) + ")"
                if len(entry['mis']) > 0:
                    if tags != "":
                        tags += ", "
                    tags += "Invalid Words (" + ", ".join(entry['mis']) + ")"

            if word in reserved_words:
                if tags != "":
                    tags += ", "
                tags += "MultiPOSDef Root"

            old_def = word_def_dict[word]
            new_def = (" / ".join(definitions)).strip()
            new_def_empty_if_same = new_def
            if old_def == new_def:
                new_def_empty_if_same = ""
            else:
                if tags != "":
                    tags += ", "
                tags += "Autosuggestion"
            row_to_write = [word.strip(), old_def.strip(), new_def_empty_if_same, tags]
            if new_def != old_def or tags != "":
                new_defs_log += "\n".join(row_to_write) + "\n\n"
                total += 1
            writer.writerow(row_to_write)
    print(new_defs_log)
    print("Total: ", total)