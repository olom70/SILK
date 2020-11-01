# analyse des macros et procedures stockées de teradata
import os
import sys
import glob
import argparse
import re
import filecmp
import statistics

# Create the parser
my_parser = argparse.ArgumentParser(description='analyse des macros et des procédures')

# Add the arguments
my_parser.add_argument('InputF',
                       metavar='inputf',
                       type=str,
                       help='Full path to the file to analyze')


# Execute the parse_args() method
args = my_parser.parse_args()

# Initialize program variables after the parameters
inputFile = args.InputF

if not os.path.isfile(inputFile):
    print('The specified file does not exist')
    sys.exit()


def createDir(head, dirToCreate):
    '''
        create a directory by adding 'dirToCreate' to the path 'head"
    '''

    fullPathToCreate = head+os.sep+dirToCreate
    if not os.path.isdir(fullPathToCreate):
        os.mkdir(fullPathToCreate)
    return fullPathToCreate


def init(inputFile, macroDir, storedProcDir):
    '''
        extract directory of the file and create output directories
    '''
    dirToReturn = list()
    head, tail = os.path.split(inputFile)
    dirToReturn.append(createDir(head, macroDir))
    dirToReturn.append(createDir(head, storedProcDir))
    return dirToReturn, head

def writeSummary(head, fileName):
    '''
        once all the file is parsed, all the name of the encountered procedures
        and macros are to write in a summary file.
    '''
    output = head+os.sep+fileName
    analysis_output = open(output, 'w+')
    analysis_output.write("Summary of all the macros and procedures found"+"\n")
    analysis_output.write("----------------------------------------------"+"\n")
    for i in range(2):
        if i == 0:
            toExtract = 'MACRO'
            analysis_output.write("------"+"\n")
            analysis_output.write("MACROS"+"\n")
            analysis_output.write("------"+"\n")
            analysis_output.write("name : count"+"\n")
        if i== 1:
            toExtract = 'PROCEDURE'
            analysis_output.write("------"+"\n")
            analysis_output.write("PROCEDURES"+"\n")
            analysis_output.write("------"+"\n")
            analysis_output.write("name : count"+"\n")

        for key, value in progCount.items():
            (codeType, howMany) = value
            if codeType == toExtract:
                analysis_output.write(str(key) + " : " + str(howMany) + "\n")
    analysis_output.close()

def findCalls():
    '''
        once the global dictionary progCount is filled, parse again the 
        input file to find the CALLs
    '''
    pass

def mainLoopToParseFile(inputfile, whereToWrite):
    '''
        read each line of the inputfile and extracts the procedures and macros in separate files
    '''
    outputDir = ''
    codeType = ''
    howMany = 0
    needToStart = False
    needToEnd = False
    needToWrite = False
    
    with open(inputfile, 'r') as analysis_read: # file in which to seek macros and procedures
        for line in analysis_read:
            if line[0:7] == 'REPLACE':
                needToStart = True
            if line[0:4] == 'show':
                needToEnd = True

            if needToStart:
                alreadyMet = False
                # a typical replace procedure line : 'REPLACE PROCEDURE "BP_PROD_032_DWHDBS"."PR_WAR_FIC_GEN"'
                # now find the name of macros/procedure
                splittedLine = line.split()
                splittedName = splittedLine[2].partition('.')
                nameIs = splittedName[2].strip('"')
                if splittedLine[1] == 'PROCEDURE':
                    outputDir = whereToWrite[1]
                    codeType = 'PROCEDURE'
                else:
                    outputDir = whereToWrite[0]
                    codeType = 'MACRO'
                # add it to the dictionary and increment the times met
                if nameIs in progCount:
                    alreadyMet = True
                    Ctype, howMany = progCount[nameIs]
                    progCount[nameIs] = Ctype, howMany+1
                else:
                    progCount[nameIs] = codeType, 1
                # time to write the file
                if not alreadyMet:
                    needToWrite = True
                    try:
                        output = outputDir+os.sep+nameIs+'.sql'
                        analysis_output = open(output, 'w')
                    except:
                        print('can''t create '+output)
                        needToWrite = False
            
            if (needToEnd and needToWrite):
                analysis_output.close()
                needToWrite = False

            if needToWrite:
                analysis_output.write(line)
            
            needToStart = False
            needToEnd = False

# -- main
macroDir = 'macros'
storedProcDir = 'stored_procedures'
summaryFile = 'summary_macros_stored_procedures.txt'
whereToWrite = list()
progCount = {}
whereToWrite, head = init(inputFile, macroDir, storedProcDir)
mainLoopToParseFile(inputFile, whereToWrite)
writeSummary(head, summaryFile)
