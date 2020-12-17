import cmd
import sys
import json
import os.path
import time
from time import strftime
from datetime import date, timedelta

class timeObject():
  start = None
  end = None
  date = None
  timeUsed = None
  client = None
  project = None

  def __init__(self, start, client, project):
    self.start = start
    self.client = client
    self.project = project
    self.date = date.today()

  # Counts used time to minutes
  def countUsedTime(self):
    self.timeUsed = int(round((self.end-self.start)/60,6))

  # Returns object in Dict format
  def toJSON(self):
    return {"start": str(self.start) ,"end": str(self.end),"date": str(self.date),"timeUsed": str(self.timeUsed),"client": self.client,"project": self.project}

  # Parses seconds to str
  def timeToStr(self, val):
    return strftime('%H:%M:%S', time.localtime(val))

  # Prints objcet to cmd/terminal
  def printTimeObject(self):
    print()
    print('Date: ' + str(self.date))
    printTime('Start time:', self.start)
    printTime('End time:', self.end)
    print('Used time: ' + minToHoursAndMins(self.timeUsed))
    print('Client: ' + self.client)
    print('Project: ' + self.project)
    print()


class TimetrackerShell(cmd.Cmd):
  intro = 'Welcome to timetracker. Type help or ? to list commands.\n'
  prompt = '$ '

  filePath = 'testdata/' # data file path
  data = None # list of time tracking objects
  curTracking = None # time tracking object to handle attributes

  # --- timetracker commands ---
  def do_ty(self, arg):
    'Start time tracking for work'
    params = parse(arg)
    self.startTime(params)
    

  def do_l(self, arg):
    'End time tracking'
    self.endTime()

  def do_show(self, arg):
    'Show current weeks time usage'
    print('show')
  def do_exit(self, arg):
    'Stop application'
    print('Ending time tracking')
    return True

  # --- utility methods ---

  # Actions to start time tracking
  def startTime(self, params):
    self.curTracking = timeObject(time.time(), params[0], params[1])
    self.prompt = self.curTracking.client + ' ' + self.curTracking.project + ' $ '
    printTime('Start time:' , self.curTracking.start)

  # Actions after ending time tracking
  def endTime(self):
    self.curTracking.end = time.time()
    self.curTracking.countUsedTime()
    self.curTracking.printTimeObject()
    self.prompt = '$ '
    self.data.append(self.curTracking)
    self.curTracking = None


  # --- data methods ---

  # Saves the data to correct JSON-file
  def postloop(self):
    weekNum = str(date.today().isocalendar()[1])
    curWeekFilePath = self.filePath + '/' + 'week'+weekNum+'.json'
    with open(curWeekFilePath, 'w') as file_data:
      data = []
      for i in self.data:
        data.append(i.toJSON())
      file_data.write(json.dumps(data, indent=4))
      file_data.close()

  # Reads the data from JSON-file and parses it to editable objects
  def preloop(self):
    weekNum = str(date.today().isocalendar()[1])
    curWeekFilePath = self.filePath + '/' + 'week'+weekNum+'.json'
    if os.path.isfile(curWeekFilePath):
      with open(curWeekFilePath, 'r') as file_data:
        self.data = []
        data = json.load(file_data)
        for i in data:
          startTime = float(i['start'])
          endTime = float(i['end'])
          obj = timeObject(startTime, i['client'], i['project'])
          obj.date = date.fromisoformat(i['date'])
          obj.end = endTime
          obj.timeUsed = int(i['timeUsed'])
          self.data.append(obj)
    else:
      self.data = []


# Split arguments to list
def parse(arg):
  'Parses args to list'
  return arg.split()


# Prints time (seconds) with text
def printTime(text ,argTime):
  localTime = time.localtime(argTime)
  strTime = str(localTime[3])+':'+str(localTime[4])
  print(text + ' ' + strTime)
  return strTime


# Formats minutes to hours and minutes
def minToHoursAndMins(mins):
    timeUsedHour = int(mins // 60)
    timeUsedMin = int(mins%60)
    return str(timeUsedHour)+" hour and "+str(timeUsedMin)+" min"

if __name__ == '__main__':
  TimetrackerShell().cmdloop()