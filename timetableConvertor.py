import os
import json
from pypdf import PdfReader
from datetime import datetime


# Global Variables

classes = []

# Helper Functions

def pick_timetable():
    choice = ''
    files = find_files()
    
    print()
    for i in range(len(files)):
        print(str(i+1) + ". " + files[i]['filename'])
    
    while True:
        choice = input('\nWhich one? ')
        if choice.isdigit() and 1 <= int(choice) <= len(files):
            break
    
    return files[int(choice)-1]

def find_files():
    trimesters = ['winter', 'spring', 'autumn']
    rawTTs = []
    files = os.listdir('./raw_timetables')

    for file in files:
        if len(file) < 14 or not file.endswith('.pdf'):
            continue
        
        # Initialize variables for year and trimester
        year = None
        trimester = None
        
        # Extract year
        for i in range(len(file) - 3):
            if file[i] == '2' and file[i+1] == '0' and file[i+2].isdigit() and file[i+3].isdigit():
                year = file[i:i+4]
                break
        
        # Extract trimester
        for t in trimesters:
            if t in file.lower():
                trimester = t
                break
        
        # If both year and trimester are found, add to results
        if year and trimester:
            rawTTs.append({
                'filename': file,
                'year': year,
                'trimester': trimester
            })

    return rawTTs

def parse_page_text(page_text):
    """Extract relevant lines from a page's text."""
    allLines = page_text.splitlines()
    lines = []

    for i in range(len(allLines)):
        firstWord = allLines[i].split()[0]
        if firstWord in ["Lecture", "Computer", "Tutorial", "Workshop"]:
            lines.append(allLines[i])
        elif firstWord in ["AND", "OR"]:
            lines.append(allLines[i][3:])

    return lines


def process_line(linestr):
    """Process a single line to extract class details."""
    classtypes = ["lecture", "lab", "tutorial", "workshop"]
    idcounter = 0

    classtype = ''
    day = ''
    start = ''
    end = ''
    location = []
    instructor = []
    words = linestr.lower().replace(')', ' ').replace('\\', ' ').replace(';', ' ').split()

    # Identify day and classtype
    for word in words:
        words = words[1:]
        if word in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            day = word
            break
        if word in classtypes:
            classtype = word

    if day == '':
        print("day not found")
        raise ValueError("Missing day")

    if classtype == '':
        print("classtype not found")
        raise ValueError("Missing classtype")

    # Identify start and end times
    start_i = end_i = 0
    for i in range(len(words)):
        if words[i] == '-':
            start_i = i - 1
            end_i = i + 1
            break

    if len(words[start_i]) != 5:
        end = words[start_i][:4]
        words[start_i] = words[start_i][4:]
    else:
        start = words[start_i]

    if len(words[end_i]) != 5:
        end = words[end_i][:5]
        words[end_i] = words[end_i][5:]
        words.insert(end_i, end)
    else:
        end = words[end_i]

    # Extract location
    words = words[3:]
    if not words[0][0].isdigit():
        return

    if words[0][4] == '-':
        location.append(words[0][0:4])
    else:
        loc = words[0][0:5]
        location = [loc[0:4], loc[0:3] + loc[4]]

    # Extract instructors
    words = words[1:]
    for i in range(len(words)):
        if words[i][-1] == ',':
            try:
                instructor.append(words[i] + ' ' + words[i + 1])
            except IndexError:
                pass

    idcounter += 1
    classes.append({
        'id': idcounter,
        'classtype': classtype,
        'day': day,
        'start': start,
        'end': end,
        'locations': location,
        'instructors': instructor
    })


def load_classes(file_path):
    """Parse all pages from the timetable PDF and extract classes."""
    reader = PdfReader(file_path)

    for pageno in range(len(reader.pages)):
        page = reader.pages[pageno]
        lines = parse_page_text(page.extract_text())

        for linestr in lines:
            try:
                process_line(linestr)
            except ValueError:
                print("ur wrong")
                return


def main():
    timetable = pick_timetable()
    
    load_classes(os.path.join("./raw_timetables", timetable['filename']))
    
    with open(os.path.join("./converted_timetables", (timetable['trimester'] + timetable['year'] + '.json')), "w") as outfile: 
        json.dump(classes, outfile, indent = 4)


main()