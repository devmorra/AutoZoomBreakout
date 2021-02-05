# AutoZoomBreakout

This is a tool intended to ease the adding of participants to breakout rooms, assigned based off of text files. It is intended to prevent creating imbalanced groups by ensuring that each group has a team leader which is either a volunteer or has been identified as strong in the current topic - though random assignment is still possible.

Prerequisites - Python 3, pyautogui, Windows 10(?)

If needed, run 'pip install pyautogui' in your terminal to install the module. If you don't have python or pip installed, get it [here](https://www.python.org/downloads/release/python-391/) and make sure you install pip during the installation.

Currently only tested on the Windows 10 default theme and text scaling. You may be able to make it work on your system by providing alternative images in the images folder for the program to recognize the Zoom window and buttons with, if you are precise.

1. Start by going to breakout rooms, set the number of groups, and assign manually. This prepares the breakout rooms.
2. Click "Choose File", and choose a group file to work with, see example groups.txt for an example of the format. If you want fully random groups, place everyone under [LEADERS] 
3. Set the number of groups and click "Generate Groups". See example groups.txt for an example. Names in the files must match the zoom participants. If multiple participants match the name designated in the file, all will be added to the group at the same time to account for multiple devices. 
4. Ensure that the Zoom breakout rooms window is visible and on your primary monitor.
5. Click "Assign Groups" and do not move your mouse - the program will take control temporarily.
6. The program stops once the search bar goes away, you'll have to manually assign from there on (tends to apply to the last group). Participants who were in the groups but were failed to be assigned will be highlighted in red (either they're absent or changed their Zoom name). Leftovers who weren't assigned will not be highlighted.
7. The most recently generated group will be saved to the groups folder as lastgroups.txt for convenience. It uses an alternative format that is used for predefined groups.

![Example](/images/example.png)
