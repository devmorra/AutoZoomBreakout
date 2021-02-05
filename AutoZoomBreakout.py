import time
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import random
import pyautogui
import webbrowser
from PIL import ImageGrab


class GroupsDisplayFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.canvas = tk.Canvas(self)
        self.cells = {}  # dictionary to hold the cells so they can be accessed at a later time to update their color or other things
        self.canvas.grid(row=0, column=0)


    # coordinate is column, row (x, y) origin top left
    def getCell(self, member):
        return self.cells[member]

    def cleanGroupDisplay(self):
        for cell, entry in self.cells.items():
            entry.grid_forget()
        self.cells = {}

    def makeCellGreen(self, member):
        self.cells[member].configure(readonlybackground="green")
        self.cells[member].update()
    def makeCellRed(self, member):
        self.cells[member].configure(readonlybackground="red")
        self.cells[member].update()
    def updateGroupsDisplay(self):
        if len(self.cells) != 0:
            self.cleanGroupDisplay()
        # Create the group number labels across the top
        # print(self.parent.groups)
        for i in range(len(self.parent.groups)):
            entry = tk.Entry(master=self.canvas, state="readonly", width=16)
            textVar = tk.StringVar(entry, f"Group {i + 1}")
            entry.configure(textvariable=textVar)
            self.cells[f"Group {i + 1}"] = entry
            entry.grid(column=i, row=0)

        groupNum = 1
        for group in self.parent.groups:
            membNum = 1
            for member in group:
                entry = tk.Entry(master=self.canvas, state="readonly", width=16)
                textVar = tk.StringVar(entry, member)
                self.cells[member] = entry
                entry.configure(textvariable=textVar)
                entry.grid(column=groupNum - 1, row=membNum)
                membNum += 1
            groupNum += 1

# class WheelDecideButton(tk.Button):
#     def __init__(self, parent, *args, **kwargs):
#         tk.Button.__init__(self, parent, *args, **kwargs)
#         self.parent = parent
#         self.buttonLabel = 'Open Wheel Decide'
#         self.wheelLink = ''
#     def generateLink(self):


class DialogFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.labelVar = tk.StringVar(self, "Thanks for using ZoomAutoBreakout! Please choose a file to load.")
        self.label = tk.Label(textvariable=self.labelVar, font="TkDefaultFont 12 bold")
        self.label.pack()

    def setDialog(self, dialog):
        self.labelVar.set(dialog)
        self.label.update()


class FileChoiceFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        groupGenFrame = ''
        self.groupNumSpinBox = ''  # these are set in setGroupGenFrame()
        self.parent = parent
        self.choiceLabelText = tk.StringVar(self, "")
        # Define labels and buttons to choose files to read leaders/participants
        fileChoiceLabel = tk.Label(master=self, textvariable=self.choiceLabelText, relief="sunken", width=40,
                                   wraplength=200)
        fileChoiceBtn = tk.Button(master=self, text="Choose file", relief="raised", command=self.chooseInputFile)
        # Label button
        # Label button
        fileChoiceLabel.grid(row=0, column=0)
        fileChoiceBtn.grid(row=0, column=1)

    # def setGroupGenFrame(self, frame):
    #     self.groupGenFrame = frame
    #     self.groupNumSpinBox = frame.groupNumSpinBox
    def setLeadAndParFromLines(self, fileLines):
        # fileLines = groupFile.readlines()
        if "[LEADERS]\n" not in fileLines:
            self.parent.setDialog("[LEADERS] block definition in file is missing, please add it. See readme.md for details.")
        elif "[PARTICIPANTS]\n" not in fileLines:
            self.parent.setDialog("[PARTICIPANTS] block definition in file is missing, please add it. See readme.md for details.")
        else:
            # remove empty lines - https://stackoverflow.com/questions/1157106/remove-all-occurrences-of-a-value-from-a-list
            # to do: understand how this works
            fileLines = list(filter(lambda a: a != "\n", fileLines))

            leadBlockStart = fileLines.index(
                "[LEADERS]\n") + 1  # lead block starts on the line below block definition
            leadBlockEnd = fileLines.index("[PARTICIPANTS]\n")  # and ends the line above the participants block
            partBlockStart = fileLines.index(
                "[PARTICIPANTS]\n") + 1  # starts line after participants block definition
            partBlockEnd = len(fileLines)  # ends on the last line of the file

            self.parent.leaders = fileLines[leadBlockStart:leadBlockEnd]
            self.parent.groupGenFrame.groupNumSpinBox.configure(from_=1, to=len(self.parent.leaders))  # ugly
            participants = fileLines[partBlockStart:partBlockEnd]
            # remove newline characters
            cleanLeaders = []
            for l in self.parent.leaders:
                if l[-1:] == "\n":
                    cleanLeaders.append(l[:-1])
                else:
                    cleanLeaders.append(l)
            cleanParticipants = []
            for p in participants:
                if p[-1:] == "\n":
                    cleanParticipants.append(p[:-1])
                else:
                    cleanParticipants.append(p)
            self.parent.leaders = cleanLeaders
            self.parent.participants = cleanParticipants
            # createGroups(leaders, participants, 0)

    def getGroupsFromPreDefLines(self, glines):
        self.parent.groups = []
        glines = glines[1:]  # cut off the [PREDEFINED]\n line
        for line in glines:
            names = line.split(",")
            # remove \n on every line but the last
            if glines.index(line) != len(glines) - 1:
                names[len(names) - 1] = names[len(names) - 1][:-1]
            self.parent.groups.append(names)

        # return groups

    def chooseInputFile(self):
        def isLeadParFile(fileLines):
            if "[LEADERS]\n" not in fileLines:
                return False
            elif "[PARTICIPANTS]\n" not in fileLines:
                return False
            else:
                return True

        def isPreDefFile(fileLines):
            return fileLines[0] == "[PREDEFINED]\n"

        inputFile = tk.filedialog.askopenfile(filetypes=[("Text files (.txt)", "*.txt")])

        if inputFile is not None:
            inputFileLines = inputFile.readlines()
            self.choiceLabelText.set(inputFile.name)
            if isLeadParFile(inputFileLines):
                self.parent.setDialog("Leader/Participant file detected. Please choose the number of groups to create.")
                self.parent.groupsDisplayFrame.cleanGroupDisplay()
                self.parent.groupGenFrame.enableButton()
                # set leaders and groups globally, make createGroups frame/button available
                self.setLeadAndParFromLines(inputFileLines)
                self.parent.disableAssignment()
            elif isPreDefFile(inputFileLines):
                self.parent.setDialog("Predefined groups file detected. You may now begin assignment.")
                # create the groups, populate the chart, make assign button available
                self.getGroupsFromPreDefLines(inputFileLines)
                self.parent.updateGroupsDisplay()
                # print(self.parent.groups)
                self.parent.groupGenFrame.disableButton()
                self.parent.enableAssignment()
                # print(groups)
            # maybe add else for invalid files, not sure how to determine

            # else:
            # make creategroups frame unavailable
            # make assign button unavailable


class GroupGenerationFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.groupNumSpinBox = ''
        # groupGenerationFrame.grid(row=0, column=0)
        # groupCreationFrame = tk.Frame(master=parent)
        self.groupNumSpinBox = tk.Spinbox(master=self)
        self.groupCreationBtn = tk.Button(master=self, text="Generate Groups",
                                          command=self.createGroupsFromLeadPar, state="disabled")
        self.groupNumSpinBox.grid(row=0, column=0)
        self.groupCreationBtn.grid(row=0, column=1)
        # groupCreationFrame.grid(row=1, column=0)

    def createGroupsFromLeadPar(self):
        participants = self.parent.participants
        leaders = self.parent.leaders
        groups = self.parent.groups
        random.shuffle(participants)
        random.shuffle(leaders)
        # numOfGroups = len(leaders) #temporary until the spinbox is hooked up
        numOfGroups = int(self.parent.groupGenFrame.groupNumSpinBox.get())  # ugly
        leads = leaders.copy()  # local variables used to pop from so the original variables are preserved
        parts = participants.copy()  # used for when generating groups multiple times from the same file, this one may not be used
        groups = []
        # creates numOfGroups groups from the scrambled leaders
        for x in range(numOfGroups):
            l = [leads.pop()]
            groups.append(l)

        # remaining leaders are put into the participant pool
        for remaining in range(len(leads)):
            parts.append(leads.pop())

        # participants are distributed evenly into groups
        i = 0
        for participant in parts:
            groups[i % numOfGroups].append(participant)
            i += 1
        self.parent.saveGroupsToFile("groups/lastgroups.txt")
        self.parent.groups = groups
        self.parent.updateGroupsDisplay()
        self.parent.setDialog("Groups created and saved as lastgroups.txt. Assignment is now available.")
        self.parent.saveGroupsToFile("groups/lastgroups.txt")
        self.parent.enableAssignment()
        # self.parent.setDialog(f"Groups: {groups}")

    def enableButton(self):
        self.groupCreationBtn.configure(state="normal")

    def disableButton(self):
        self.groupCreationBtn.configure(state="disabled")


# format and __init__ taken from https://stackoverflow.com/questions/17466561/best-way-to-structure-a-tkinter-application
class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.participants = ''
        self.leaders = ''
        self.groups = ''
        # Create subframes with parent of this main application frame
        self.dialogFrame = DialogFrame(self)
        self.dialogFrame.pack()
        self.fileChoiceFrame = FileChoiceFrame(self)
        self.fileChoiceFrame.pack()
        self.groupGenFrame = GroupGenerationFrame(self)
        self.groupGenFrame.pack()
        self.groupsDisplayFrame = GroupsDisplayFrame(self)
        self.groupsDisplayFrame.pack()
        self.assignGroupsButton = tk.Button(self, text="Assign Groups", state="disabled", command=self.assignGroups)
        self.assignGroupsButton.pack()
        self.wheelDecideButton = tk.Button(self, text="Open wheel decide", state="active", command=self.openWheelDecide)
        self.wheelDecideButton.pack()
        # self.fileChoiceFrame.setGroupGenFrame(self.groupGenFrame)

    def updateGroupsDisplay(self):
        self.groupsDisplayFrame.updateGroupsDisplay()

    def setDialog(self, dialog):
        self.dialogFrame.setDialog(dialog)

    def saveGroupsToFile(self, filePath):
        groups = self.groups
        gfile = open(filePath, "w")
        gfile.write("[PREDEFINED]\n")
        for i in range(len(groups)):
            for j in range(len(groups[i])):
                gfile.write(groups[i][j])
                if j < len(groups[i]) - 1:
                    gfile.write(",")
            if i < len(groups) - 1:
                gfile.write("\n")
        gfile.close()

    def enableAssignment(self):
        self.assignGroupsButton.configure(state="normal")
        self.wheelDecideButton.configure(state="normal")

    def disableAssignment(self):
        self.assignGroupsButton.configure(state="disabled")
        self.wheelDecideButton.configure(state="disabled")

    def assignGroups(self):
        def locateWindow():
            # searchVar.set("Searching...")
            # print("Scanning for Zoom Breakout Room window...")
            # attempts to find Zoom Breakout Room window, exits upon failure
            breakoutBox = pyautogui.locateOnScreen("images/breakout bar.png", grayscale=True)
            # print(f"First scan: {breakoutBox}")
            if (breakoutBox == None):
                breakoutBox = pyautogui.locateOnScreen("images/breakout bar 2.png", grayscale=True)
                # print(f"Second scan: {breakoutBox}")
                if (breakoutBox == None):
                    return None
                # else:
                # return True
            # else:
            # return True
            return breakoutBox

        def findSearchCoordinate():
            return pyautogui.locateCenterOnScreen("images/magnifying glass.png")

        def fromOriginX(x):
            return originX + x

        def fromOriginY(y):
            return originY + y

        def clickRel(x, y):
            # click a location relative to the origin of the window (top left = 0,0)
            pyautogui.moveTo(originX + x, originY + y, duration=0.05)
            pyautogui.click()

        def moveRel(x, y):
            # clickRel without the click
            pyautogui.moveTo(originX + x, originY + y, duration=0.05)

        def type(string):
            pyautogui.typewrite(string, interval=0)
        self.setDialog("Searching for Zoom window...")
        pyautogui.PAUSE = .025
        pyautogui.FAILSAFE = True
        breakoutBox = locateWindow()
        if breakoutBox is None:
            self.setDialog("Zoom window not found. Please make sure it is visible.")
            return
        self.setDialog("Assigning members, please do not touch the mouse.")
        groups = self.groups
        # unassignedParticipants = {}
        # for g in groups:
        #     for p in g:
        #         unassignedParticipants[p] = f"Group {groups.index(g) + 1}"
                # unassignedParticipants.append([p, f"Group {groups.index(g) + 1}"])
        # print(f"initial unassigned: {unassignedParticipants}")
        originX = breakoutBox[0]
        originY = breakoutBox[1]
        # assignment button for first breakout room
        assignX = 427
        assignY = 47
        assignGap = 30
        windowWidth = 448
        # name search bar for assignees
        searchX = 510
        searchY = 30
        searchYOffset = 60
        searchGap = 30
        # checkmark boxes for assignees, gap between them, and color of checked box
        # 469, 53 value on test execution, discrepancy of -7, -3
        # old values 476, 57 -> try 483, 60
        checkX = 476  # edge of checkbox, 468 is center value
        checkY = 57  # centered
        checkGap = 24  # this and RGB used for participants with multiple devices
        checkedRGB = (14, 114, 235)
        checkBorderRGB = (144, 144, 150)
        white = (255, 255, 255)
        dropdownX = 21
        dropdownY = 49
        # dropdownGap = assignGap
        clearX = 626
        clearY = 27
        pixelCheckX = 475
        pixelCheckY = 55
        mGlassLocRegion = (originX + windowWidth + 20, originY, originX + windowWidth + 40, originY + 400)
        # move mouse to window origin
        # pyautogui.moveTo(originX, originY, duration=0.25)

        currentGroup = 0
        for group in groups:
            clickRel(assignX, assignY + currentGroup * assignGap)
            # small delay added because locate function below was inconsistent
            time.sleep(0.1)
            for participant in group:
                # move mouse to breakout room assign button and click
                # locate the search bar in case it has moved, adjust click position accordingly
                try:
                    searchLoc = pyautogui.locateCenterOnScreen("images/magnifying glass.png", region=mGlassLocRegion)
                    searchX = searchLoc[0] - originX
                    searchY = searchLoc[1] - originY
                    checkY = searchY + 28
                    clearY = searchY
                    pixelCheckY = searchY + 28
                except:
                    # stop assigning because the search bar is gone
                    break
                # adjust searchY to relative position
                # adjust checkbox, clear, pixcheck values based off new searchY value

                # print(searchY)
                clickRel(searchX, searchY)
                # (participant)
                type(participant)
                # check the checkbox pixels, if it's not white, click it. Make note that the participant was added
                # if it is white and the participant was not added, add them to a not found participants list
                # multiCheck is incremented to move down the checkbox list in case of a participant having multiple devices
                multiCheck = 0
                added = False
                while True:
                    # Imagegrab more compatible with more python versions. pyautogui.pixel causes exceptions sometimes
                    pixCheck = ImageGrab.grab().getpixel((originX + pixelCheckX, originY + pixelCheckY + multiCheck * checkGap))
                    # pixCheck = pyautogui.pixel(originX + pixelCheckX, originY + pixelCheckY + multiCheck * checkGap)
                    if pixCheck == checkBorderRGB:  # if there's a checkbox border, click on it
                        clickRel(checkX, checkY + multiCheck * checkGap)
                        self.groupsDisplayFrame.makeCellGreen(participant)
                        # if multiCheck == 0:
                        #     del unassignedParticipants[participant]
                        added = True
                        multiCheck += 1
                    else:
                        break
                        # if the pixel check failed, the participant either wasn't there
                        # or already added or the assign button was missed

                if added == False:
                    self.groupsDisplayFrame.makeCellRed(participant)
                    # index = unassignedParticipants.index([participant])
                    # unassignedParticipants[index].append(f", Group {multiCheck + 1}")

                # pixCheck = pyautogui.pixelMatchesColor(originX + pixelCheckX, originY + pixelCheckY, checkedRGB)
                # print(pixCheck)
                # if added == False:
                # print(f"{participant} unable to be assigned, check if they are absent or incorrectly named")
                # participantsNotAssigned.append((participant, f"Room {currentGroup + 1}"))
                clickRel(clearX, clearY)
                # pyautogui.press('backspace', presses=20, interval=0.01)
            clickRel(dropdownX, dropdownY + currentGroup * assignGap)
            currentGroup += 1
        #self.disableAssignment()
        #print(f"Not assigned: {unassignedParticipants}")
        self.setDialog("Assignment complete. Please assign any remaining members manually.")

    def openWheelDecide(self):
        count = 1
        baseUrl = "https://wheeldecide.com/index.php?c1="
        urlSuffix = "&t=Wheel+Decide%21&time=5&remove=1"
        fullUrl = baseUrl
        for group in self.groups:
            if count > 1:
                fullUrl += f"&c{count}="
            for member in group:
                fullUrl += f"{member}, "
            fullUrl = fullUrl[:-2] #chop off the extra ", "
            count += 1
        fullUrl = fullUrl.replace(",", "%2C")
        fullUrl = fullUrl.replace(" ", "+")
        fullUrl += urlSuffix
        webbrowser.open(fullUrl)




root = tk.Tk()
root.title("ZoomAutoBreakout")
MainApplication(root).pack(side="top", fill="both", expand=True)
root.mainloop()
