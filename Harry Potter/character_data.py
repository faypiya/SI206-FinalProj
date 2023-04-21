import sqlite3
import requests

def call_api(url):

    #pagination
    start_index = 0
    params = {"limit": 25, "skip": start_index}
    response = requests.get(url, params=params)

    return response.json()

def query_function(statement: str):
    conn = sqlite3.connect("harry_potter.db")
    c = conn.cursor()
    result = c.execute(statement).fetchall()
    c.close()
    return result

def filter_to_25(characters: list, table: str):
    ids = [i[0] for i in query_function('SELECT character_id from characters')]
    characters_data = [i for i in characters if i['id'] not in ids][:25]
    return characters_data

def create_table_char():
    conn = sqlite3.connect("harry_potter.db")
    c = conn.cursor()

    # Create a table for storing character data
    c.execute('''CREATE TABLE IF NOT EXISTS characters
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              character_id TEXT,
              name TEXT NOT NULL,
              house TEXT NOT NULL,
              patronus TEXT,
              hogwarts_student INTEGER NOT NULL,
              alive INTEGER NOT NULL)''')              
    conn.commit()
    c.close()

def insert_character(characters: list):
    conn = sqlite3.connect("harry_potter.db")
    c = conn.cursor()
    for character in characters:
        character_id = character.get("id")
        name = character.get("name")
        house = character.get("house")
        patronus = character.get("patronus", "unknown")
        hogwarts_student = 1 if character.get("hogwartsStudent") else 0
        alive = 1 if character.get("alive") else 0

        #check if the character is already in the database based on their name
        c.execute("SELECT * FROM characters WHERE name=?", (name,))
        existing_character = c.fetchone()
        if existing_character:
            continue
        c.execute("INSERT OR REPLACE INTO characters (character_id, name, house, patronus, hogwarts_student, alive) VALUES (?, ?, ?, ?, ?, ?)",
                    (character_id, name, house, patronus, hogwarts_student, alive))   
    conn.commit()
    c.close()

def main():

    data = call_api(url="https://hp-api.onrender.com/api/characters")
    create_table_char()
    filtered_data = filter_to_25(data, 'characters')
    if not filtered_data:
        return "No more data to insert"
    insert_character(filtered_data)


if __name__ == "__main__":
    main()








