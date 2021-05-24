import cmd
import sys
import json
import os.path
import time
from time import strftime
from datetime import date

class timeObject():
  start = None
  end = None
  date = None
  timeUsed = None
  client = None
  project = None

  def __init__(self, start, client='ceili', project='muu'):
    self.start = start
    self.client = client
    self.project = project
    self.date = date.today()

  def countUsedTime(self):
    """ Counts used time to minutes
    """
    self.timeUsed = int(round((self.end-self.start)/60,6))

  def toJSON(self):
    """ Returns object in Dict format
    """
    return {"start": str(self.start) ,"end": str(self.end),"date": str(self.date),"timeUsed": str(self.timeUsed),"client": self.client,"project": self.project}

  def timeToStr(self, val):
    """ Parses seconds to str
    """
    return strftime('%H:%M:%S', time.localtime(val))

  def printTimeObject(self):
    """ Prints objcet to cmd/terminal
    """
    print()
    #print('Date: ' + str(self.date))
    #printTime('Start time:', self.start)
    printTime('End time:', self.end)
    print('Client: ' + self.client)
    print('Project: ' + self.project)
    print('Used time: ' + minToHoursAndMins(self.timeUsed))
    print()


class TimetrackerShell(cmd.Cmd):
  intro = 'Welcome to timetracker. Type help or ? to list commands.\n'
  prompt = '$ '

  filePath = 'testdata/' # data file path
  if "timetracker" not in os.getcwd():
    filePath = "coding/timetracker/testdata/"
  data = None # list of time tracking objects
  curTracking = None # time tracking object to handle attributes

  # --- timetracker commands ---
  def do_ty(self, arg):
    'Start time tracking for work'
    params = parse(arg)
    self.startTime(params)
    

  def do_l(self, arg):
    'End time tracking'
    if self.curTracking is None:
      return
    self.endTime()

  def do_show(self, arg):
    'Show current weeks time usage'
    printData(self.data)

  def do_exit(self, arg):
    'Stop application'
    if self.curTracking is not None:
      self.endTime()
    print('Ending time tracking')
    return True

  # --- utility methods ---

  def startTime(self, params):
    """ Actions to start time tracking
    """
    if self.curTracking is not None:
      self.handleEndTracking()
      self.curTracking = None
    self.curTracking = timeObject(time.time(), params[0], params[1])
    self.prompt = 'Client: '+ self.curTracking.client + '\nProject: ' + self.curTracking.project + '\n$ '
    print()
    printTime('Start time:' , self.curTracking.start)

  def endTime(self):
    """ Actions after ending time tracking
    """
    self.handleEndTracking()
    self.curTracking.printTimeObject()
    self.prompt = '$ '
    self.curTracking = None

  def handleEndTracking(self):
    self.curTracking.end = time.time()
    self.curTracking.countUsedTime()
    self.data.append(self.curTracking)
    

  # --- data methods ---
  def postloop(self):
    """ Saves the data to correct JSON-file
    """
    curWeekFilePath = curWeekPath(self.filePath)
    with open(curWeekFilePath, 'w') as file_data:
      data = []
      for i in self.data:
        data.append(i.toJSON())
      file_data.write(json.dumps(data, indent=4))
      file_data.close()


  def preloop(self):
    """ Reads the data from JSON-file and parses it to editable objects
    """
    curWeekFilePath = curWeekPath(self.filePath)
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


def printData(data):
  print()
  indent = "  "
  dataDict = {}
  for i in data:
    dataDict[i.client] = {}
  for i in data:
    dataDict[i.client][i.project] = 0
  for i in data:
    dataDict[i.client][i.project] = dataDict[i.client][i.project] + i.timeUsed
  for i in dataDict.keys():
    print(i)
    for j in dataDict[i]:
      print(indent + j + ' : ' + minToHoursAndMins(dataDict[i][j]))
  print()

def curWeekPath(folderPath):
  """ Return filename and path
  """
  weekNum = str(date.today().isocalendar()[1])
  year = str(date.today().year)
  return folderPath + '/' + year + '_week'+weekNum+'.json'

def parse(arg):
  'Parses args to list'
  return arg.split()

def printTime(text ,argTime):
  """ Prints time (seconds) with text
  """
  localTime = time.localtime(argTime)
  strTime = str(localTime[3])+':'+str(localTime[4])
  print(text + ' ' + strTime)
  return strTime

def minToHoursAndMins(mins):
  """ Formats minutes to hours and minutes
  """
  timeUsedHour = int(mins // 60)
  timeUsedMin = int(mins%60)
  return str(timeUsedHour)+" hour and "+str(timeUsedMin)+" min"

if __name__ == '__main__':
  TimetrackerShell().cmdloop()