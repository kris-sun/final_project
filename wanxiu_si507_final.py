#################################
##### Name:wanxiu sun
##### Uniqname:wanxiu
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets 
from requests_oauthlib import OAuth1
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import random as random
random.seed(33)
from matplotlib.path import Path
import sqlite3
import plotly.graph_objs as  go
import re
import PIL.Image
import PIL.ImageDraw

#import plotly.graph_objects as goob
from flask import Flask
print("Welcome to POEMON GO!")

a=input("input the pokemon you want to search!\n")

pattern="[A-Z]"

conn1 = sqlite3.connect("ShinnyPokemon.sqlite")
cur1 = conn1.cursor()

drop_tables = '''
    DROP TABLE IF EXISTS "ShinnyPokemon";
'''

create_tables = '''
        CREATE TABLE IF NOT EXISTS "ShinnyPokemon"(
            "Id" INTERGER PRIMARY KEY UNIQUE,
            "Name" TEXT NOT NULL,
            "Found_egg" BOOLEAN NOT NULL,
            "Found_evolution" BOOLEAN NOT NULL,
            "Found_raid" BOOLEAN NOT NULL,
            "Found_research" BOOLEANR NOT NULL,
            "Found_wild" BOOLEAN NOT NULL


        );
'''

conn2 = sqlite3.connect("PokemonInfo.sqlite")
cur2 = conn2.cursor()

drop_table2 = '''
    DROP TABLE IF EXISTS "PokemonInfo";
'''

create_table2 = '''
        CREATE TABLE IF NOT EXISTS "PokemonInfo"(
            "Id" INTERGER PRIMARY KEY UNIQUE,
            "Name" TEXT NOT NULL,
            "Type" INTERGER NOT NULL,
            "Weight" INTERGER NOT NULL,
            "Height" INTERGER NOT NULL,
            "HP" INTERGER NOT NULL,
            "Attack" INTERGER NOT NULL,
            "Defense" INTERGER NOT NULL


        );
'''


CACHE_FILENAME = "final_cache.json"

def open_cache():
    ''' opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    Parameters
    ----------
    None
    Returns
    -------
    The opened cache
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' saves the current state of the cache to disk
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 

class Pokemon:
    '''a pokemon info

    Instance Attributes
    -------------------
    name: string
       the name of a pokemon
    
    national_No: int
        the No.of a pokemon

    pokemon_type: string
        the type of a pokemon

    weight: string
        the weight of a pokemon

    height: string
         the height of a pokemon

    HP: int
        the HP number of a pokemon
    
    attack: int
        the attack number of a pokemon

    defense: int
        the defense number of a pokemon
    '''
    def __init__(self,name,national_No,pokemon_type,weight,height,HP,attack,defenes):
        self.name = name
        self.national_No = national_No
        self.pokemon_type = pokemon_type
        self.weight = weight
        self.height = height
        self.HP = HP
        self.attack = attack
        self.defense = defenes
    
    def info(self):
        return self.name + " [ No. :" + self.national_No + "; Type : " \
                         + self.pokemon_type + "; Weight :  " + self.weight\
                         + "; Height : " + self.height + "; HP :" + self.HP\
                         + "; attack: " + self.attack + "; defense: " +self.defense + "]"

def get_pokemon_instance(pokemon_url):
    '''Make an instances from a pokemon URL.
    
    Parameters
    ----------
    pokemon_url: string
        The URL for a  sigle pokemon
    
    Returns
    -------
    instance
        a pokemon instance
    '''
    pokemon_type = ""
    BASE_URL = pokemon_url
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text,'html.parser')

    test = soup.find('div',class_ = "tabset-basics sv-tabs-wrapper sv-tabs-onetab")
    if test == None:
        test = soup.find('div',class_ = "tabset-basics sv-tabs-wrapper")

    info1 = test.find('div',class_ = "grid-col span-md-6 span-lg-4").find_all('tr') 
    info2 = test.find('div',class_ = "resp-scroll").find_all('tr')
    name = soup.find('main', id = "main",class_ = "main-content grid-container").find('h1').string.strip()
    for i in info1:
        if i.find('th').string == "National №":
            national_No =  i.find('td').string.strip()
        if i.find('th').string == "Type":
            for  x in i.find('td'):
                pokemon_type = pokemon_type + x.string.strip()
        if i.find('th').string == "Weight":
            weight = i.find('td').string.strip()
        if i.find('th').string == "Height":
            height = i.find('td').string.strip()
    for i in info2:
        if i.find('th').string == "HP":
            HP = i.find('td').string.strip()
        if i.find('th').string == "Attack":
            attack = i.find('td').string.strip()     
        if i.find('th').string == "Defense":
            defense = i.find('td').string.strip()          

    return Pokemon(name,national_No,pokemon_type,weight,height,HP,attack,defense)

def get_pokemon_instance_by_cache(pokemon_url):
    if pokemon_url in CACHE_DICT:
        print("cache")
        return Pokemon(CACHE_DICT[pokemon_url]["name"],
                        CACHE_DICT[pokemon_url]["national_No"],
                        CACHE_DICT[pokemon_url]["pokemon_type"],
                        CACHE_DICT[pokemon_url]["weight"],
                        CACHE_DICT[pokemon_url]["height"],
                        CACHE_DICT[pokemon_url]["HP"],
                        CACHE_DICT[pokemon_url]["attack"],
                        CACHE_DICT[pokemon_url]["defense"])
    else:
        print("fetching")
        temp = get_pokemon_instance(pokemon_url)
        CACHE_DICT[pokemon_url] = temp.__dict__
        save_cache(CACHE_DICT)
        return Pokemon(CACHE_DICT[pokemon_url]["name"],
                        CACHE_DICT[pokemon_url]["national_No"],
                        CACHE_DICT[pokemon_url]["pokemon_type"],
                        CACHE_DICT[pokemon_url]["weight"],
                        CACHE_DICT[pokemon_url]["height"],
                        CACHE_DICT[pokemon_url]["HP"],
                        CACHE_DICT[pokemon_url]["attack"],
                        CACHE_DICT[pokemon_url]["defense"])

def get_info_for_pokemon(pokemon_name,poke_dict):
    '''Make a list of pokemon instances from a pokemon URL.
    
    Parameters
    ----------
    pokemon_url: string
        The URL for a pokemon 
    
    Returns
    -------
    list
        a list of pokemon instances
    '''
    l=[]
    if pokemon_name in poke_dict:
        BASE_URL = poke_dict[pokemon_name]
    inst = get_pokemon_instance(BASE_URL)
    return l.append(inst)

def get_api(BASE_URL_API):
    #BASE_URL = "https://pokemon-go1.p.rapidapi.com/shiny_pokemon.json"

    headers = {
    'x-rapidapi-key': secrets.API_KEY,
    'x-rapidapi-host': secrets.API_HOST
    }

    response = requests.request("GET", BASE_URL_API, headers=headers)
    alldata = response.json()
    return  alldata

def get_api_by_cache(BASE_URL_API):
    if BASE_URL_API in CACHE_DICT:
        print("use cache")
        return CACHE_DICT[BASE_URL_API]
    else:
        print("fetching")
        CACHE_DICT[BASE_URL_API] = get_api(BASE_URL_API)
        save_cache(CACHE_DICT)
        return CACHE_DICT[BASE_URL_API]

def get_pokemon_url_dict(BASE_URL_POKEDEX):
    dic = {}
    URL = "https://pokemondb.net"
    response = requests.get(BASE_URL_POKEDEX)
    soup = BeautifulSoup(response.text,'html.parser')
    TEST = "data-table block-wide"
    pokedex = soup.find_all('td',class_="cell-name")
    for pokemon in pokedex:
        pokemon_path =pokemon.find('a')["href"]
        pokey = pokemon.string
        dic[pokey] = URL + pokemon_path
    del dic[None]
    return dic

def get_pokemon_url_dict_by_cache(BASE_URL_POKEDEX):
    if BASE_URL_POKEDEX in CACHE_DICT:
        print("cache")
        return CACHE_DICT[BASE_URL_POKEDEX]
    else:
        print("fetching")
        CACHE_DICT[BASE_URL_POKEDEX] = get_pokemon_url_dict(BASE_URL_POKEDEX)
        save_cache(CACHE_DICT)
        return CACHE_DICT[BASE_URL_POKEDEX]

def get_list_of_all_pokemon_instance(pokedic):
    pokemon_object_list = []
    for val in pokedic.values():
        BASE_URL = val
        pokemon_object = get_pokemon_instance_by_cache(BASE_URL)
        pokemon_object_list.append(pokemon_object)
    return pokemon_object_list

def change_the_type_style(old_string):
    new_string=re.sub(pattern,lambda x:" "+x.group(0),old_string)
    new_split_string = new_string.split()
    return new_split_string

def if_the_pokemon_shinny(a):
    #a = input("Input the Pokemon you wanna search\n") 
    connection = sqlite3.connect("ShinnyPokemon.sqlite")
    cursor = connection.cursor()
    query = "SELECT ShinnyPokemon.Found_egg FROM ShinnyPokemon\
        JOIN PokemonInfo ON ShinnyPokemon.Id = PokemonInfo.Id\
        WHERE PokemonInfo.Name = '"+a+"'" 
    result_1 = cursor.execute(query).fetchall()
    query = "SELECT ShinnyPokemon.Found_evolution FROM ShinnyPokemon\
        JOIN PokemonInfo ON ShinnyPokemon.Id = PokemonInfo.Id\
        WHERE PokemonInfo.Name = '"+a+"'" 
    result_2 = cursor.execute(query).fetchall()
    query = "SELECT ShinnyPokemon.Found_raid FROM ShinnyPokemon\
        JOIN PokemonInfo ON ShinnyPokemon.Id = PokemonInfo.Id\
        WHERE PokemonInfo.Name = '"+a+"'" 
    result_3 = cursor.execute(query).fetchall()
    query = "SELECT ShinnyPokemon.Found_research FROM ShinnyPokemon\
        JOIN PokemonInfo ON ShinnyPokemon.Id = PokemonInfo.Id\
        WHERE PokemonInfo.Name = '"+a+"'" 
    result_4 = cursor.execute(query).fetchall()
    query = "SELECT ShinnyPokemon.Found_wild FROM ShinnyPokemon\
        JOIN PokemonInfo ON ShinnyPokemon.Id = PokemonInfo.Id\
        WHERE PokemonInfo.Name = '"+a+"'" 
    result_5 = cursor.execute(query).fetchall()
    connection.close()
    result = ["Found in Egg?\t \t"+str(result_1[0][0]) +"          1 means yes! 0 means no! \n\n",
            "Found in Evolution?\t \t"+str(result_2[0][0]) +"      1 means yes! 0 means no! \n\n",
            "Found in Raid?\t \t"+str(result_3[0][0]) +"           1 means yes! 0 means no! \n\n",
            "Found in Research?\t \t"+str(result_4[0][0]) +"       1 means yes! 0 means no! \n\n",
            "Found in Wild?\t \t"+str(result_5[0][0]) +"           1 means yes! 0 means no! \n\n"]
    return result

def show_bar_plot(pokemon_object_list):
    xvals = ["Normal","Fighting","Flying","Poison","Ground",
             "Rock","Bug","Ghost","Steel","Fire",
             "Water","Grass","Electric","Psychic","Ice",
             "Dragon","Dark","Fairy"]
    yvals = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    for obj in pokemon_object_list:
        new_string_list = change_the_type_style(obj.pokemon_type)
        for i in new_string_list:
            if i == "Normal":
                yvals[0] = yvals[0]+1
            if i == "Fighting":
                yvals[1] = yvals[1]+1           
            if i == "Flying":
                yvals[2] = yvals[2]+1
            if i == "Poison":
                yvals[3] = yvals[3]+1
            if i == "Ground":
                yvals[4] = yvals[4]+1
            if i == "Rock":
                yvals[5] = yvals[5]+1
            if i == "Bug":
                yvals[6] = yvals[6]+1
            if i == "Ghost":
                yvals[7] = yvals[7]+1
            if i == "Steel":
                yvals[8] = yvals[8]+1
            if i == "Fire":
                yvals[9] = yvals[9]+1
            if i == "Water":
                yvals[10] = yvals[10]+1
            if i == "Grass":
                yvals[11] = yvals[11]+1
            if i == "Electric":
                yvals[12] = yvals[12]+1
            if i == "Psychic":
                yvals[13] = yvals[13]+1
            if i == "Ice":
                yvals[14] = yvals[14]+1
            if i == "Dragon":
                yvals[15] = yvals[15]+1  
            if i =="Dark":
                yvals[16] = yvals[16]+1
            if i == "Fairy":
                yvals[17] = yvals[17]+1  
    bar_data = go.Bar(x=xvals,y=yvals)
    basic_layout = go.Layout(title="Type Bar Graph")
    fig = go.Figure(data = bar_data,layout = basic_layout)   
    fig.show()

def show_scatter_plot(pokemon_dict,pokemon):
    xvals = ["HP","Attack","Defense"]
    #pokemon = input("Which Pokemon you want to search: (e.g. Bulbasaur)\n")
    if pokemon in  pokemon_dict:
        pokemon_url = pokemon_dict[pokemon]
        obj_pokemon = get_pokemon_instance_by_cache(pokemon_url)
        hp = int(obj_pokemon.HP)
        attack = int(obj_pokemon.attack)
        defense = int(obj_pokemon.defense)
    yvals = [hp,attack,defense]
    scatter_data = go.Scatter(x = xvals,y=yvals)
    basic_layout = go.Layout(title = pokemon)
    fig = go.Figure(data = scatter_data,layout = basic_layout)
    fig.write_html(pokemon+".html",auto_open = True)

def show_triangle_plot(pokemon_dict,pokemon):
    if pokemon in  pokemon_dict:
        pokemon_url = pokemon_dict[pokemon]
        obj_pokemon = get_pokemon_instance_by_cache(pokemon_url)
        hp = int(obj_pokemon.HP)
        attack = int(obj_pokemon.attack)
        defense = int(obj_pokemon.defense)
        a=PIL.Image.new('RGB',(200,200))
        m=PIL.ImageDraw.Draw(a)
        m.polygon([(100,hp),(attack,150),(defense,defense)],fill=0xff0000)
        #m.text((100,50), obj_pokemon.HP)
        m.text((defense+10,defense+10), obj_pokemon.defense )
        m.text((defense,defense), u'defense')
        m.text((100,hp), u'hp')
        m.text((100,hp+10),  obj_pokemon.HP )
        m.text((attack,150), u'attack')
        m.text((attack,140),  obj_pokemon.attack )
        m.text((130,90), obj_pokemon.name)
        a.show()

app = Flask(__name__)

@app.route('/')
def index():
    result = if_the_pokemon_shinny(a) 
    web = '<h1>'+result[0]+'</h1>'\
          '<h1>'+result[1]+'</h1>'\
          '<h1>'+result[2]+'</h1>'\
          '<h1>'+result[3]+'</h1>'\
          '<h1>'+result[4]+'</h1>'
    return web

def print_menue():
    print("Welcome to POKEMON GO!!!!!!")
    print("===========================")
    print("1. show the number of different types of pokemon")
    print("2. Chose one of pokemon as your buddy!")
    print("3. Does your buddy strong enough?")
    print("4. Search where can find the target Pokemon?")


if __name__ == "__main__":
    CACHE_DICT = open_cache()
    #print('start flask',app.name)
    #app.run(debug=True)
    BASE_URL_API = "https://pokemon-go1.p.rapidapi.com/shiny_pokemon.json"
    BASE_URL_POKEDEX =  "https://pokemondb.net/pokedex/all"

    api = get_api_by_cache(BASE_URL_API)

    cur1.execute(drop_tables)
    cur1.execute(create_tables)
    conn1.commit()
    cur1.execute(drop_table2)
    cur1.execute(create_table2)
    conn1.commit()

    cur2.execute(drop_table2)
    cur2.execute(create_table2)
    conn2.commit()

    insert_api_table = '''
        INSERT INTO ShinnyPokemon
        VALUES (?,?,?,?,?,?,?)
    '''
    for val in api.values():
        add_api_to_db = [val["id"],val["name"],val["found_egg"],val["found_evolution"],
                         val["found_raid"],val["found_research"],val["found_wild"]]
        cur1.execute(insert_api_table,add_api_to_db)
        conn1.commit()  


    POKEMON_DICT = get_pokemon_url_dict_by_cache(BASE_URL_POKEDEX)
    
    POKEMON_LIST = get_list_of_all_pokemon_instance(POKEMON_DICT)
    #print(POKEMON_DICT)

    insert_pokemonInfo_table = '''
        INSERT INTO PokemonInfo
        VALUES (?,?,?,?,?,?,?,?)
    '''
    for i in POKEMON_LIST:
        add_instance_to_db = [i.national_No,i.name,i.pokemon_type,i.weight,i.height,i.HP,i.attack,i.defense]
        cur2.execute(insert_pokemonInfo_table,add_instance_to_db)
        conn2.commit()
        cur1.execute(insert_pokemonInfo_table,add_instance_to_db)
        conn1.commit()
    
    while True:
        #print('start flask',app.name)
        #app.run(debug=True)
        print_menue()
        your_choice = input("which option you want to choose:\n")
        if your_choice == "1":
            show_bar_plot(POKEMON_LIST)
        if your_choice == "2":
            pokemon = input("Who am I?\n")
            if pokemon not in POKEMON_DICT:
                print("WRONG INPUT!")
            else:
                show_scatter_plot(POKEMON_DICT,pokemon)
        if your_choice == "3":
            pokemon = input("Who am I?\n")
            if pokemon not in POKEMON_DICT:
                print("WRONG INPUT!")
            else:
                show_triangle_plot(POKEMON_DICT,pokemon)
        if your_choice == "4":
            print('start flask',app.name)
            app.run(debug=True)
        if your_choice =="exit":
            break

    save_cache(CACHE_DICT)




        