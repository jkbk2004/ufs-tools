import sys
import os
import argparse
from turtle import color, forward
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from datetime import datetime

'''
Description: Read in hpc usage data from given log file directory and provide a visualization.
    The goal is to help visualize HPC allocated core hours vs actual core hours used.
    There is an additional metric for fair share values.

'''

comArgs = argparse.ArgumentParser(
    prog="usageVisual", description="Visualize hpc usage data.")
comArgs.add_argument('-f', '--filepath', type=str)
comArgs.add_argument('-o', '--output', type=str)

args = comArgs.parse_args()

# graph settings
barWidth = 0.3
barPadding = 3
xFontSize = 12
yFontSize = 16
xAxisFont = 20
yAxisFont = 20
titleFontSize = 24
legendFontSize = 14
plotXSize = 25
plotYSize = 13
plotDPI = 500

filepath = args.filepath
outputFilepath = args.output


def getCurrentTime():
    '''Return current local time as a string'''
    currentTime = datetime.now()
    return currentTime.strftime('%b-%d-%Y (%I-%M-%Ss %p)')


def readLogData(filepath):
    '''
    Description: Reads in log data from given directory
    and returns a list of dicts, each with data on a log.

    Parameters: filepath (str): path to directory with logs

    Returns: data (object): list of dicts with log data
    '''

    acc = 'Project Report for:'
    reportTime = 'Report Run:'
    reportBeginning = 'Report Period Beginning:'
    machine = 'Machines:'
    initAlloc = 'Initial Allocation in Hours:'
    adjustAlloc = 'Adjusted Allocation:'
    usedCoreHrs = 'Total Core Hours Used:'
    fairShare = 'Project Fair Share:'

    data = []

    try:
        files = os.listdir(filepath)
    except Exception as e:
        sys.exit(f'Invalid input filepath provided. Error details:\n{e}')

    # go through each log and retrieve data
    for file in files:
        tmpDct = {}
        if file.endswith('.txt') or file.endswith('.log'):
            f = open(filepath+file)
            for line in f:
                if acc in line:
                    tmpDct['acc'] = line[line.find(acc)+len(acc):].strip()
                elif reportTime in line:
                    tmpDct['endTime'] = reformatTime(line[line.find(
                        reportTime)+len(reportTime):].strip())
                elif reportBeginning in line:
                    tmpDct['startTime'] = reformatTime(line[line.find(
                        reportBeginning)+len(reportBeginning):].strip())
                elif machine in line:
                    tmpDct['machineID'] = line[line.find(
                        machine)+len(machine):].strip()
                elif initAlloc in line:
                    tmpDct['initialAlloc'] = line[line.find(
                        initAlloc)+len(initAlloc):].strip().replace(',', '')
                elif adjustAlloc in line:
                    tmpDct['adjustedAlloc'] = line[line.find(
                        adjustAlloc)+len(adjustAlloc):].strip().replace(',', '')
                elif usedCoreHrs in line:
                    tmpDct['usedHrs'] = line[line.find(
                        usedCoreHrs)+len(usedCoreHrs):].strip().replace(',', '')
                elif fairShare in line:
                    tmpDct['fairShare'] = line[line.find(
                        fairShare)+len(fairShare):].strip()
            if(len(tmpDct) == 0):
                print('Empty/invalid log file, skipping...')
            else:
                data.append(tmpDct)
    if(len(data) == 0):
        sys.exit('No data retrieved from log directory. Exiting...')
    return data


def plotUsageData(data):
    '''
    Description: Makes a grouped bar chart from the given data for 
    HPC resource usage.

    Parameters: data (object): list of dicts containing data on each
    system's usage

    returns: none
    '''
    xlabels = []
    for i in range(len(data)):
        label = data[i]['startTime']+'-'+data[i]['endTime'] + \
            " "+data[i]['machineID']+'/'+data[i]['acc']
        xlabels.append(label)

    valsAlloc = getPlotColVals('adjustedAlloc', data)
    valsUsed = getPlotColVals('usedHrs', data)

    xSpacing = np.arange(len(xlabels))

    fig, ax = plt.subplots()
    barsAlloc = ax.bar(xSpacing - barWidth/2, valsAlloc,
                       barWidth, label='Allocated Core Hours', color='green')
    barsUsed = ax.bar(xSpacing + barWidth/2, valsUsed,
                      barWidth, label='Used Core Hours', color='red')

    ax.set_xlabel('Time frame & HPC / Account', fontsize=xAxisFont)
    ax.set_ylabel('Core Hours', fontsize=yAxisFont)
    ax.set_xticks(xSpacing,  xlabels,  fontsize=xFontSize)
    plt.yticks(fontsize=yFontSize)
    ax.legend(fontsize=legendFontSize)
    ax.set_title('HPC Core Hour Usage', fontsize=titleFontSize)

    # if output location not provided, let user decide in the graph popup
    if not args.output:
        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized()
        plt.show()
    else:
        fig = plt.gcf()
        fig.set_size_inches((plotXSize, plotYSize), forward=False)
        time = getCurrentTime()
        outputLoc = outputFilepath+f' Core Hour Resource Usage - {time}'
        plt.savefig(outputLoc, dpi=plotDPI)
        print(f'Plot figure saved to {outputFilepath}')

    return


def plotShareData(data):
    '''
    Description: Makes a fair share bar chart from the given data for 
    HPC resource usage.

    Parameters: data (object): list of dicts containing data on each
    system's usage

    returns: none
    '''
    xlabels = []
    for i in range(len(data)):
        label = data[i]['startTime']+'-'+data[i]['endTime'] + \
            " "+data[i]['machineID']+'/'+data[i]['acc']
        xlabels.append(label)

    fairShareVals = getPlotColVals('fairShare', data, toFloat=True)
    xspacing = np.arange(len(xlabels))

    fig, ax = plt.subplots()

    barsFairShare = ax.bar(xlabels, fairShareVals, barWidth)

    plt.xlabel('Time frame & HPC / Account', fontsize=xAxisFont)
    plt.ylabel('Fair Share', fontsize=yAxisFont)
    plt.xticks([r for r in range(len(fairShareVals))],
               xlabels, fontsize=xFontSize)
    plt.yticks(fontsize=yFontSize)
    plt.title('HPC Fair Share', fontsize=titleFontSize)

    ax.bar_label(barsFairShare)

    if not args.output:
        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized()
        plt.show()
    else:
        fig = plt.gcf()
        fig.set_size_inches((plotXSize, plotYSize), forward=False)
        time = getCurrentTime()
        outputLoc = outputFilepath+f' Fair Share  - {time}'
        plt.savefig(outputLoc, dpi=plotDPI)
        print(f'Plot figure saved to {outputFilepath}')
    return


def getPlotColVals(col, data, toFloat=False):
    '''
    Description: Return list of values from given dictionary key

    Parameters: data (object): list of dicts containing data on each
    system's usage

    returns: none
    '''
    vals = []
    for row in data:
        if toFloat:
            vals.append(float(row[col]))
        else:
            vals.append(int(row[col]))

    return vals


def reformatTime(time):
    '''Take time from logs and return a format for plot labels'''
    newTime = time.split()
    return datetime.strptime(
        f'{newTime[1]} {newTime[2]} {newTime[3]}', '%d %b %Y').strftime('%m/%d/%Y')


def main():

    logData = readLogData(filepath)
    # print(logData)
    plotUsageData(logData)
    plotShareData(logData)

    print('closing...')

    return


if __name__ == "__main__":
    main()
