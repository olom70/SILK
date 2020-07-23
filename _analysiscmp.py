# analyse perl sources and BTEQ sources.
import os
import sys
import glob
import argparse
import re
import filecmp
import statistics

# Create the parser
my_parser = argparse.ArgumentParser(description='analyse perl sources and BTEQ sources')

# Add the arguments
my_parser.add_argument('Path',
                       metavar='path',
                       type=str,
                       help='the path to list')

my_parser.add_argument('FilesExt',
                       metavar='ext',
                       type=str,
                       help='the extensions of files to analyse')

# Execute the parse_args() method
args = my_parser.parse_args()

# Initialize program variables after the parameters
extension = args.FilesExt
input_path = args.Path

if not os.path.isdir(input_path):
    print('The path specified does not exist')
    sys.exit()

# variables and functions of the program
dicOfFilesWithDetails = {}
dicOfIdenticalFiles = {}
booleandigitInName = lambda d : d != None
booleanunderscoreInName = lambda u : u > 0

def getfiles(input_path, extension):
    '''
        returns the files of the specified dir that have the specified extension
    '''
    dic = {}
    alreadyChecked = False
    for file in (glob.glob(input_path + "*." + extension,recursive=False)):
        file_stats = os.stat(file)
        size = file_stats.st_size
        #get just the name the file without the path nor the extension
        filename = file[file.rfind(os.path.sep)+1:-(len(file)-(file.rfind('.')))]
        # get the prefix of the file
        # what is the prefix ?
        #  - the part before
        #    - the last _ or
        #    - the first digit
        bu = booleanunderscoreInName(filename.rfind('_'))
        bd = booleandigitInName(re.search(r"\d",filename))
        underscoreInName = filename.rfind('_')
        digitInName = re.search(r"\d",filename)
        
        if (bu): whereToCut = underscoreInName
        if (not bu and bd): whereToCut = digitInName.start()
        if (bu or bd):
            toCut = True
        else:
            toCut = False

        if (toCut):
            prefix = filename[0:whereToCut]
            suffix = filename[whereToCut:]
        else:
            prefix = filename
            suffix = filename
        # finally add all the information in a dictionary
        dic[file] = filename, prefix, suffix, size, alreadyChecked
    return dic

def writeMainDictionary(output):
    '''
    Writes the details of all the files that are to be inspected
    '''
    analysis_output = open(output, 'w+')
    analysis_output.write("fullpath;filename;prefix;suffix;size;alreadyChecked\n")
    for key, value in dicOfFilesWithDetails.items():
        (filename, prefix, suffix, size, alreadyChecked) = value
        analysis_output.write(str(key) + ";" + str(filename) + ";" + str(prefix) + ";" + str(suffix) + ";" + str(size) + ";" + str(alreadyChecked) + "\n")
    analysis_output.close()

def filterTheDict(dictObj, mainKey, newList, toBeComparedTo, counter):
    # Iterate over all the items in dictionary
    for (key, value) in dictObj.items():
        # Check if item satisfies the given condition then add to new dict
        (filename, prefix, suffix, size, alreadyChecked) = value
        if (not alreadyChecked and size == toBeComparedTo):
            if (filecmp.cmp(mainKey, key, shallow=False)):
                dicOfFilesWithDetails[key] = filename, prefix, suffix, size, True # don't check again that file
                newList.append(key)
                counter +=1
    return newList, counter

def groupIdenticalFiles(output):
    groupNumber = 1
    newList = list()
    listToWrite = list()
    nbOfFiles = 1
    analysis_output_groups = open(output, 'w+')
    analysis_output_groups.write("group;file1;file2;file3;file4;file5;file6;file7;file8;file9;file10;file11;file12;file13;file14;file15;file16;file17;file18;file19;file20\n")
    for key, value in dicOfFilesWithDetails.items():
        (filename, prefix, suffix, size, alreadyChecked) = value
        if not alreadyChecked:
            dicOfFilesWithDetails[key] = filename, prefix, suffix, size, True # That key won't be examined later
            del listToWrite[:]
            del newList[:]
            nbOfFiles = 1
            newList.append(key) # initialize the list that will contains all the files with the same size
            listToWrite, nbOfFiles = filterTheDict(dicOfFilesWithDetails, key, newList, size, nbOfFiles)
            analysis_output_groups.write(f'{groupNumber}')
            for p in listToWrite:
                analysis_output_groups.write(f';{p}')
            analysis_output_groups.write(f';n{nbOfFiles};s{size}\n')
            groupNumber += 1
    analysis_output_groups.close()

def removeComments(extraExtension):
    '''
        parse the files and strip them from the comments
        purpose : see if the result is different
        comments markers : # =head =cut REM
        empty lines are also skipped
    '''
    for key in dicOfFilesWithDetails:
        analysis_write = open(f'{key}{extraExtension}', 'w+')# resulting file without the comments ("cr" means "comments removed")
        with open(key, 'r') as analysis_read: # file in which to seek comments
            needToReachCut = False
            for line in analysis_read:
                lineToWrite = True
                if (line[0] == '\n'):
                    lineToWrite = False
                if (line[0:3] == 'REM' or line[0] == '#'):
                    lineToWrite = False
                if (line[0:5] == '=head'):
                    lineToWrite = False
                    needToReachCut = True
                if (needToReachCut):
                    lineToWrite = False
                if (line[0:4] == '=cut'):
                    lineToWrite = False
                    needToReachCut = False
                if (lineToWrite):
                    analysis_write.write(line)
        analysis_write.close()

def dumpGroupContent(inputFile, extensionToRemove, pathToTest):
    groupNumber = int()
    filename = str()
    filenameBeginning = int()
    filenameEnding = int()
    lenToremove = len(extensionToRemove) # at this point the dictionary is filled with the files without comments (with extra extension added). But one want to read the untouched file
    with open(inputFile, 'r') as analysis_read:
        for line in analysis_read:
            filenameBeginning = line.find(';',0)+1 # to find the first ";"
            groupNumber = line[0:filenameBeginning-1]
            filenameEnding = line.find(';', 10) - lenToremove # to find the second ";" assuming starting at position 10 is enough to skip the first ";" 
            filename=line[filenameBeginning:filenameEnding]
            if (filename[0:2] == pathToTest[0:2]):
                with open(filename) as toRead:
                    text = toRead.read()
                with open(f'{groupNumber}.txt', 'w+') as toWrite:
                    toWrite.write(text)
                
def reportsOnGroups(input, output):
    groupNumber = int()
    nbOfFiles = int()
    size = int()
    whereisSize = int()
    whereisNbOfFiles = int()
    filenameBeginning = int()
    toWrite = open(output, 'w+')
    toWrite.write('group;nbOfFiles;size\n')
    with open(input) as toRead:
        for line in toRead:
            if line[0] != 'g':
                filenameBeginning = line.find(';',0)+1 # to find the first ";"
                groupNumber = line[0:filenameBeginning-1]
                whereisSize = line.find(';s')
                whereisNbOfFiles = line.find(';n')
                nbOfFiles = line[whereisNbOfFiles+2:whereisSize]
                size = line[whereisSize+2:]
                toWrite.write(f'{groupNumber};{nbOfFiles};{size}')
    toWrite.close()

 # ---- main ----
for i in range(2):
    extraExtension = '.cr'

    if i == 0:
        outputwriteMainDictionary = '_filesToAnalyze_untouched.txt'
        outputgroupIdenticalFIles = '_identical_files_group.txt'
        groupSummary = '_summary.txt'
        currentExtension = extension

    if i == 1:
        outputwriteMainDictionary = '_filesToAnalyze_without_comments.txt'
        outputgroupIdenticalFIles = '_identical_files_group_without_comments.txt'
        groupSummary = '_summary_without_comments.txt'
        dicOfFilesWithDetails.clear
        currentExtension = extension + extraExtension

    # get all the details we need about the files
    # purpose : it's the base to browse and compare between them
    dicOfFilesWithDetails = getfiles(input_path, currentExtension)

    # write the content of the dictionary in a file in order to get an handy reference to dive into
    writeMainDictionary(outputwriteMainDictionary)

    # parse the dictionary and for each key(=file) find others keys(=file) with the same content.
    # purpose : group them and be able to know the how many group there are
    groupIdenticalFiles(outputgroupIdenticalFIles)

    # parse the files and strip them from the comments
    # purpose : see if the result is different
    # comments markers : # =head =cut REM
    if i == 0:
        removeComments(extraExtension)

    # dump once the content of the files that are identical
    # purpose : being able to have à look at what are doint each groups of files
    # and see (manually with your onw eyes) whare are the groups that are very similar despite being different
    if i == 1:
        dumpGroupContent(outputgroupIdenticalFIles, '', input_path) # to dump untouched files : extraExtension instaed of ''
    
    reportsOnGroups(outputgroupIdenticalFIles, groupSummary)
