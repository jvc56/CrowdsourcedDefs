import sqlite3
import csv
import argparse

def update_definitions(tsv_file, db_file):
    try:
        # Read TSV file
        with open(tsv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            tsv_data = {row[0].upper(): row[1] for row in reader}

        # Connect to SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Retrieve all words from the 'words' table
        cursor.execute("SELECT word, definition FROM words")
        db_words = {row[0]: row[1] for row in cursor.fetchall()}

        # Check if all TSV words exist in the SQLite 'words' table
        tsv_words = set(tsv_data.keys())
        db_word_keys = set(db_words.keys())
        missing_words = tsv_words - db_word_keys
        if missing_words:
            print("Error: The following words in the TSV file are not in the SQLite 'words' table:")
            for word in missing_words:
                print(f"{word}")
            return

        # Prepare to track updated words
        updated_words = set()

        # Update definitions in the SQLite database
        for word, new_definition in tsv_data.items():
            db_word_keys.remove(word)
            cursor.execute("""
                UPDATE words
                SET definition = ?
                WHERE word = ?
            """, (new_definition, word))

        if db_word_keys:
            print("Error: The following words were not updated with new definitions:")
            for word in db_word_keys:
                print(f"{word}")
            conn.rollback()
            return

        # Commit the changes
        conn.commit()
        print("Update successful. All words were updated with new definitions.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except FileNotFoundError:
        print("Error: TSV file not found.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update definitions in a SQLite database using a TSV file.")
    parser.add_argument("defs", help="Path to the TSV file containing word-definition pairs.")
    parser.add_argument("db", help="Path to the SQLite database file.")
    args = parser.parse_args()

    update_definitions(args.defs, args.db)
