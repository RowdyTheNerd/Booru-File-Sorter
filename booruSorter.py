# BOORU SORTER PROJECT
# author: Dyst
# please read the README included in the zip before attempting to run this script.

import os 
import requests
import json
import shutil
import sys


# FUNCTIONS

# validate file name function
def validate(fileName):
    #validate file name
    if '.' not in fileName:
        print(f'\tfile name \'{fileName}\'　invalid: no extension found. ID set to 0')
        return False
    #validate that it matches template
    if '-' not in fileName:
        print(f'\tfile name \'{fileName}\' invalid: no separator found. ID set to 0.')
        return False
    return True
    
# isolate the file name from the address
def isolateName(address):
    split = address.split('\\')
    name = split[-1]
    return name 

# ISOLATE ID function
def isolateID(fileName):
    if validate(fileName) == False:
        return 0
    # split the name by dots and dashes
    split = fileName.replace('.','-').split('-')
    # delete the strings that defenitely aren't the ID
    goodItems = []
    for string in split:
        if string.isdigit():
            goodItems.append(string)
    if len(goodItems) == 1:
        ID = int(goodItems[0])
    else:
        # print(f'multiple or 0. ({goodItems})')
        ID = max(int(goodItems[0]))
    return ID

# trim artists: clean up the artist list, hopefully narrows it down to 1. 
def trimArtists(file):
    artistList = file['artist']
    # clean up extra artist tags
    badTags = ('avoid_posting','conditional_dnp', 'third-party_edit',
                'sound_warning','epilepsy_warning','jumpscare_warning',
                'ai_generated','ai_generated_audio')
    newList = []
    for artist in artistList:
        if artist not in badTags:
            newList.append(artist)
    file['artist'] = newList

# copyright tag handler
def trimCopyright(file):
    crlist = file['copyright']
    impCR = file['impliedCopyright']
    badCRtags = ('4th_of_july','christmas','earth_day','easter','father\'s_day',
                'halloween','mardi_gras','mother\'s_day','new_year','chinese_new_year',
                'st._patrick\'s_day','thanksgiving','valentine\'s_day',
                'mythology')
    
    # plan A: remove bad tags
    newList = []
    for tag in crlist:
        if tag not in badCRtags:
            newList.append(tag)  
    crlist = newList 
        
    # plan B:check for implications that have caused trouble before
    for relation in hindsight:
        if (relation['ante'] in crlist) & (relation['cons'] in crlist):
            crlist.remove(relation['cons'])
            impCR.append(relation['cons'])
            # print(f'tag {relation['cons']} removed with hindsight.')
    
    # return the data if this is sufficient (so it doesnt have to get tag data every time)
    if len(crlist) <= 1:
        file['copyright'] = crlist
        return file
    
    # plan C: find data for tag implications, remove dependant tags
    # convert the list to text for search
    crlistTXT = ''
    for copyright in crlist:
        crlistTXT = crlistTXT + "," + copyright
    tagURL = 'https://' + URL + '/tag_implications.json'
    antecedents = {'search[antecedent_name]': crlistTXT}
    response = requests.get(tagURL, headers=header, auth=(username,api_key), params=antecedents)
    impDict = json.loads(response.text) # a list of implying tags and the tags implied.
    # check if there are 0 tag implications
    if impDict == {'tag_implications': []}:
        return crlist
    # get a list of consequent tags 
    impTable = []
    for anteTag in impDict:
        if anteTag['status'] == 'active':
            impTable.append({'ante': anteTag['antecedent_name'], 'cons': anteTag['consequent_name']})
    # for each tag, check if its implied by another tag
    nonImpliedTags = []
    for tag in crlist:          # the tag being checked
        implied = False 
        for row in impTable:    #the list it is being checked against
            if tag in row['cons']:
                implied = True
                hindsight.append({'ante':row['ante'],'cons':tag})
        if implied:
            impCR.append(tag)
        else:
            nonImpliedTags.append(tag)
    #print(nonImpliedTags)
    crlist = nonImpliedTags

    file['copyright'] = crlist
    file['impliedCopyright'] = impCR
    return file

# function which decides what folder to put it in
def locator(file):
    # plan A: check special cases
    if file['id'] == 0:
        print(f'\tID is invalid. Defaulting to unknown folder.')
        return 'unknown'
    for tag in priorityTags:
        if tag in file['tags']:
            #print(f'\tPriority tag found! ({tag})')
            folder = tag
            folder = checker(folder)
            return folder
        
    # plan B: copyright
    # now check how many
    if len(file['copyright']) >= 1:
        folder = file['copyright'][0]
        folder = checker(folder)
        return folder
    
    # plan C: artist
    # in case of unknown artist
    if 'unknown_artist' in file['artist']:
        #print(f'\tArtist unknown. Moving to Unknown folder.')
        artist = 'Unknown'
    else:
        artist = file['artist'][0]
    artist = checker(artist)
    folder = os.path.join('other',artist)
    return folder

# count the number of files in a folder
def countFiles(directoryPath):
    count = 0
    try:
        for entry in os.listdir(directoryPath):
            fullPath = os.path.join(directoryPath, entry)
            if os.path.isfile(fullPath):
                count += 1
            elif os.path.isdir(fullPath):
                count += countFiles(fullPath)
        return count
    except FileNotFoundError:
        print(f"Error: Directory '{directoryPath}' not found.")
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0

# generate a list of addresses for all files in a folder
def listAddresses(unsortedFolder):
    # list all the files in the folder
    currentList = os.listdir(unsortedFolder)
    finalList = []
    for file in currentList: 
        # join the addresses
        address = os.path.join(unsortedFolder,file)
        #print(f'address: {address}')
        # if its a folder, add contents to final list
        if os.path.isdir(address):
            for subAddress in listAddresses(address):
                finalList.append(subAddress)
        # otherwise just add it to the list
        else:
            finalList.append(address)
            #print(f'adding {file}')
    return finalList

# fix file name if it wont work as a file name
def checker(destination):
    charsToRemove = '<>:"/\\|?*'
    newDes = destination
    for char in charsToRemove:
        newDes = newDes.replace(char, '')
    return newDes

#create a grouping of the files
def groupFiles(dataTable, groupSize):
    tempRow = []
    dataTable2D = []
    for index, file in enumerate(dataTable):
        tempRow.append(file)
        if (index % groupSize == groupSize - 1):
            dataTable2D.append(tempRow)
            tempRow = []
    dataTable2D.append(tempRow)
    return dataTable2D



# MAIN BODY OF CODE

#get configuration info from config file
with open('CONFIG.txt') as config:
    configInfo = config.readlines()

# get settings from config
counter = 0
index = 0
for line in configInfo:
    counter = counter + 1
    if line.startswith('unsorted folder:'):
        unsortedFolder = line.replace('unsorted folder:','').strip()
    elif line.startswith('sorted folder:'):
        sortedFolder = line.replace('sorted folder:','').strip()
    elif line.startswith('username:'):
        username = line.replace('username:','').strip()
    elif line.startswith('api key:'):
        api_key = line.replace('api key:','').strip()
    elif line.startswith('URL:'):
        URL = line.replace('URL:','').strip()
    elif line.startswith('priority tags:'):
        index = counter

# get priority tags
if index == 0:
    print('no priority tags list in config file. please check the formatting.')
    sys.exit()
rawTags = configInfo[index:]
priorityTags = []
for line in rawTags:
    priorityTags.append(line.strip())

# checking if either is blank
if unsortedFolder == '':
    print('No folder named in config file. please enter a folder to be sorted, and be sure to hit save.')
    sys.exit()
if sortedFolder == '':
    sortedFolder = unsortedFolder + ' sorted'
    print(f'No folder specified. creating new folder, \'{sortedFolder}\'')

# creating destination file if needed
if not os.path.exists(sortedFolder):
    os.makedirs(sortedFolder)
    print(f'Folder \'{sortedFolder}\' created.')

# list addresses for all files in the folder to be sorted
fileAddresses = listAddresses(unsortedFolder)

# create table for storing data
print('isolating IDs...')
dataTable = [{'address': address} for address in fileAddresses]
for file in dataTable:
    file['name'] = isolateName(file['address'])
    file['id'] = isolateID(file['name'])

#for file in dataTable:
#    print('ad: ' + file['address'] + ', nm: ' + file['name'] + ', id: ' +str(file['id']))

# group files 
# i can search "~id:123 ~id:124" to get both to come up; taking advantage of this for speed
groupSize = 40
dataTable2D = groupFiles(dataTable, groupSize)

#retrieve data for a group of files
print('retrieving tag data...')
deletedFiles = []
header = {'user-agent': 'booru file sorter WIP (by horny_pan_boi_uwu on e926)'}
for index, group in enumerate(dataTable2D):
    # create search string
    searchString = ''
    for file in group:
        searchString = searchString + '~id:' + str(file['id']) + ' '
    # find info for file
    postURL = 'https://' + URL + '/posts.json'
    tags = {'tags': searchString}
    response = requests.get(postURL, headers=header, auth=(username,api_key), params=tags)
    allData = json.loads(response.text)['posts']
    for file in group:
        hasMatch = False
        for post in allData:
            if post['id'] == file['id']:
                hasMatch = True
                # extract important info and add to table
                tags = post['tags']
                file['artist'] = tags['artist']
                file['tags'] = tags['general'] + tags['character'] + tags['species'] + tags['meta']
                file['copyright'] = tags['copyright']
        if hasMatch == False:
            print(f'post #{file['id']} was (probably) deleted from the servers.')
            deletedFiles.append(file)

# retrieve tag data for a single file
print('retrieving data for deleted files...')
for file in deletedFiles:
    # find info for file
    print(f'Data for post #{file['id']} found!')
    if file['id'] != 0:
        postURL = 'https://' + URL + '/posts/' + str(file['id']) + '.json'
        response = requests.get(postURL, headers=header, auth=(username,api_key))
        allTags = json.loads(response.text)['post']['tags']
        # extract important info and add to table
        file['artist'] = allTags['artist']
        file['tags'] = allTags['general'] + allTags['character'] + allTags['species'] + allTags['meta']
        file['copyright'] = allTags['copyright']
    else:
        file['artist'] = 'none'
        file['tags'] = 'none'
        file['copyright'] = 'none'

#create an implied copyright section for each file
for file in dataTable:
    file['impliedCopyright'] = []

# get tags cleaned up
print('cleaning up tag data...')
hindsight = []
for file in dataTable:
    trimArtists(file)
    trimCopyright(file)
    print(f'Copyright tags for post #{file['id']}: {file['copyright']}')
# print(hindsight)

# find a place for each post
for file in dataTable:
    file['destination'] = locator(file)

# get file sorted away
print('sorting files...')
for file in dataTable:
    print(f'Sorting file {file['name']}')
    startPath = file['address']
    destinationPath = os.path.join(sortedFolder, file['destination'])
    endPath = os.path.join(destinationPath, file['name'])
    if not os.path.exists(destinationPath):
        os.makedirs(destinationPath)
        print(f'\tFolder \'{destinationPath}\' created.')
    if not os.path.exists(startPath):
        print(f'\tFile \'{startPath}\' does not exist.')
        sys.exit('file did not exist.')
    else:
        shutil.copy(startPath, endPath)
        #print(f'\tFile \'{file['name']}\' copied to folder \'{file['destination']}\'.')

#finish up, check work
print('\nProgram complete.')
fileCount1 = countFiles(unsortedFolder)
print(f'{fileCount1} files in the original folder.')
fileCount2 = countFiles(sortedFolder)
print(f'{fileCount2} files in the new folder.')
if fileCount2 < fileCount1:
    print('some files were lost. please try running the program again.')
elif fileCount2 == fileCount1:
    print('all files transferred successfully. thanks for using the program!')
    # get user input
else:
    print('something went wrong, and there are now more files in the new folder. woops!')