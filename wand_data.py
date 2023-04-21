import sqlite3
import requests

def call_api(url):

    # Initialize the start index for pagination
    start_index = 0

    # Set the limit and start parameters for pagination
    params = {"limit": 25, "skip": start_index}

    # Send a GET request to the API endpoint
    response = requests.get(url, params=params)

    return response.json()

def query_function(statement: str):
    # Create a connection to the database
    conn = sqlite3.connect("harry_potter.db")

    # Create a cursor object
    c = conn.cursor()
    result = c.execute(statement).fetchall()
    c.close()
    return result

def filter_to_25(characters: list, table: str):
    ids = [i[0] for i in query_function(f'SELECT id from {table}')]
    characters_data = [i for i in characters if i['id'] not in ids][:25]
    return characters_data

def create_table_wand():
    conn = sqlite3.connect("harry_potter.db")
    c = conn.cursor()
    # Create a table for storing wand data
    c.execute('''CREATE TABLE IF NOT EXISTS wands
             (id INTEGER PRIMARY KEY,
              character_id TEXT,
              wood TEXT,
              core TEXT,
              length INTEGER)''')        
    conn.commit()
    c.close()


def insert_wands(characters: list):
    conn = sqlite3.connect("harry_potter.db")
    c = conn.cursor()
    
    for character in characters:
        # Extract the and wand information
        wand = character.get("wand")
        if not wand:
            continue
        character_id = character.get("id")
        wood = wand.get("wood", "unknown")
        core = wand.get("core", "unknown")
        length = wand.get("length", "unknown")

        # Check if the character is already in the database based on their id
        c.execute("SELECT * FROM wands WHERE character_id=?", (character_id,))
        existing_character = c.fetchone()


        # If the character is not in the characters table, skip inserting their wand information
        if existing_character:
            continue

        # Insert the wand information into the wands table
        c.execute("INSERT INTO wands (character_id, wood, core, length) VALUES (?, ?, ?, ?)",
                    (character_id, wood, core, length))
        
    conn.commit()
    c.close()


def main():
    data = call_api(url="https://hp-api.onrender.com/api/characters/students")
    create_table_wand()
    filtered_data = filter_to_25(data, "characters")
    if not filtered_data:
        return "No more data to insert"
    insert_wands(filtered_data)

if __name__ == "__main__":
    main()