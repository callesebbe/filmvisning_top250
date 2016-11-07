import requests
import re
import imdb
import progressbar
import time

imdb_access = imdb.IMDb()
top250_url = "http://akas.imdb.com/chart/top"
#Creates the lists of ids and titles of movies 1-250
listOfmovieIds = []
listOfmovieTitles = []

#Copied from JABBA on Stack overflow. Credd
def get_top250Ids():
    r = requests.get(top250_url)
    html = r.text.split("\n")
    result = []
    for line in html:
        line = line.rstrip("\n")
        m = re.search(r'data-titleid="tt(\d+?)">', line)
        if m:
            _id = m.group(1)
            result.append(_id)
    return result

def get_top250Titles():
    global listOfmovieIds
    global listOfmovieTitles
    bar = progressbar.ProgressBar()
    for i in bar(range(0,10)):
        listOfmovieTitles.append(get_movie_fromtop(i))
        #bar.update(i+1)
        time.sleep(0.1)
    #bar.finish()
def update_lists():
    global listOfmovieIds
    global listOfmovieTitles
    listOfmovieIds = list(get_top250Ids())
    get_top250Titles()

def get_movie_fromtop(index):
    movie = imdb_access.get_movie(listOfmovieIds[index])
    title = movie.get('long imdb title')
    rating = movie.get('rating')
    result = str(title) + ' - rating: ' + str(rating)
    return result

def print_list(_list):
    for i in range(len(_list)):
        print _list[i]

def main():
    menu = {}
    menu['1']="Update from Topp 250."
    menu['2']="Output Titles to index."
    menu['3']="nothing"
    menu['4']="Exit"
    while True:
        options=menu.keys()
        options.sort()
        print("################################################################ \
        \nWelcome to update-script for fetching data from IMDb's top 250! \
        \n################################################################  ")
        for entry in options:
            print entry, menu[entry]
        selection = raw_input("Please Select:")
        if selection =='1':
            update_lists()
        elif selection == '2':
            print_list(listOfmovieTitles)
        elif selection == '3':
            print "none"
        elif selection == '4':
            break
        else:
            print "Unknown Option Selected!"
    #update_lists()
    #print_list(listOfmovieTitles)
    #print get_movie_fromtop(1)

if __name__ == "__main__":
    main()
