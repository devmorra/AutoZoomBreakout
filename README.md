# AutoZoomBreakout

Prerequisites - Python 3, pyautogui, Windows 10(?)

If needed, run 'pip install pyautogui' in your terminal to install the module

Currently only tested on the Windows 10 default theme and text scaling.

Start by going to breakout rooms, set the number of groups, and assign manually. The window must be visible for the program to find it, and on the primary monitor. Creates groups based off of a designated text file. Set the number of groups and click Generate Groups. See example groups.txt for an example. Names in the files must match the zoom participants. If multiple participants match the name designated in the file, all will be added to the group at the same time to account for multiple devices. The program stops once the search bar goes away, you'll have to manually assign from there on (tends to apply to the last group). Participants who were in the groups but were failed to be assigned will be highlighted in red.

![Example](/images/example.png)
