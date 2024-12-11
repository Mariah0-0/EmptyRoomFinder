import os
import json
from datetime import datetime

classes = []
allLocations = set()
allTTS = []
change = True

def read_json(path):
    data = []
    with open(path, "r") as tt:
        data = json.load(tt)
    for c in data:
        c['start'] = datetime.strptime(c['start'], '%H:%M')
        c['end'] = datetime.strptime(c['end'], '%H:%M')
        classes.append(c)
    
def get_latest_timetable():
    trimesters = ['winter', 'spring', 'autumn']
    isTT = False
    fileFound = False
    trimester = ''
    year = ''
    files = os.listdir('./converted_timetables')
    max = {'year': '0', 'trimester': 'winter', 'path': ''}
    
    for file in files:
        if len(file) < 15 or not file.endswith('.json'):
            continue
        
        # Extract year
        for i in range(len(file) - 3):
            if file[i] == '2' and file[i+1] == '0' and file[i+2].isdigit() and file[i+3].isdigit():
                year = file[i:i+4]
                isTT = True
                break
        if not isTT:
            continue
        isTT = False
        
        # Extract trimester
        for t in trimesters:
            if t in file.lower():
                isTT = True
                trimester = t
                break
        if not isTT:
            continue
        
        fileFound = True
        allTTS.append({'year' : year, 'trimester' : trimester, 'path' : os.path.join('./converted_timetables', file)})

        if (year > max['year']) or (year == max['year'] and trimesters.index(trimester) > trimesters.index(max['trimester'])):
            max['year'] = year
            max['trimester'] = trimester
            max['path'] = os.path.join('./converted_timetables', file)
    
    if not fileFound:
        print("cant find file :(")
        exit()
    
    return max


def initialize_locations():
    """Extract all unique locations from classes."""
    notLocs = ['3.50', '3.51', '3.53', '3.55', '4.49', '4.53', '4.54', '6.28', '6.29', '6.30']
    for c in classes:
        for loc in c['locations']:
            if loc[0] in ['0', '1'] or loc in notLocs:
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


def setTimetable():
    files = os.listdir('./converted_timetables')
    
    print()
    for i in range(len(files)):
        print("\033[38;2;117;195;255m" + str(i+1) + ". " + files[i][:-5] + "\033[0m")
    
    while True:
        choice = input("\033[38;2;255;148;234m\nWhich one? \033[0m").lower()
        if choice.isdigit() and 1 <= int(choice) <= len(files):
            break
        elif choice == 'no':
            print("\033[38;2;255;206;107m\nok bye\n\033[0m")
            exit()
            break
        else:
            print("\nno")
    
    return {'path': os.path.join("./converted_timetables", files[int(choice)-1])}


def main():
    global change
    setTT = False
    while change:
        change = False
        tt = setTT if setTT else get_latest_timetable()
        
        read_json(tt['path'])
        initialize_locations()

        # Current availability
        print("\033[38;2;255;148;234m\nrooms available rn:\033[0m")
        Available(datetime.now().strftime("%A").lower(), datetime.now().replace(year=1900, month=1, day=1))

        # User interaction loop
        again = True
        while again:
            print("\033[38;2;255;206;107m\nsay 'change' if change tt\033[0m")
            print("\033[38;2;255;206;107msay 'no' if no\033[0m")

            # Input day
            while again:
                day = input("\033[38;2;255;148;234m\nWhich day? \033[0m").lower()
                if day in ['no', 'change']:
                    again, change = False, (day == 'change')
                    setTT = setTimetable() if change else None
                    break
                if day not in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                    print("\nno")
                else:
                    break

            # Input time
            while again:
                time = input("\033[38;2;255;148;234m\nWhen (HH:MM) (24h) ? \033[0m")
                if time.lower() in ['no', 'change']:
                    again, change = False, (time.lower() == 'change')
                    setTT = setTimetable() if change else None
                    break
                try:
                    time = datetime.strptime(time, '%H:%M')
                    break
                except ValueError:
                    print("\nno")
            
            # Exit or process availability
            if not again and not change:
                print("\033[38;2;255;206;107m\nok bye\n\033[0m")
                break
            elif change:
                break

            Available(day, time)


main()