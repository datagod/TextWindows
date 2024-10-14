#------------------------------------------------------------------------------
# Author: William McEvoy AND ChatGPT                                         --
# Created: Oct 12 2024                                                       --
#                                                                            --
# Purpose:  TextWindow and TextPad classes for creating and managing text    --
#           windows and pads in a curses-based terminal interface. This file --
#           can be used as a standalone module to integrate with other       --
#           programs requiring a simple curses-based user interface.         --
#                                                                            --
# Usage:                                                                     --
#   To use the TextWindow or TextPad class in another Python program,        --
#   import this module and create instances of the classes by providing      --
#   appropriate parameters for the window or pad dimensions, coordinates,    --
#   and styles.                                                              --
#                                                                            --
# Example:                                                                   --
#   from textwindow import TextWindow, TextPad                               --
#                                                                            --
#   window1 = TextWindow('Window1', 10, 40, 0, 0, 10, 40, 'Y', 2, 2)         --
#   window1.ScrollPrint("Hello, World!", Color=3, TimeStamp=True)            --
#                                                                            --
#   pad1 = TextPad('Pad1', 100, 40, 1, 1, 10, 40, 'N', 2)                    --
#   pad1.PadPrint("This is a long text to be printed in a pad.", Color=4)    --
#                                                                            --
#------------------------------------------------------------------------------
#
# Imported Modules:                                                          --
#   - curses: Provides functions to create text-based user interfaces.       --
#   - traceback: Used for generating and formatting stack trace information  --
#                when exceptions occur.                                      --
#   - datetime: Used for creating timestamps for messages displayed in the   --
#               TextWindow and TextPad.                                      --
#   - time: Provides time-related functions used in error handling.          --
#   - sys: Provides access to system-specific parameters and functions,      --
#          used in error handling to exit the program gracefully.            --
#   - inspect: Used to get information about the current stack frame to      --
#              determine the calling function in the error handler.          --
#------------------------------------------------------------------------------

import curses
import traceback
from datetime import datetime
import time
import sys
import inspect

class TextWindow(object):
    def __init__(self, name, rows, columns, y1, x1, y2, x2, ShowBorder, BorderColor, TitleColor):
        max_y, max_x = curses.LINES - 1, curses.COLS - 1
        self.rows = min(rows, max_y - y1)
        self.columns = min(columns, max_x - x1)

        if self.rows <= 0 or self.columns <= 0:
            raise ValueError("Window size exceeds terminal size. Please expand your terminal.")

        self.name = name
        self.y1 = y1
        self.x1 = x1
        self.y2 = y2
        self.x2 = x2
        self.ShowBorder = ShowBorder
        self.BorderColor = BorderColor  # pre-defined text colors 1-7
        try:
            self.window = curses.newwin(self.rows, self.columns, self.y1, self.x1)
        except curses.error:
            raise ValueError("Failed to create a new window. Check if terminal size is sufficient.")
        
        self.CurrentRow = 1
        self.StartColumn = 1
        self.DisplayRows = self.rows  # we will modify this later, based on if we show borders or not
        self.DisplayColumns = self.columns  # we will modify this later, based on if we show borders or not
        self.PreviousLineText = ""
        self.PreviousLineRow = 0
        self.PreviousLineColor = 2
        self.Title = ""
        self.TitleColor = TitleColor

        if self.ShowBorder == 'Y':
            self.CurrentRow = 1
            self.StartColumn = 1
            self.DisplayRows = self.rows - 2
            self.DisplayColumns = self.columns - 2
            self.window.attron(curses.color_pair(BorderColor))
            self.window.border()
            self.window.attroff(curses.color_pair(BorderColor))
            # self.window.refresh()
        else:
            self.CurrentRow = 0
            self.StartColumn = 0

    def ScrollPrint(self, PrintLine, Color=2, TimeStamp=False, BoldLine=True):
        current_time = datetime.now().strftime("%H:%M:%S")

        if TimeStamp:
            PrintLine = current_time + ": {}".format(PrintLine)

        PrintLine = PrintLine.expandtabs(4)
        PrintableString = PrintLine[0:self.DisplayColumns]
        RemainingString = PrintLine[self.DisplayColumns:]

        try:
            while len(PrintableString) > 0:
                PrintableString = PrintableString.ljust(self.DisplayColumns, ' ')
                self.window.attron(curses.color_pair(self.PreviousLineColor))
                self.window.addstr(self.PreviousLineRow, self.StartColumn, self.PreviousLineText)
                self.window.attroff(curses.color_pair(self.PreviousLineColor))

                if BoldLine:
                    self.window.attron(curses.color_pair(Color))
                    self.window.addstr(self.CurrentRow, self.StartColumn, PrintableString, curses.A_BOLD)
                    self.window.attroff(curses.color_pair(Color))
                else:
                    self.window.attron(curses.color_pair(Color))
                    self.window.addstr(self.CurrentRow, self.StartColumn, PrintableString)
                    self.window.attroff(curses.color_pair(Color))

                self.PreviousLineText = PrintableString
                self.PreviousLineColor = Color
                self.PreviousLineRow = self.CurrentRow
                self.CurrentRow = self.CurrentRow + 1

                PrintableString = RemainingString[0:self.DisplayColumns]
                RemainingString = RemainingString[self.DisplayColumns:]

            if self.CurrentRow > (self.DisplayRows):
                if self.ShowBorder == 'Y':
                    self.CurrentRow = 1
                else:
                    self.CurrentRow = 0

            # Do not refresh here
            # self.window.refresh()

        except Exception as ErrorMessage:
            TraceMessage = traceback.format_exc()
            AdditionalInfo = "PrintLine: {}".format(PrintLine)
            self.ErrorHandler(ErrorMessage, TraceMessage, AdditionalInfo)

    def DisplayTitle(self):
        try:
            Title = self.Title[0:self.DisplayColumns - 3]
            self.window.attron(curses.color_pair(self.TitleColor))
            if self.rows > 2:
                self.window.addstr(0, 2, Title)
            else:
                print("ERROR - You cannot display title on a window smaller than 3 rows")
            self.window.attroff(curses.color_pair(self.TitleColor))
            # self.window.refresh()

        except Exception as ErrorMessage:
            TraceMessage = traceback.format_exc()
            AdditionalInfo = "Title: " + Title
            self.ErrorHandler(ErrorMessage, TraceMessage, AdditionalInfo)

    def Clear(self):
        self.window.erase()
        self.window.attron(curses.color_pair(self.BorderColor))
        self.window.border()
        self.window.attroff(curses.color_pair(self.BorderColor))
        self.DisplayTitle()
        if self.ShowBorder == 'Y':
            self.CurrentRow = 1
            self.StartColumn = 1
        else:
            self.CurrentRow = 0
            self.StartColumn = 0

    def refresh(self):
        self.window.refresh()

    def ErrorHandler(self, ErrorMessage, TraceMessage, AdditionalInfo):
        print("ERROR - An error occurred in TextWindow class.")
        print(ErrorMessage)
        print("TRACE")
        print(TraceMessage)
        if AdditionalInfo:
            print("Additional info:", AdditionalInfo)

class TextPad(object):
    def __init__(self, name, rows, columns, y1, x1, y2, x2, ShowBorder, BorderColor):
        max_y, max_x = curses.LINES - 1, curses.COLS - 1
        self.rows = min(rows, max_y - y1)
        self.columns = min(columns, max_x - x1)

        if self.rows <= 0 or self.columns <= 0:
            raise ValueError("Pad size exceeds terminal size. Please expand your terminal.")
        
        self.name = name
        self.ypos = y1  # Position on the screen
        self.xpos = x1
        self.height = self.rows
        self.width = self.columns
        self.ShowBorder = ShowBorder
        self.BorderColor = BorderColor  # pre-defined text colors 1-7
        try:
            self.pad = curses.newpad(self.rows, self.columns)
        except curses.error:
            raise ValueError("Failed to create a new pad. Check if terminal size is sufficient.")
        self.PreviousLineColor = 2

    def PadPrint(self, PrintLine, Color=2, TimeStamp=False):
        # Print to the pad
        try:
            self.pad.idlok(1)
            self.pad.scrollok(1)

            current_time = datetime.now().strftime("%H:%M:%S")
            if TimeStamp:
                PrintLine = current_time + ": " + PrintLine

            # Expand tabs to X spaces
            PrintLine = PrintLine.expandtabs(4)
            # Pad the string with space then truncate
            PrintLine = PrintLine.ljust(self.columns, ' ')
            PrintLine = PrintLine[:self.columns - 1]  # Truncate to fit

            self.pad.attron(curses.color_pair(Color))
            self.pad.addstr(PrintLine + '\n')
            self.pad.attroff(curses.color_pair(Color))

            # Do not refresh here
            # self.refresh()

        except Exception as ErrorMessage:
            time.sleep(2)
            TraceMessage = traceback.format_exc()
            AdditionalInfo = "PrintLine: " + PrintLine
            self.ErrorHandler(ErrorMessage, TraceMessage, AdditionalInfo)

    def refresh(self):
        # Calculate the refresh area
        max_y, max_x = curses.LINES - 1, curses.COLS - 1
        pad_max_y, pad_max_x = self.ypos + self.height - 1, self.xpos + self.width - 1

        refresh_y1 = min(self.ypos, max_y)
        refresh_x1 = min(self.xpos, max_x)
        refresh_y2 = min(pad_max_y, max_y)
        refresh_x2 = min(pad_max_x, max_x)

        self.pad.refresh(
            0, 0,
            refresh_y1, refresh_x1,
            refresh_y2, refresh_x2
        )

    def Clear(self):
        try:
            self.pad.erase()
            self.refresh()
        except Exception as ErrorMessage:
            TraceMessage = traceback.format_exc()
            AdditionalInfo = "erasing textpad"
            self.ErrorHandler(ErrorMessage, TraceMessage, AdditionalInfo)

    def ErrorHandler(self, ErrorMessage, TraceMessage, AdditionalInfo):
        print("ERROR - An error occurred in TextPad class.")
        print(ErrorMessage)
        print("TRACE")
        print(TraceMessage)
        if AdditionalInfo:
            print("Additional info:", AdditionalInfo)

def ErrorHandler(ErrorMessage, TraceMessage, AdditionalInfo):
    # Generic error handler function
    CallingFunction = inspect.stack()[1][3]
    print("\n\n--------------------------------------------------------------")
    print("ERROR - Function ({} ) has encountered an error.".format(CallingFunction))
    print(ErrorMessage)
    print("\n\nTRACE")
    print(TraceMessage)
    if AdditionalInfo != "":
        print("\n\nAdditional info:", AdditionalInfo)
    print("\n\n--------------------------------------------------------------")
    time.sleep(1)
    sys.exit('Goodbye for now...')


def main(stdscr):
    # Initialization
    stdscr.clear()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)

    # Initialize colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)

    # Create TextWindow and TextPad
    window = TextWindow('ExampleWindow', 10, 40, 0, 0, 10, 40, 'Y', 2, 2)
    window.ScrollPrint("Hello, World!", Color=3, TimeStamp=True)

    pad = TextPad('ExamplePad', 100, 40, 12, 0, 20, 40, 'N', 2)
    pad.PadPrint("This is a long text to be printed in a pad.", Color=4, TimeStamp=True)
    pad.PadPrint("Another line in the pad to show scrolling capability.", Color=5, TimeStamp=True)

    # Refresh custom windows/pads
    window.refresh()
    pad.refresh()

    while True:
    
        # Handle other keys if necessary

        # Refresh custom windows/pads after handling input
        window.refresh()
        pad.refresh()

    # No manual cleanup needed with curses.wrapper()

# Start the curses application
curses.wrapper(main)
