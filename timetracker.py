import json
import time
import os.path
from datetime import date

#TODO
# - Poikkeavan Inputin hallinta
# - 
# - Json-filen alustus dynaamisesti
# - Työprojektin / koulukurssin yksilöllinen seuranta
# - Datan syöttö ulos
#   - Komentorivi
#   - Harvest

time_types = ["uni", "opiskelu", "tyot", "muu"]
time_types_lyh =  ["un", "op", "ty", "mu"]
time_end_types = ["loppu", "end", "l", "lounas"]
close_types = "exit"
help_type = "help"

data_folder = "data/"
print(os.getcwd())
if os.getcwd() == "/Users/otto":
        data_folder = "coding/timetracker/data/"

def timetracker():
    readTimeType()


def readTimeType():
    time_type = input()
    if close_types == time_type:
        close()
    if help_type == time_type:
        help_info()
    for i in range(0,len(time_types)):
        if time_types[i] == time_type:
            startTime(time_types[i])
        elif time_types_lyh[i] == time_type:
            startTime(time_types[i])
   

def startTime(type_t):
    timeStart = time.time()
    print( "Started " + type_t)
    timePrint(timeStart)
    endTime(timeStart, type_t)


def endTime(timeStart, type_t):
    listen = True
    while listen:
        input_listen = input()
        if input_listen == close_types:
            timeEnd = time.time()
            usedTime = countUsedTime(timeEnd, timeStart)
            saveData(usedTime, type_t)
            listen = False
        if input_listen in time_end_types:
            timeEnd = time.time()
            print()
            print("Start time: ")
            timePrint(timeStart)
            print()
            print("End time: ")
            timePrint(timeEnd)

            print("Used time: ")
            usedTime = countUsedTime(timeEnd, timeStart)

            #Debug
            usedTime = 420

            listen = False
            saveData(usedTime, type_t)
            timetracker()


def saveData(usedTime, type_t):
    weekNum = str(getWeek())
    if os.path.isfile(data_folder+'week'+weekNum+'.json'):
        print('File already exists')
        with open(data_folder+'week'+weekNum+'.json') as file_data:
            data = json.load(file_data)
            data = handleJson(data, usedTime, type_t)
            file_data.close()
            save(data, weekNum)
    else:
        with open(data_folder+'week'+weekNum+'.json', 'w') as file_data:
            print('Creating new file / starting new week')
            data = []
            day =   {   "date" : "",
                        "uni" : 0,
                        "opiskelu" : 0,
                        "tyot" : 0,
                        "muu" : 0
                    }
            day["date"] = str(date.today())
            day[type_t] = usedTime
            data.append(day)
            json.dump(data, file_data)
            file_data.close()


def save(data, weekNum):
    with open(data_folder+'week'+weekNum+'.json', 'w') as file_data:
        json.dump(data, file_data)


def handleJson(data, usedTime, type_t):
    print(data)
    for i in data:
        if str(date.today()) == i["date"]:
            print('mentiinkö tänne?')
            i[type_t] = i[type_t] + usedTime
            return data
    day =   {   "date" : "",
                "uni" : 0,
                "opiskelu" : 0,
                "tyot" : 0,
                "muu" : 0
            }
    day["date"] = str(date.today())
    day[type_t] = day[type_t] + usedTime
    print(day)
    data.append(day)
    return data


def countUsedTime(timeEnd, timeStart):
    timeUsed = int(round((timeEnd-timeStart)/60, 6))
    timeUsedHour = int(timeUsed // 60)
    timeUsedMin = int(timeUsed%60)
    print()
    print(str(timeUsedHour)+" hour and "+str(timeUsedMin)+" min")
    return timeUsed #Palauttaa ajan minuutteina
    

def timePrint(timePrint):
    timePrint = time.localtime(timePrint)
    print(str(timePrint[3])+":"+str(timePrint[4])+":"+str(timePrint[5]))


def getWeek():
    return date.today().isocalendar()[1]


def help_info():
    print()
    print("Start time keeping:")
    print()
    for i in range(0,len(time_types)):
        print(time_types[i] + " - " + time_types_lyh[i])
    print()
    print("End time keeping:")
    print()
    for i in range(0, len(time_end_types)):
        print(time_end_types[i])
    
    print()
    print("Exit app: exit")
    timetracker()
        

def close():
    print("Time tracking ended!")


if __name__ == '__main__':
    timetracker()