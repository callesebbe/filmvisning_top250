import requests
import re
import imdb
import progressbar
import time
import pickle

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#open connection to imdbpy.
imdb_access = imdb.IMDb()
#The top 250 movies-URL
top250_url = "http://akas.imdb.com/chart/top"
#Creates the lists of ids and titles of movies 1-250
listOfmovieIds = []
listOfmovieIdsnew = []
listOfmovieTitles = []
listOfmovieRatings = []
listOfmovieCovers = []
listOfmovienew = [0]*251
# following code-snippet Copied from JABBA on Stack overflow. Credd
#Code that with help of requests module fetches top 250 of imdb at this moment.
####################################################################
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
######################################################################
#End of Jabba's code.

# Traverses the list of id's and link them to title, rating and so on
def get_top250Titles():
    global listOfmovieIds
    global listOfmovieIdsnew
    global listOfmovieTitles
    global listOfmovieRatings
    global listOfmovieCovers
    global listOfmovienew

    bar = progressbar.ProgressBar()
    for i in bar(range(len(listOfmovieIdsnew))):
        if listOfmovieIdsnew[i] != listOfmovieIds[i]:
            listOfmovieIds[i] = listOfmovieIdsnew[i]
            movie = get_movie_fromtop(i)
            listOfmovieTitles[i] = movie.get('long imdb title')
            listOfmovieRatings[i] = movie.get('rating')
            listOfmovieCovers[i] = movie.get('cover url')
            listOfmovienew[i] = 1
        time.sleep(0.1)

#Puts all ID's in global listOfmovieIds
def update_lists():
    global listOfmovieIdsnew
    listOfmovieIdsnew = list(get_top250Ids())
    get_top250Titles()

#Fetch info about movie from id
def get_movie_fromtop(index):
    movie = imdb_access.get_movie(listOfmovieIds[index])
    return movie

#Prints the list of movies
def print_list():
    global listOfmovieTitles
    global listOfmovieRatings
    global listOfmovienew
    for i in range(len(listOfmovieTitles)):
        m = bcolors.OKGREEN+"New"+bcolors.ENDC if listOfmovienew[i]==1 else bcolors.OKBLUE+"Old"+bcolors.ENDC
        print str(i+1) + ". " + listOfmovieTitles[i] + " - " + str(listOfmovieRatings[i]) +" - " + m

#Saves all global lists to file
def save_lists_toFile():
    global listOfmovieIds
    global listOfmovieTitles
    global listOfmovieRatings
    global listOfmovieCovers
    f = open( "save.p", "w" )
    pickle.dump( listOfmovieIds, f )
    pickle.dump( listOfmovieTitles, f )
    pickle.dump( listOfmovieRatings, f )
    pickle.dump( listOfmovieCovers, f )
    f.close()

#Fetches all saved content from save.p
def fetch_lists_fromFile():
    global listOfmovieIds
    global listOfmovieTitles
    global listOfmovieRatings
    global listOfmovieCovers
    f = open ("save.p", "r")
    listOfmovieIds = pickle.load(f)
    listOfmovieTitles = pickle.load(f)
    listOfmovieRatings = pickle.load(f)
    listOfmovieCovers = pickle.load(f)
    f.close

#Creates SQL-code for all fetched data
def update_mysql_db_query():
    global listOfmovieIds
    global listOfmovieTitles
    global listOfmovieRatings
    global listOfmovieCovers
    values_str = ""
    for i in range(len(listOfmovieIds)):
        values_str += "('" + str(listOfmovieIds[i]) + "' , '" + listOfmovieTitles[i].replace("'", "''") + "' ,'" + str(listOfmovieRatings[i]) + "' ,'" + listOfmovieCovers[i] + "') ,"
    values_str = values_str[:-1]
    sql_insert_all= "Truncate Table imdb_top250;\n" + "INSERT INTO `imdb_top250`(`id`, `title`, `rating`, `cover_url`) VALUES " + values_str
    text_file = open("Output.txt", "w")
    text_file.write(sql_insert_all.encode('utf-8'))
    text_file.close()

#Main fuction for menu and so forth
def main():
    ##fetch_lists_fromFile()
    menu = {}
    menu['1']="Update from Topp 250."
    menu['2']="Output Titles."
    menu['3']="Save lists to file."
    menu['4']="Fetch lists from file."
    menu['5']="Save MYSQL-query to output.txt."
    menu['6']="Exit"
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
            if len(listOfmovieIds) == 0:
                print bcolors.WARNING+"Nothing gathered."+bcolors.ENDC
            else:
                print_list()
        elif selection == '3':
            save_lists_toFile()
            print "####Saved all lists to file.####"
        elif selection == '4':
            fetch_lists_fromFile()
            print "####Fetched all lists from file.####"
        elif selection == '5':
            if len(listOfmovieIds) == 0:
                print bcolors.WARNING+"Nothing gathered."+bcolors.ENDC
            else:
                update_mysql_db_query()
            print "####Saved query to file output.txt.####\nThe sql only includes Title, ID & Movie-photo"
        elif selection == '6':
            ##save_lists_toFile()
            break
        else:
            print "Unknown Option Selected!"

if __name__ == "__main__":
    main()
