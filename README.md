ps2gui
======

A GUI wrapper around a non cohesive web experience.  

How to get it to run:
=====================

The code is not designed to run on Windows.
If you really want it, fork and import os to get started.

Install the Python bindings for Qt. ( The package is called python-qt4 on Ubuntu )
Extract the zipped archive at a convenient location and run gui.py ( python gui.py ).

Provide the PS website username and password when prompted for. The credentials are used to update/fetch the PS station lists.
The cookiejar should expire at the end of the session.
Migration now works and new PS stations should update seamlessly without any loss of previously recorded notes/prefs.


Filled the prefs. What next?
============================

Press the export buttona and the app should write to a file in the home folder. ( file's called finalpreflist )
Now login to the PS2 website and navigate to the preference page. Wait for the page to load.
Do not press any keys. No tabs. *Nothing*.

With the page open, open up a terminal and run the fill_pref.sh ( bash fill_pref.sh , check for permissions 
The script should fill the prefs. Verify and submit.
)


There are quite a few(update:very few) known bugs but time is such a bitch. Only let me know if something goes **horribly** wrong.
Backups *don't* hurt. Look for the database file at this location : ~/.ps2gui.
Also tinkering with the code and changing directories is not a good idea ( unless, ofcourse, you know what you are doing )
You can optionally link the app_home to Dropbox and make sure the database follows you on all your devices.

I need a spell check for my terminal.

If the GUI does not load correctly and the app exits with an error about ICE default I/O error handler, delete the 
~/.ICEauthority file. 

Last but not the least, the software is provided as is and without **any** warranty/guarantee.
