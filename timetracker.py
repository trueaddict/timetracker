import cmd
import sys
import json
import os.path
import time
import re
from time import strftime
from datetime import date, timedelta, datetime

from numpy import full
from harvest import Harvest


CONFIG_FILE = 'timetracker_config.json'
DATAFILES_PATH = 'datafiles_path'
ACCOUNT_ID = 'account_id'
USER_TOKEN = 'user_token'

""" Read configs
"""
config = {
  DATAFILES_PATH:"testdata",
  'harvest': {
    ACCOUNT_ID:'',
    USER_TOKEN:''
  },
  'weekly working time': '37.5',
  'weekly capacity %': '75'
}
if not os.path.isfile(CONFIG_FILE):
  print('Config file not found. Using default config')
else:
  with open(CONFIG_FILE, 'r') as configJson:
    config = json.load(configJson)

# Print configs
print('Timetracker configs:')
for key, item in config.items():
  if type(item) == dict:
    print('  '+key+':')
    for key2, item2 in item.items():
      print('    '+key2+':', item2)    
  else:
    print('  '+key+':', item)
print()

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

  runTime = None

  harvest = None

  #filePath = 'testdata/' # data file path
  data = [] # list of time tracking objects
  curTracking = None # time tracking object to handle attributes

  # --- timetracker commands ---
  def do_ty(self, arg):
    """
    Start time tracking for work
    ty <client> <project>
    """
    params = parse(arg)
    self.startTime(params)
    self.saveData()

  def complete_ty(self, text, line, begindx, endinx):    
    searchterm = ''
    i=0
    args = line.split(' ')[1:]
    for arg in args:
      searchterm = arg
      i=i+1
    offs = len(searchterm) - len(text)

    searchlist = []
    if i == 1:
      searchlist = self.harvest.getClients()
    if i == 2:
      searchlist = self.harvest.getTasks()

    return [s[offs:] for s in searchlist if s.lower().startswith(searchterm)]

  def do_l(self, arg):
    'End time tracking'
    if self.curTracking is None:
      return
    self.endTime()
    self.saveData()

  def do_add(self, arg):
    """
    Insert custom
    add <client> <project>
    """
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
    '''
    show - todays time usage
    show day.month.year - specific date time usage
    show day.month.year client - specific date specific client time usage
    '''
    params = parse(arg)
    while len(params) < 2:
      params.append(None)
    if params[0] is not None:
      params[0] = datetime.strptime(params[0], '%d.%m.%Y').date()
    else:
      params[0] = datetime.now().date()
    print('Given params:', params)
    # printData(self.data, date=params[0], client=params[1])
    self.saveData()
    runTimeData = [i for i in self.data]

    self.runTime.end = datetime.now()
    self.runTime.countUsedTime()
    runTimeData.append(self.runTime)
    
    printData(runTimeData, date=params[0], client=params[1])
    

  def do_harvest(self, arg):
    '''
    harvest - list harvest time entries
    '''

    startOfWeek = date.today() - timedelta(days=date.today().weekday())
    endOfWeek = startOfWeek + timedelta(days=6)
    todayEntries = self.harvest.getTimeEntries(startDate=date.today(), endDate=date.today())
    weekEntries = self.harvest.getTimeEntries(startDate=startOfWeek, endDate=endOfWeek)
    printDataHarvest(todayEntries, weekEntries)

  def do_exit(self, arg):
    'Stop application'
    if self.curTracking is not None:
      self.endTime()
    print('Ending time tracking')
    return True

  def do_config(self, arg):
    """
    Setup timetracker
    """
    
    print('Setup configs')
    print('Leave value empty to use current value')
    print()

    for key, item in config.items():
      if type(item) == dict:
        for key2, item2 in item.items():
          print('Current value:', config[key][key2])
          value = input(key + ', ' + key2 + ': ')
          if value.strip() != '':
            config[key][key2] = value
      else:
        value = ''
        print('Current value:', config[key])
        if key == 'datafiles_path':
           value = os.path.abspath(input(key + ': '))
        else:
          value = input(key + ': ')
        if value.strip() != '':
          config[key] = value

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

    if 'harvest' in config.keys():
      self.harvest = Harvest(user_token=config['harvest'][USER_TOKEN], account_id=config['harvest'][ACCOUNT_ID])
    
    if self.runTime is None:
      self.runTime = timeObject(datetime.now(), 'runtime', 'today')

  
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
  overall_time = datetime.min
  overall_time_week = datetime.min
  

  week_startDate = datetime.today().date() - timedelta(days=datetime.today().date().weekday())
  week_endDate = week_startDate + timedelta(days=6)
  
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
      overall_time = overall_time + i.timeUsed
    
    if i.client == 'runtime': continue  # skip runtime from overall counts
    
    if i.date >= week_startDate and i.date <= week_endDate:
      overall_time_week = overall_time_week + i.timeUsed

  for client_name in dataDict.keys():
    print(client_name)
    for project_name in dataDict[client_name]:
      print(indent + project_name + ' : ' + dataDict[client_name][project_name].strftime('%H:%M'))
  print()
  print('Total today: ' + overall_time.strftime('%H:%M'))
  print()
  capacityProgressBar(overall_time_week)
  print()

def printDataHarvest(entriesToday, entriesWeek):
    print()
    indent = "  "
    overall_time = datetime.min
    overall_time_week = datetime.min
    

    week_startDate = datetime.today().date() - timedelta(days=datetime.today().date().weekday())
    week_endDate = week_startDate + timedelta(days=6)
    
    dataDict = {}
    
    # Init dataDict
    for i in entriesToday:
        client = {}
        if i['client']['name'] not in dataDict.keys():
            dataDict[i['client']['name']] = client
        else:
            client = dataDict[i['client']['name']]
        client[i['task']['name']] = datetime.min
        dataDict[i['client']['name']] = client

    # Count used time per client and project on selected date / today
    for i in entriesToday:
        dataDict[i['client']['name']][i['task']['name']] = dataDict[i['client']['name']][i['task']['name']] + i['timeUsed']
        overall_time = overall_time + i['timeUsed']

    # Count week total hours
    for i in entriesWeek:
        overall_time_week = overall_time_week + i['timeUsed']
    
    for client_name in dataDict.keys():
        print(client_name)
        for project_name in dataDict[client_name]:
            print(indent + project_name + ' : ' + dataDict[client_name][project_name].strftime('%H:%M'))
    # pprint.pprint(dataDict)
    print()
    print('Total today: ' + overall_time.strftime('%H:%M'))
    print()
    capacityProgressBar(overall_time_week)
    print()

def capacityProgressBar(overall_time_week):
  """
  !NOTE In progress
  'weekly working time': '37.5',
  'weekly capacity %': '75'
  """ 
  weekCapacity = round(float(config['weekly working time']) * (float(config['weekly capacity %']) / 100), 2)
  weekTotal = round(abs(datetime.min - overall_time_week).total_seconds() / 3600, 2)
  
  print('Week total:', weekTotal)
  print('Week capacity:', weekCapacity)
  
  
  fullBarLength = 100
  barLength = int((weekTotal / weekCapacity) * 100)
  printBar(barLength=fullBarLength, text=' Week capacity (' + str(weekCapacity) + 'h / ' +  str(round((weekCapacity / 37.5) * 100))  + '%) ', barStart='|', barEnd='|')
  printBar(barLength=barLength, text=' ' + str(weekTotal) + 'h ', barStart='|', barEnd='>')

def printBar(barLength=100, text='', barStart='', barEnd=''):
  bar = [barStart]
  for i in range(barLength):
    bar.append('=')
  
  if len(text) % 2 != 0:
    text = text + ' '

  if len(text) < len(bar):
    textList = list(text)
    j = 0
    for i in range(int(len(bar)/2) - int(len(text) / 2), int(len(bar)/2) + int(len(text) / 2)):
      bar[i] = textList[j]
      j = j + 1
    bar.append(barEnd)
  else:
    textList = list(text)
    bar.append(barEnd)
    for s in textList:
      bar.append(s)

  print(''.join(bar))

def currentWeekFilePath():
  """ Return filename and path
  """
  weekNum = str(date.today().isocalendar()[1])
  year = str(date.today().year)
  return config[DATAFILES_PATH] + '/' + year + '_week'+weekNum+'.json'

def parse(arg):
  'Parses args to list'
  ret_array = []
  if '"' in arg:
    #ret_array.append(arg.split(' ')[:1][0])
    ret_array = re.findall(r'\"(.*?)\"', arg)
    print(ret_array)
    return ret_array
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
  try:
    import readline
  except ImportError:
    sys.stdout.write("No readline module found, no tab completion available.\n")
  TimetrackerShell().cmdloop()