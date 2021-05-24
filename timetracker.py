import cmd
import sys
import json
import os.path
import time
from time import strftime
from datetime import date, timedelta, datetime


CONFIG_FILE = 'timetracker_config.json'
DATAFILES_PATH = 'datafiles_path'

""" Read configs
"""
config = {
  DATAFILES_PATH:"testdata"
}
if not os.path.isfile(CONFIG_FILE):
  print('Config file not found. Using default config')
else:
  with open(CONFIG_FILE, 'r') as configJson:
    config = json.load(configJson)

print(json.dumps(config, indent=4))

class timeObject():
  start = None
  end = None
  date = None
  timeUsed = None
  client = None
  project = None

  def __init__(self, start=None, client='ceili', project='muu'):
    self.start = start
    self.client = client
    self.project = project
    self.date = datetime.now().date()

  def countUsedTime(self):
    """ Counts used time to minutes
    """
    self.timeUsed = self.end-self.start # int(round(()/60,6))

  def toJSON(self):
    """ Returns object in Dict format
    """
    return {"start": self.start.strftime('%Y-%m-%d %H:%M:%S') ,"end": self.end.strftime('%Y-%m-%d %H:%M:%S') ,"date": str(self.date),"timeUsed": self.timeUsed.total_seconds() ,"client": self.client,"project": self.project}

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
    print('Used time: ' + str(self.timeUsed))
    print()


class TimetrackerShell(cmd.Cmd):
  """ Cmd application
  """
  intro = 'Welcome to timetracker. Type help or ? to list commands.\n'
  prompt = '$ '

  #filePath = 'testdata/' # data file path
  data = [] # list of time tracking objects
  curTracking = None # time tracking object to handle attributes

  # --- timetracker commands ---
  def do_ty(self, arg):
    'Start time tracking for work'
    params = parse(arg)
    self.startTime(params)
    self.saveData()
    

  def do_l(self, arg):
    'End time tracking'
    if self.curTracking is None:
      return
    self.endTime()
    self.saveData()

  def do_add(self, arg):
    'Insert custom'
    try:
      params = parse(arg)
      obj = timeObject()
      obj.client = params[0]
      obj.project = params[1]
      obj.date = datetime.strptime(input('Date xx.xx.xxxx : '), '%d.%m.%Y')
      obj.start = datetime.strptime(input('Start time xx:xx : '), '%H:%M')
      obj.end = datetime.strptime(input('End time xx:xx : '), '%H:%M')
    except ValueError:
      print('Error, try again')
      return
    obj.countUsedTime()
    print(obj.toJSON())

  def do_show(self, arg):
    'Show current weeks time usage'
    params = parse(arg)
    while len(params) < 2:
      params.insert(0,None)
    if params[0] is not None:
      params[0] = datetime.strptime(params[0], '%d.%m.%Y').date()
    else:
      params[0] = datetime.now().date()
    print('Given params:', params)
    printData(self.data, date=params[0], client=params[1])
    self.saveData()

  def do_exit(self, arg):
    'Stop application'
    if self.curTracking is not None:
      self.endTime()
    print('Ending time tracking')
    return True

  def do_config(self, arg):
    'Setup timetracker'
    config[DATAFILES_PATH] = os.path.abspath(input('Data files path: '))

    saveConfig()
    self.preloop()



  # --- utility methods ---

  def startTime(self, params):
    """ Actions to start time tracking
    """
    if self.curTracking is not None:
      self.handleEndTracking()
      self.curTracking = None
    self.curTracking = timeObject(datetime.now(), params[0], params[1])
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
    self.curTracking.end = datetime.now()
    self.curTracking.countUsedTime()
    self.data.append(self.curTracking)
    

  # --- data methods ---
  def postloop(self):
    """ Saves the data to correct JSON-file
    """
    self.saveData()


  def preloop(self):
    """ Reads the data from JSON-file and parses it to editable objects
    """
    createDataFilesDirectory(config[DATAFILES_PATH])
    curWeekFilePath = currentWeekFilePath()
    if os.path.isfile(curWeekFilePath):
      with open(curWeekFilePath, 'r') as file_data:
        self.data = []
        data = json.load(file_data)
        for i in data:
          startTime = datetime.strptime(i['start'], '%Y-%m-%d %H:%M:%S')
          endTime = datetime.strptime(i['end'], '%Y-%m-%d %H:%M:%S')
          obj = timeObject(startTime, i['client'], i['project'])
          obj.date = datetime.strptime(i['date'], '%Y-%m-%d').date()
          obj.end = endTime
          obj.timeUsed = timedelta(seconds=float(i['timeUsed']))
          self.data.append(obj)
    elif self.data is []:
      self.data = []
  
  def saveData(self):
    createDataFilesDirectory(config[DATAFILES_PATH])
    curWeekFilePath = currentWeekFilePath()
    with open(curWeekFilePath, 'w') as file_data:
      data = []
      for i in self.data:
        data.append(i.toJSON())
      file_data.write(json.dumps(data, indent=4))
      file_data.close()


def printData(data, date=None, client=None):
  print()
  indent = "  "
  dataDict = {}
  for i in data:
    if date == None and client == None:
      dataDict[i.client] = {}
    elif i.date == date and client == None:
      dataDict[i.client] = {}
    elif i.date == date and client == i.client:
      dataDict[i.client] = {}
  
  for i in data:
    if date == None and client == None:
      dataDict[i.client][i.project] = datetime.min
    elif i.date == date and client == None:
      dataDict[i.client][i.project] = datetime.min
    elif i.date == date and client == i.client:
      dataDict[i.client][i.project] = datetime.min
    
  for i in data:
    if date == None and client == None:
      dataDict[i.client][i.project] = dataDict[i.client][i.project] + i.timeUsed
    elif i.date == date and client == None:
      dataDict[i.client][i.project] = dataDict[i.client][i.project] + i.timeUsed
    elif i.date == date and client == i.client:
      dataDict[i.client][i.project] = dataDict[i.client][i.project] + i.timeUsed
    
  for i in dataDict.keys():
    print(i)
    for j in dataDict[i]:
      print(indent + j + ' : ' + dataDict[i][j].strftime('%H:%M'))
  print()

def currentWeekFilePath():
  """ Return filename and path
  """
  weekNum = str(date.today().isocalendar()[1])
  year = str(date.today().year)
  return config[DATAFILES_PATH] + '/' + year + '_week'+weekNum+'.json'

def parse(arg):
  'Parses args to list'
  return arg.split()

def printTime(text ,argTime):
  """ Prints time (seconds) with text
  """
  #localTime = time.localtime(argTime)
  strTime = argTime.strftime('%H:%M')
  print(text + ' ' + strTime)
  return strTime

def minToHoursAndMins(mins):
  """ Formats minutes to hours and minutes
  """
  timeUsedHour = int(mins // 60)
  timeUsedMin = int(mins%60)
  return str(timeUsedHour)+" hour and "+str(timeUsedMin)+" min"


def createDataFilesDirectory(path):
  if not os.path.isdir(path):
    os.makedirs(path)
    

def saveConfig():
  with open(CONFIG_FILE, 'w') as configJson:
    configJson.write(json.dumps(config, indent=2))

if __name__ == '__main__':
  TimetrackerShell().cmdloop()