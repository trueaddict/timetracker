import json
import time
import os.path
from datetime import date

#TODO
# - Poikkeavan Inputin hallinta
# - 
# - Koulukurssin yksilöllinen seuranta (Työprojektien seuranta)
# - Datan syöttö ulos
#   - Komentorivi <- DONE
#   - Harvest

time_types = ["sleep", "study", "work", "other"]
time_types_lyh =  ["un", "op", "ty", "mu"]
time_end_types = ["loppu", "end", "l", "lounas"]
close_types = "exit"
help_type = "help"
nayta_list = ["n", "nayta", "show"]

default_project = "kehitysprojekti"
default_projects = {
    "project_name" : default_project,
    "time_used" : 0
}

default_day = { 
    "date" : str(date.today()),
    "sleep" : 0,
    "study" : 0,
    "work" : [default_projects],
    "other" : 0
}

data_folder = "data/"
print(os.getcwd())
if os.getcwd() == "/Users/otto":
        data_folder = "coding/timetracker/data/"

def timetracker():
    data = initWeek()
    readTimeType(data)


def initWeek():
    weekNum = str(getWeek())
    if os.path.isfile(data_folder+'week'+weekNum+'.json'):
        with open(data_folder+'week'+weekNum+'.json') as file_data:
            print('File already exists')
            data = json.load(file_data)
            inc_today = True
            for day in data:
                if day["date"] == str(date.today()):
                    inc_today = False
            if inc_today:
                data.append(default_day)

            return data
    else:
        with open(data_folder+'week'+weekNum+'.json', 'w') as file_data:
            print('Creating new file / starting new week')
            data = []
            data.append(default_day)
            file_data.write(json.dumps(data, indent=4))
            file_data.close()
            return data
            

def readTimeType(data):
    time_type = input().split(' ')
    if close_types == time_type[0]:
        close()
    if help_type == time_type[0]:
        help_info()
    if time_type[0] in nayta_list:
        nayta(data)
    for i in range(0,len(time_types)):
        if time_types[i] == time_type[0]:
            if (len(time_type) > 1):
                startTime(data, time_types[i], time_type[1])
            else: startTime(data, time_types[i], default_project)
        elif time_types_lyh[i] == time_type[0]:
            if (len(time_type) > 1):
                startTime(data, time_types[i], time_type[1])
            else: startTime(data, time_types[i], default_project)
    

def startTime(data, type_t, project):
    timeStart = time.time()
    print( "Started " + type_t + " '" + project + "'")
    timePrint("", timeStart)
    endTime(data, timeStart, type_t, project)


def endTime(data, timeStart, type_t, project):
    listen = True
    while listen:
        input_listen = input()
        if input_listen == close_types:
            timeEnd = time.time()
            usedTime = countUsedTime(timeEnd, timeStart)
            saveData(data, usedTime, type_t, project)
            listen = False
        if input_listen in time_end_types:
            timeEnd = time.time()
            print()
            timePrint("Start time: " ,timeStart)
            timePrint("End time: " ,timeEnd)
            print()
            print("Used time: ")
            usedTime = countUsedTime(timeEnd, timeStart)

            #Debug
            #usedTime = 420

            listen = False
            saveData(data, usedTime, type_t, project)
            readTimeType(data)


def saveData(data, usedTime, type_t, project):
    weekNum = str(getWeek())
    if os.path.isfile(data_folder+'week'+weekNum+'.json'):
        with open(data_folder+'week'+weekNum+'.json', 'w') as file_data:
            for day in data:
                if day["date"] == str(date.today()):
                    if type_t == "work":
                        nothappened = True
                        for proj in day[type_t]:
                            if proj["project_name"] == project:
                                proj["time_used"] = proj["time_used"] + usedTime
                                nothappened = False
                        if nothappened:
                            new_proj = {
                                "project_name" : project,
                                "time_used" : usedTime
                            }
                            day[type_t].append(new_proj)
                                
                    else:
                        day[type_t] = day[type_t] + usedTime
            file_data.write(json.dumps(data, indent=4))
            file_data.close()
    else:
        print('File not found')


def countUsedTime(timeEnd, timeStart):
    timeUsed = int(round((timeEnd-timeStart)/60, 6))
    timeUsedHour = int(timeUsed // 60)
    timeUsedMin = int(timeUsed%60)
    print()
    print(str(timeUsedHour)+" hour and "+str(timeUsedMin)+" min")
    print()
    return timeUsed #Palauttaa ajan minuutteina
    

def timePrint(info ,timePrint):
    timePrint = time.localtime(timePrint)
    print(info + str(timePrint[3])+":"+str(timePrint[4]))


def getWeek():
    return date.today().isocalendar()[1]


def minToHoursAndMins(mins):
    timeUsedHour = int(mins // 60)
    timeUsedMin = int(mins%60)
    return str(timeUsedHour)+" hour and "+str(timeUsedMin)+" min"

def nayta(data):
    for day in data:
        overal_worktime = 0
        print("Date: " + day["date"])
        for proj in day["work"]:
            overal_worktime = overal_worktime + proj["time_used"]
            print("   " + proj["project_name"] + " : " + minToHoursAndMins(proj["time_used"]))
        print()
        print("   Overal worktime: "+ minToHoursAndMins(overal_worktime))
    readTimeType(data)


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