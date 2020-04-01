import json
import time
from datetime import date

#TODO
# - Päivämäärän tarkistaminen, että ei tule tuplia dataan
# - Ajan träkkäys
#   - Komentorivin kuuntelu
# - Datan tallentaminen säännöllisin ajoin
# - Datan jakaminen viikoille
# - 

def timetracker():
    readJson()
    initData()


def initData():
    with open('data/week14.json', 'r') as r_file:
        data = json.load(r_file)
        day =   {   "date" : "",
                    "uni" : 0,
                    "opiskelu" : 0,
                    "tyot" : 0,
                    "muu" : 0
                }
        day["date"] = str(date.today())
        data.append(day)

        print(data)
        r_file.close()
        saveData(data)
        

def saveData(data):
    with open('data/week14.json', 'w') as w_file:
        json.dump(data, w_file)


def readJson():
    weeknumber = getWeek()
    filePath = '/data/week' + str(weeknumber) +'.json'


def getWeek():
    return date.today().isocalendar()[1]


if __name__ == '__main__':
    timetracker()