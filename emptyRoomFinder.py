# Importing required libraries
from pypdf import PdfReader
from datetime import datetime

# Global Variables
classtypes = ["lecture", "lab", "tutorial", "workshop"]
classes = []
idcounter = 0
allLocations = set()


# Helper Functions
def isClasstype(classtype):
    """Check if the given classtype is valid."""
    return classtype in classtypes


def isDay(day):
    """Check if the given string is a valid weekday."""
    return day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


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
    global idcounter

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
        if isDay(word):
            day = word
            break
        if isClasstype(word):
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

    start = datetime.strptime(start, '%H:%M')
    end = datetime.strptime(end, '%H:%M')

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


def initialize_locations():
    """Extract all unique locations from classes."""
    for c in classes:
        for loc in c['locations']:
            if loc[0] in ['0', '1'] or loc in ['5.12', '6.29', '3.53', '6.30', '5.17', '6.28']:
                continue
            allLocations.add(loc)


def Available(day, time):
    """Check available locations at a specific day and time."""
    unavailable = set()
    for c in classes:
        if day == c['day'] and time >= c['start'] and time < c['end']:
            for loc in c['locations']:
                unavailable.add(loc)

    available = sorted(allLocations - unavailable)
    if set(available) == allLocations:
        print("\033[38;2;117;195;255m\nall rooms are available\033[0m")
    else:
        print()
        for i in available:
            print("\033[38;2;117;195;255m" + i + "\033[0m")


# Main Code Execution
load_classes("timetable.pdf")
initialize_locations()

# Current availability
print("\033[38;2;255;148;234m\nrooms available rn:\033[0m")
Available(datetime.now().strftime("%A").lower(), datetime.now().replace(year=1900, month=1, day=1))

# User interaction loop
again = True
while again:
    print("\033[38;2;255;206;107m\nsay 'no' if no\033[0m")

    while again:
        day = input("\033[38;2;255;148;234m\nWhich day? \033[0m").lower()
        if day.lower() == 'no':
            again = False
            break
        if not isDay(day):
            print("\nno")
            continue
        break

    while again:
        time = input("\033[38;2;255;148;234m\nWhen (HH:MM) (24h) ? \033[0m")
        if time.lower() == 'no':
            again = False
            break
        try:
            time = datetime.strptime(time, '%H:%M')
            break
        except ValueError:
            print("\nno")

    if not again:
        print("\033[38;2;255;206;107m\nok bye\n\033[0m")
        break

    Available(day, time)
