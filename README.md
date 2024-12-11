Here's the updated version of the README:

### **Empty Room Finder**

This project helps find empty rooms in a university based on the official timetable. It is divided into two main functionalities for better efficiency:

1. **`timetableConverter.py`**: Converts raw PDF timetable files from the `raw_timetables/` directory into JSON format and saves them in the `converted_timetables/` directory.
2. **`emptyRoomFinder.py`**: Uses the converted JSON files to find available rooms based on the current or user-specified timetable.

For convenience, the full program (`emptyRoomFinder_fullProgram.py`) combines both functionalities, allowing you to find available rooms based on the latest timetable, without the need for separate conversion.

### **Usage**
- **To Find Empty Rooms**: `python emptyRoomFinder.py`
- **To Convert Timetables**: `python timetableConverter.py`
- **To Run Full Program**: `python emptyRoomFinder_fullProgram.py`

The program can switch timetables during runtime for added flexibility.