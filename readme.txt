e6 Sorter
v1.0, updated aug 20, 2025
created by Dyst 

Hello! thanks for checking out my python script ive been working on. 

heres all the important info i can think of, but if I forgot anything please let me know. 

DISCLAIMERS:
- i am not an expert in python, and relearned it from scratch (after ~5 years of not using it) in order to make this project. however, i do have a bit of experience with coding and computer science, and did my best to make this script as easy to use, efficient and compatible as possible. 
- I have only tested it on my windows device, but linux should also theoretically work. 
- run this program at your own risk. there are some failsafes in place, but the program is prone to error, and may crash. it will not modify the original files only create copies.
- this program will also require you to input info about your e926 log in. this is purely to make the requests to the server to retrieve tag info, and I have no means to collect your data. However, if you are still concerned regarding your privacy (rightfully so!), please feel free to review the code to see what exactly its being used for.

PURPOSE:
This program is designed to take a folder containing images downloaded from certain booru websites (such as e926, a sfw furry imageboard) and organize them based on criteria set by the user. HOWEVER, the program operates under the assumption that the file name contains an ID number; some applications will include the ID in the name automatically when a file is downloaded (such as the android app "The Wolf's Stash"), but most others do not. (compatibility with other naming conventions is a planned future feature)

REQUIRED DOWNLOADS/LIBRARIES:
(some of the python libraries are included by default, others are not. Some research may be required.)
- an up-to-date version of Python
- an IDE that can run python scripts (I use VSCode, but any IDE should work)
- os (python library)
- requests (python library)
- json (python library)
- shutil (python library)
- sys (python library)

INSTRUCTIONS:
1. download the zip, and unzip it. Move the files from this zip, as well as the folder containing your files you would like to be sorted, into a new folder. 
2. open the file titled CONFIG-TEMPLATE.txt in notepad or a similar piece of software. you will need to input a couple important pieces of information so the program can run, such as:
- the name of the folder containing your files
- the name of the folder to sort files into (if left blank, a new file will be created)
- your booru username (the code to request data from the server requires a login.)
- your API key (to find yours, log in to your account and go to settings, and it should be under "general".)
- the URL of the website which hosts the images and their data (this was designed with e926 and related websites in mind, and has not been tested with any others).
- the 'priority tags'. when the program is deciding which folder to place a file in, it will first check the tags listed here before moving on and looking for any more info. tags should be listed 1 per line underneath the priority tags line.
3. once this info is in the config file, hit save, and then create a copy of the file called 'CONFIG.txt'. 
4. open the python script (booruSorter.py) in an IDE, and hit 'run'. 
5. after a few seconds (or minutes, depending on the size of your stash), the files should be copied into organized folders in the sorted folder specified int he config. the script will give updates in the terminal as it runs. 
6. once the script is finished, review the new folder. ideally, your files should now be categorized neatly into folders based on copyright (such as what show or game the characters are from). there will also be an "other" folder for posts with no copyright tags, in which posts are organized by who drew them.

HOW IT WORKS:
this is a rough outline of how this script works.
1. extract the info from the CONFIG file, such as user details and how files are organized.
2. take each file and check if the file name contains a valid post ID number.
3. Communicate with the servers for the imageboards and requests the tag data for each image.
4. discard copyright and artist tags which are not deemed useful in categorizing files.
5. categorize files by copyright tags first, and if none exist then categorize by the artist who drew it.
6. copy each file to its designated folder.

MODIFYING THIS PROGRAM:
I give full permission to modify this program in whatever ways may suit your needs, and to publish those changes here on github (as long as no changes were introduced with ill intent). 
I did my best to polish the program as much as I could, but I have no doubt that there is room for improvement. If you are experienced with python, file management or API infrastructure, then please feel free to look through the code and fix all the bugs and account for all the edge cases I didn't catch. 
If you would like to improve the functionality (such as making the code run more efficiently, or add compatibility for different use cases), then you are more than welcome to!

PLANNED FUTURE FEATURES:
- a visual GUI to replace the config file and terminal output
- a way to prioritize putting files in folders that already exist rather than creating new folders
- copyright subfolders (instead of moving files to the most specific copyright folder, put the more specific folder in the more general one)
- if a folder has just 1 file in it, move it to a misc. folder
- implement md5 search, so this script works with e6 files downloaded from a web browser.






