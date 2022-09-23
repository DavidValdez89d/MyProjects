#Modules
import requests
from bs4 import BeautifulSoup
import re
import functools
import json

#we create a session to reduce calculation time calling the info
s = requests.Session()

#Save information into the document function
def save():
    with open("leaders.json","w") as fp:
        json.dump(leaders_per_country, fp)

#we create a hashable cashe in order to hash our function
cache = {}
def hashable_cache(f):
    def inner(url, session):
        if url not in cache:
            cache[url] = f(url, session)
        return cache[url]
    return inner

#we create a get first paragraph function in order to call it
@hashable_cache
def get_first_paragraph(wikipedia_url,s):
    req = s.get(wikipedia_url)
    soup = BeautifulSoup(req.text,"html.parser")
    for paragraph in soup.find_all('p'):
        if paragraph.find_all('b'):
            first_paragraph = paragraph.text
            subst = ""
            patern = "(\[\w*\s*\d+])"
            first_paragraph = re.sub(patern, subst, first_paragraph)
            return first_paragraph
        
#we create the main fucntion that creates a leaders dictionary wit different keys: id, first_name, last_name, birth_date, death_date, place_of_birth, wikipedia_url, start_mandate, end_mandate, first_paragraph.
def get_leaders():
    print('run get_leaders')
    root_url = "https://country-leaders.herokuapp.com"
    
    cookie_url = root_url + "/cookie"
    cookies = s.get(cookie_url).cookies
    
    countries_url = root_url + "/countries"
    countries = s.get(countries_url, cookies=cookies).json()
    
    leaders_url = root_url + "/leaders"
    leaders_per_country = {}
    for country in countries:
        params = {'country' : country}
        #the cookie time might expire, so we write a piece of code that will make another cookie
        leaders_req = s.get(leaders_url, params=params, cookies=cookies)
        if leaders_req.status_code == 403:  #cookie error
            cookies = s.get(cookie_url).cookies
            leaders_req = s.get(leaders_url, params=params, cookies=cookies)
        #We retrieve the main dictionary
        leaders = leaders_req.json()
        for leader in leaders:
            #we add a key first_paragraph, from wikipedia to the dictionary
            leader['first_paragraph'] = get_first_paragraph(leader['wikipedia_url'],s)
        leaders_per_country[country] = leaders
    save()
    return leaders_per_country


