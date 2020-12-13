import cmd
import sys
import json
import time
import os.path
from datetime import date

class TimetrackerShell(cmd.Cmd):
  intro = 'Welcome to timetracker. Type help or ? to list commands.\n'
  prompt = '$ '
  file = None

  filePath = 'testdata/'
  data = None

  start = None
  end = None
  timeUsed = None
  client = None
  project = None

  

  # --- timetracker commands ---
  def do_ty(self, arg):
    'Start time tracking for work'
    params = parse(arg)
    self.clientAndProject(params)
    self.startTime()
    

  def do_l(self, arg):
    'End any time tracking'
    self.endTime()
    self.countUsedTime()
    #self.save()

  def do_show(self, arg):
    'Show current weeks time usage'
    print('show')
  def do_exit(self, arg):
    'Stop application'
    print('Ending time tracking')
    return True

  # --- utility methods ---
  def startTime(self):
    self.start = time.time()
    self.prompt = self.client + ' ' + self.project + ' $ '
    printTime(self.start)

  def endTime(self):
    self.end = time.time()
    self.prompt = '$ '

  def countUsedTime(self):
    timeUsed = int(round((self.end-self.start)/60,6))
    self.timeUsed = timeUsed
    print(timeUsed)
    return timeUsed

  def clientAndProject(self, params):
    self.client = params[0]
    self.project = params[1]

  def save(self):
    todayStr = str(date.today())
    cli = self.client
    proj = self.project
    dataToday = self.data[todayStr]
    print(dataToday)
    dataCli = dataToday[cli]

    project = {proj : self.countUsedTime()}
    dataCli.append(project)
    print(dataCli)

  # --- data methods ---
  def postloop(self):
    weekNum = str(date.today().isocalendar()[1])
    curWeekFilePath = self.filePath + '/' + 'week'+weekNum+'.json'
    with open(curWeekFilePath, 'w') as file_data:
      file_data.write(json.dumps(self.data, indent=4))
      file_data.close()

  def preloop(self):
    weekNum = str(date.today().isocalendar()[1])
    curWeekFilePath = self.filePath + '/' + 'week'+weekNum+'.json'
    if os.path.isfile(curWeekFilePath):
      with open(curWeekFilePath, 'r') as file_data:
        self.data = json.load(file_data)
        print(self.data)
    else:
      print('File not found')

def parse(arg):
  'Parses args to list'
  return arg.split()

def printTime(argTime):
  localTime = time.localtime(argTime)
  strTime = str(localTime[3])+':'+str(localTime[4])
  print(strTime)
  return strTime

if __name__ == '__main__':
  TimetrackerShell().cmdloop()