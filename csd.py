import csv
import re
import argparse
import requests
from io import StringIO

VALID_POS = {'n', 'v', 'adj', 'adv', 'interj', 'pron', 'prep', 'conj'}
KEY_DELIMITER = '###'
ROOT_WORD_EXCEPTIONS = {'LOAST', 'LOSEN', 'SURBET'}
SPECIAL_LOOS = {'obsolete', 'archaic', 'Spenser', 'Milton'}
RETRIEVED_FILENAME = 'latest_edition.txt'
TSV_URL = "https://docs.google.com/spreadsheets/d/1Msy6NKnhxCoBF23IwlfemSCZpgacJND4sWTQpvi7LZ4/export?format=tsv"


def parse_definition(defi, valid_words, word, existing_words_info):
    if defi.count('[') != 1:
        raise ValueError("definition does not have exactly one '[' character: " + defi)
    if defi.count(']') != 1:
        raise ValueError("definition does not have exactly one ']' character: " + defi)
    if not defi.endswith(']'):
        raise ValueError("definition does not end with ']' character: " + defi)

    for match in re.finditer(r'\[(^[^\]\s]+)', defi):
        part_of_speech = match.group(1)
        if part_of_speech not in VALID_POS:
            raise ValueError("definition contains invalid part of speech: " + defi)

    root_word = None
    loo = None
    alt_spellings = set()
    part_of_speech = None
    conjugations = None

    defi = defi.strip()

    word_is_root_word = False
    root_word_match = re.search(r'^([A-Z]+),', defi)
    if root_word_match:
        root_word = root_word_match.group(1)
        if word == root_word:
            raise ValueError(f"definition lists word as its own root word: " + defi)
        defi = defi[len(root_word) + 1:].strip()
    else:
        root_word = word
        word_is_root_word = True

    loo_match = re.search(r'^\(([^)]+)\)', defi)
    if loo_match:
        loo = loo_match.group(1)
        # Use +2 to account for the parens 
        defi = defi[len(loo)+2:].strip()

    pos_and_conj_match = re.search(r'\[([^]]+)\]', defi)
    if pos_and_conj_match:
        pos_and_conj = pos_and_conj_match.group(1)
        split_by_pos = pos_and_conj.split(" ", 1)
        part_of_speech = split_by_pos[0]
        if len(split_by_pos) > 1:
            if not word_is_root_word and word not in ROOT_WORD_EXCEPTIONS:
                raise ValueError("definition lists conjugations for nonroot word: " + word + ", " + defi)
            tenses = split_by_pos[1].split(",")
            tenses = [x.strip() for x in tenses]
            conjugations = []
            for tense in tenses:
                tense_conjs_split = tense.strip().replace("or", " ").split()
                tense_conjs = []
                for conj in tense_conjs_split:
                    conj = conj.strip()
                    if conj[0] == "(" and conj[-1] == ")":
                        continue
                    if not conj.isupper():
                        raise ValueError("definition contains a conjugation '' that is not uppercase: " + defi)
                    tense_conjs.append(conj)
                conjugations.append(tense_conjs)
        defi = defi[:defi.find('[')].strip()
    else:
        raise ValueError("definition does not contain part of speech: " + defi)

    if existing_words_info and word in existing_words_info and existing_words_info[word]['pos'] == part_of_speech and existing_words_info[word]['is_root'] != word_is_root_word:
        raise ValueError("invalid root status: " + word)

    alt_spellings_match = re.search(r', also ([^[]+)', defi)
    if alt_spellings_match:
        alt_spellings_str = alt_spellings_match.group(1)
        alt_spellings = {x.strip() for x in alt_spellings_str.split(",")}
        for alt_spelling in alt_spellings:
            if not alt_spelling.isupper():
                raise ValueError(f"definition contains an alt spelling that is not uppercase: " + defi)
            if alt_spelling not in valid_words:
                raise ValueError(f"definition contains an alt spelling that is not a valid word: " + defi)
        defi = defi[:defi.find(', also ')].strip()

    def_words = defi.split()
    misspelled = []
    for def_word in def_words:
        if len(def_word) > 1 and len(def_word) <= 15 and def_word.isalpha() and def_word.islower() and def_word.upper() not in valid_words:
            misspelled.append(def_word.upper())

    if len(misspelled) > 0:
        raise ValueError(f"{word.upper()} definition has mispelled word(s): " + ", ".join(misspelled))

    return root_word, loo, defi, alt_spellings, part_of_speech, conjugations

def create_key(word, pos):
    return word + KEY_DELIMITER + pos

def decompose_key(key):
    return key.split(KEY_DELIMITER)

# Function to parse the TSV file
def parse_tsv(file_path, existing_lexicon):
    valid_words = set()

    word_def_lines = []
    word_def_dict = {}
    errors = []

    existing_words_info = None
    if existing_lexicon:
        existing_words_info = {}
        with open(existing_lexicon, 'r') as file:
            for line in file:
                word_and_defi = line.split('\t')
                if len(word_and_defi) != 2:
                    errors.append("line does not have exactly one tab: " + line)
                    continue
                word = word_and_defi[0].strip()
                all_defis = word_and_defi[1].strip()
                all_defis_split = all_defis.split(' / ')
                for defi in all_defis_split:
                    is_conj = re.search(r'^([A-Z]+),', defi)
                    word_is_root = is_conj is None
                    pos_matches = re.findall(r'\[(\w+)', defi)
                    if len(pos_matches) != 1:
                        errors.append(f"word {word} does not have exactly one part of speech")
                        continue
                    pos = pos_matches[0]
                    if pos not in VALID_POS:
                        errors.append(f"word {word} has invalid part of speech: {pos}")
                        continue
                    existing_words_info[word.upper()] = {
                        'is_root': word_is_root,
                        'pos': pos
                    }

        if errors:
            return None, None, None, None, errors

    with open(file_path, 'r') as file:
        for line in file:
            word_and_all_defis = line.split('\t')
            if len(word_and_all_defis) != 2:
                errors.append("line does not have exactly one tab: " + line)
                continue
            word = word_and_all_defis[0].strip()
            all_defis = word_and_all_defis[1].strip()
            if word == '':
                errors.append("word is empty: " + line)
                continue
            if all_defis == '':
                errors.append("definition is empty: " + line)
                continue
            if not word.isupper():
                errors.append("word is not uppercase: " + line)
                continue

            valid_words.add(word)
            word_def_lines.append((word, all_defis))
            word_def_dict[word] = all_defis

    parsed_definitions = []

    for word, all_defis in word_def_lines:
        all_defis_split = all_defis.split(' / ')
        for defi in all_defis_split:
            try:
                root_word, loo, defi, alt_spellings, part_of_speech, conjugations = parse_definition(defi, valid_words, word, existing_words_info)
                parsed_definitions.append([root_word, loo, defi, alt_spellings, part_of_speech, conjugations, word])
            except ValueError as e:
                errors.append(str(e))
                continue

    if errors:
        return None, None, None, None, errors

    parsed_tsv = {}
    root_def_to_entry = {}
    num_word_pos = {}
    adj_list = {}
    for root_word, loo, def_text, alt_spellings, pos, conjugations, word in parsed_definitions:
        conjugations_exp = None
        if conjugations:
            conjugations_exp = set()
            total_conjs = 0
            for tenses in conjugations:
                for tense in tenses:
                    conjugations_exp.add(tense.replace('-', word))
                    total_conjs += 1
            if len(conjugations) == 3 and total_conjs == 3:
                wl = len(word)
                abrev_conjs = set()
                for tense in conjugations:
                    if len(tense[0]) <= wl or tense[0][:wl] != word:
                        break
                    abrev_conjs.add(tense[0][wl:])
                if abrev_conjs == {'ED', 'ING', 'S'} or abrev_conjs == {'ED', 'ING', 'ES'}:
                    for tense in conjugations:
                        tense[0] = '-' + tense[0][wl:]

        entry = {
            'root': root_word,
            'loo': loo,
            'def': def_text,
            'alts': alt_spellings,
            'pos': pos,
            'conjs': conjugations,
            'conjs_exp': conjugations_exp,
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
            if root_def_key not in root_def_to_entry and word not in ROOT_WORD_EXCEPTIONS:
                errors.append("Root word definition not found: " + word)
                continue
            if word not in ROOT_WORD_EXCEPTIONS:
                root_entry = root_def_to_entry[root_def_key]
                if word != root_word and (root_entry['conjs_exp'] is None or word not in root_entry['conjs_exp']):
                    errors.append(f"{root_word} has missing conjugation(s): {word}")
                    continue

    if errors:
        return None, None, None, None, errors

    # Make the graph undirected and remove dead end neighbors
    for node_key, node_val in adj_list.items():
        for neighbor in list(node_val['neighbors']):
            if neighbor not in adj_list:
                node_val['neighbors'].remove(neighbor)
            else:
                adj_list[neighbor]['neighbors'].add(node_key)

    return parsed_tsv, adj_list, reserved_nodes, word_def_dict, []

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
        loo = node_val.get('loo')
        if loo and loo not in SPECIAL_LOOS:
            current_group['loos'].append(loo)
    for neighbor in node_val['neighbors']:
        dfs(adj_list, neighbor, current_group)

def validate(input_lexicon, existing_lexicon):
    parsed_tsv, adj_list, start_reserved_nodes, word_def_dict, errors = parse_tsv(input_lexicon, existing_lexicon)

    if errors:
        print("\n".join(errors))
        exit(1)

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
        current_group = {'defs': [], 'words': [], 'loos': []}
        dfs(adj_list, node_key, current_group)
        if len(current_group['words']) == 0:
            continue
        def_counts = {}
        for root_def in current_group['defs']:
            if root_def not in def_counts:
                def_counts[root_def] = 0
            def_counts[root_def] += len(root_def)
        loo_counts = {}
        for loo in current_group['loos']:
            if loo not in loo_counts:
                loo_counts[loo] = 0
            loo_counts += 1
        plurality_def = max(def_counts, key=def_counts.get)
        plurality_loo = None
        if len(loo_counts) > 0:
            plurality_loo = max(loo_counts, key=loo_counts.get)
        sorted_alt_spellings = sorted(current_group['words'])
        _, pos = decompose_key(node_key)
        for salt in sorted_alt_spellings:
            completed_groups[create_key(salt, pos)] = {
                'pdef': plurality_def,
                'ploo': plurality_loo,
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
                plurality_loo = completed_groups[adj_list_key]['ploo']
                entry['alts'] = [x for x in completed_alts if x != root]
                entry['def'] = plurality_def
                if plurality_loo and entry['loo'] not in SPECIAL_LOOS:
                    entry['loo'] = plurality_loo

    return parsed_tsv, reserved_words, word_def_dict

def create_sheet(parsed_tsv, reserved_words, word_def_dict):
    output_file = "out.tsv"
    new_defs_log = "New Definitions:\n"
    total = 0
    autosuggestions = []
    with open(output_file, 'w', newline='', encoding='utf-8') as tsv_out:
        writer = csv.writer(tsv_out, delimiter='\t')

        for word, entries in parsed_tsv.items():
            definitions = []
            tags = ""
            for entry in entries:
                definition_str = ""

                if entry['root'] and entry['root'] != word:
                    definition_str += f"{entry['root']}, "

                if entry['loo']:
                    definition_str += f"({entry['loo']}) "

                definition_str += entry['def']

                if entry['alts']:
                    definition_str += f", also {', '.join(entry['alts'])}"

                pos_str = f"[{entry['pos']}"
                if entry['conjs']:
                    tense_strs = []
                    for tense_conjs in entry['conjs']:
                        tense_str = " or ".join(tense_conjs)
                        tense_strs.append(tense_str)
                    pos_str += f" {', '.join(tense_strs)}"
                pos_str += "]"
                definition_str += " " + pos_str

                definitions.append(definition_str)

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
                autosuggestions.append([word, old_def, new_def])
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
    with open("autosuggestions.tsv", "w", newline='', encoding='utf-8') as autosugg_out:
        writer = csv.writer(autosugg_out, delimiter='\t')
        writer.writerows(autosuggestions)

def retrieve_latest_edition():
    response = requests.get(TSV_URL)
    response.raise_for_status()  # Ensure we downloaded successfully
    
    tsv_content = response.text
    reader = csv.reader(StringIO(tsv_content), delimiter='\t')
    
    with open(RETRIEVED_FILENAME, "w") as outfile:
        # Skip the header row
        # Skip the first two rows
        next(reader, None)  # Skip the first row
        next(reader, None)  # Skip the second row

        for row in reader:
            if len(row) < 6:
                raise ValueError("Row does not have enough columns: " + str(row))
            
            word = row[0].strip()
            existing_def = row[1].strip()
            autosuggested_def = row[2].strip()
            new_def = row[4].strip()
            completed = row[5].strip().lower() in ("true", "1", "yes", "x")
            
            if completed:
                definition = new_def or autosuggested_def or existing_def
            else:
                definition = existing_def
            
            # Write manually to the file with tabs between values
            outfile.write(f"{word}\t{definition}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse a TSV file of words and definitions.")
    parser.add_argument("--file", nargs="?", default=None, help="Specify the TSV file to process.")
    parser.add_argument("--exist", nargs="?", default=None, help="Specify the existing word definitions file.")
    parser.add_argument("--create", action="store_true", help="Creates a new TSV file from the input definitions for crowdsourcing on Google Sheets.")
    args = parser.parse_args()
    
    filename = args.file if args.file else RETRIEVED_FILENAME
    
    if args.file is None:
        retrieve_latest_edition()
    
    parsed_tsv, reserved_words, word_def_dict = validate(filename, args.exist)

    if args.create:
        create_sheet(parsed_tsv, reserved_words, word_def_dict)