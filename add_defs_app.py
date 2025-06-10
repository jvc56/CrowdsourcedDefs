import sqlite3
import csv
import tkinter as tk
from tkinter import filedialog, messagebox

def update_definitions(tsv_file, db_file, output_text):
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
            output_text.insert(tk.END, "Error: The following words in the TSV file are not in the SQLite 'words' table:\n")
            for word in missing_words:
                output_text.insert(tk.END, f"{word}\n")
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
            output_text.insert(tk.END, "Error: The following words were not updated with new definitions:\n")
            for word in db_word_keys:
                output_text.insert(tk.END, f"{word}\n")
            conn.rollback()
            return

        # Commit the changes
        conn.commit()
        output_text.insert(tk.END, "Update successful. All words were updated with new definitions. You must restart Zyzzyva for the changes to take effect. You can now close the application.\n")

    except sqlite3.Error as e:
        output_text.insert(tk.END, f"SQLite error: {e}\n")
    except FileNotFoundError:
        output_text.insert(tk.END, "Error: TSV file not found.\n")
    except Exception as e:
        output_text.insert(tk.END, f"Unexpected error: {e}\n")
    finally:
        if 'conn' in locals():
            conn.close()

def browse_tsv_file():
    tsv_path = filedialog.askopenfilename(filetypes=[("TSV Files", "*.tsv")])
    tsv_entry.delete(0, tk.END)
    tsv_entry.insert(0, tsv_path)

def browse_db_file():
    db_path = filedialog.askopenfilename(filetypes=[("SQLite DB Files", "*.db"), ("SQLite Files", "*.sqlite")])
    db_entry.delete(0, tk.END)
    db_entry.insert(0, db_path)

def run_update():
    tsv_file = tsv_entry.get()
    db_file = db_entry.get()
    if not tsv_file or not db_file:
        messagebox.showerror("Error", "Both TSV and database files are required.")
        return
    output_text.delete(1.0, tk.END)  # Clear previous output
    update_definitions(tsv_file, db_file, output_text)

# Set up the GUI
root = tk.Tk()
root.title("Update Definitions")

# TSV file input
tsv_label = tk.Label(root, text="Definitions File:")
tsv_label.grid(row=0, column=0, padx=10, pady=10)
tsv_entry = tk.Entry(root, width=40)
tsv_entry.grid(row=0, column=1, padx=10, pady=10)
tsv_button = tk.Button(root, text="Browse", command=browse_tsv_file)
tsv_button.grid(row=0, column=2, padx=10, pady=10)
tsv_description = tk.Label(root, text="This should be a plain text file that contains each word with its definition delimited by a tab.", fg="gray")
tsv_description.grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="w")

# Database file input
db_label = tk.Label(root, text="Database File:")
db_label.grid(row=2, column=0, padx=10, pady=10)
db_entry = tk.Entry(root, width=40)
db_entry.grid(row=2, column=1, padx=10, pady=10)
db_button = tk.Button(root, text="Browse", command=browse_db_file)
db_button.grid(row=2, column=2, padx=10, pady=10)
db_description = tk.Label(root, text="This is the SQLite database file that contains the words and definitions for Zyzzyva.\nIt should look something like 'CSW24.db' and\ncan usually be found in C:\\Users\\<name>\\.collinszyzzyva\\lexicons for Collins Zyzzyva or C:\\Users\\<name>\\Zyzzyva\\lexicons for NASPA Zyzzyva.\nFor MacOS and Linux users it can be found in ~/.collinszyzzyva/lexicons for Collins Zyzzyva or ~/Zyzzyva/lexicons for NASPA Zyzzyva.", fg="gray")
db_description.grid(row=3, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="w")

# Output text area
output_label = tk.Label(root, text="Output:")
output_label.grid(row=4, column=0, padx=10, pady=10)
output_text = tk.Text(root, height=15, width=60)
output_text.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

# Run button
run_button = tk.Button(root, text="Update Definitions", command=run_update)
run_button.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

root.mainloop()
