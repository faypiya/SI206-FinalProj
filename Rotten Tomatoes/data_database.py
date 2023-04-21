from bs4 import BeautifulSoup
import urllib.request, urllib.parse, urllib.error
import requests
import re
import json
import sqlite3
import os

'''GATHER DATA'''

#create BeatifulSoup object
def create_soup(url):
    agent = {"User-Agent":"Mozilla/5.0"}
    req = requests.get(url, headers=agent)
    soup = BeautifulSoup(req.text, "html.parser")
    return soup

#get movie titles of the movies from the 'Best Movies at Home' page
def get_movie_titles(url):
    soup = create_soup(url)
    
    movie_titles_list = []

    movie_titles = soup.find_all("span", {"data-qa": "discovery-media-list-item-title"})
    
    for movie in movie_titles:
        movie_titles_list.append(movie.text.strip())

    return movie_titles_list

#get tomatometer percentages of the movies from the 'Best Movies at Home' page
def get_tomatometers(url):
    soup = create_soup(url)

    tomatometers_list = []

    tomatometers = soup.find_all("score-pairs")

    for percentage in tomatometers:
        try:
            tomatometers_list.append(int(percentage.get("criticsscore")))
        except:
            tomatometers_list.append("None")

    return tomatometers_list

#get the movies' genres from their respective individual information pages
def get_genres(url):
    soup = create_soup(url)

    movie_genres_list = []

    movie_href = soup.select("a.js-tile-link, a[data-qa='discovery-media-list-item-caption']")
    movie_urls_list = []

    for href in movie_href:
        movie_url = "https://www.rottentomatoes.com" + href.get("href")
        movie_urls_list.append(movie_url)
    
    for m_url in movie_urls_list:
        movie_req = requests.get(m_url)
        movie_soup = BeautifulSoup(movie_req.text, "html.parser")

        reg_exp = "Genre:\s*([a-zA-z,\s\n-]+)[^(?:Original Laguage)]"
        x = re.findall(reg_exp, str(movie_soup.text))

        if len(x) == 0:
            movie_genres_list.append("None")
        else:
            for i in x:
                istr = i.strip().replace("\n", "")
                istr = re.sub('\s{2,}', ' ', istr)
                movie_genres_list.append(istr)

    return movie_genres_list

#get the data_ems_id of the movies from the 'Best Movies at Home' page
def get_data_ems_ids(url):
    soup = create_soup(url)

    data_ems_id_list = []

    data_ems_id_select = soup.select("div[data-qa='discovery-media-list-item'], a[data-qa='discovery-media-list-item']")

    for s in data_ems_id_select:
        data_ems_id = s.get("data-ems-id")
        data_ems_id_list.append(data_ems_id)

    return data_ems_id_list

#make a json file of the movies from the 'Best Movies at Home'
def best_movies_json(json_name):
    for num in range(5):
        url = "https://www.rottentomatoes.com/browse/movies_at_home/sort:popular?page=" + str(num) 

        movie_titles_list = []
        tomatometers_list = []
        movie_genres_list = []
        data_ems_id_list = []

        movie_titles_list += get_movie_titles(url)
        tomatometers_list += get_tomatometers(url)
        movie_genres_list += get_genres(url)
        data_ems_id_list += get_data_ems_ids(url)


    movie_info = []

    for i in range(len(movie_titles_list)):
        movie_dict = {}

        movie_dict['title'] = movie_titles_list[i]
        movie_dict['tomatometer'] = tomatometers_list[i]
        movie_dict['genres'] = movie_genres_list[i]
        movie_dict['data_ems_id'] = data_ems_id_list[i]
 
        movie_info.append(movie_dict)

    f = open(json_name, 'w')

    json.dump(movie_info, f, indent=4)

    f.close()

#make a json file of the movies from the 'Best Movies at Home' that are Certified Fresh
def best_movies_fresh(json_name):
    for num in range(5):
        url = "https://www.rottentomatoes.com/browse/movies_at_home/critics:certified_fresh~sort:popular?page=" + str(num) 

        movie_titles_list = []
        data_ems_id_list = []

        movie_titles_list += get_movie_titles(url)
        data_ems_id_list += get_data_ems_ids(url)

    movie_info = []

    for i in range(len(data_ems_id_list)):
        movie_dict = {}

        movie_dict['title'] = movie_titles_list[i]
        movie_dict['data_ems_id'] = data_ems_id_list[i]
 
        movie_info.append(movie_dict)

    f = open(json_name, 'w')

    json.dump(movie_info, f, indent=4)

    f.close()


'''STORE DATA IN DATABASE'''

#create database
def setUpDatabase(database_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+database_name)
    cur = conn.cursor()
    return cur, conn

#create table for 'Best Movies at Home' movies 
def create_best_movies_table(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS best_movies (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, tomatometer INTEGER, genre TEXT, data_ems_id TEXT)")

    conn.commit()

    cur.execute("SELECT id FROM best_movies ORDER BY id DESC LIMIT 25")
    last_ids = [row[0] for row in cur.fetchall()]
    
    f = open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'best_movies.json')))
    file_data = f.read()
    f.close()
    all_data = json.loads(file_data)
    data = [item for item in all_data if item['data_ems_id'] not in last_ids][:25]

    for item in data:
        title = item['title']
        tomatometer = item['tomatometer']
        genre = item['genres']
        data_ems_id = item['data_ems_id']

        cur.execute(
            """
            INSERT OR IGNORE INTO best_movies (title, tomatometer, genre, data_ems_id)
            VALUES (?, ?, ?, ?)
            """,
            (title, tomatometer, genre, data_ems_id)
        )
    conn.commit()

#create table for 'Best Movies at Home' Certified Fresh movies 
def certified_fresh_table(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS certified_fresh (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, best_movie_id INTEGER, FOREIGN KEY(best_movie_id) REFERENCES best_movies(id))")
    conn.commit()

    cur.execute("SELECT id FROM certified_fresh ORDER BY id DESC LIMIT 25")
    last_ids = [row[0] for row in cur.fetchall()]

    f = open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'certified_fresh_movies.json')))
    file_data = f.read()
    f.close()
    all_data = json.loads(file_data)
    data = [item for item in all_data if item['data_ems_id'] not in last_ids][:25]

    for item in data:
        title = item['title']
        data_ems_id = item['data_ems_id']

        cur.execute("SELECT id FROM best_movies WHERE data_ems_id = ?", (data_ems_id,))
        result = cur.fetchone()

        if result is not None:
            best_movie_id = result[0]

            cur.execute(
                """
                INSERT OR IGNORE INTO certified_fresh (title, best_movie_id)
                VALUES (?, ?)
                """,
                (title, best_movie_id)
            )
    conn.commit()


#run the functions to gather the data and store it in the database
def main():
    best_movies_json('best_movies.json')
    best_movies_fresh('certified_fresh_movies.json')

    cur, conn = setUpDatabase('rotten_tomatoes.db')
    create_best_movies_table(cur, conn)
    certified_fresh_table(cur,conn)

#run main
main()

