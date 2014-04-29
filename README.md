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

There are quite a few known bugs but time is such a bitch. Only let me know if something goes **horribly** wrong.
