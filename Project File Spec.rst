==========================================
GunShotMatch Project File Specification
==========================================

Tape Archive file containing the following files and directories:

info.json
^^^^^^^^^^^^^

JSON-formatted file containing information about the Project, with the following structure:


Name
------

The name of the Project

User
------
The user who created the Project

Device
-------------

The device that created the Project

Date Created
---------------

The date and time the Project was created, as a datetime.datetime timestamp

Date Modified
----------------
The date and time the Project was last modified, as a datetime.datetime timestamp

Description
--------------
A description of the Project

Version
----------

File format version in semver format

Method
................
The name of the file containing the Method used to create the Project

Experiments
-----------------

List of dictionaries containing the Experiments

Each entry contains the following keys:

Name
........

The name of the Experiment

Filename
...........
The name of the Experiment file

Description
...............
A description of the Experiment

User
......
The user who created the Experiment

Device
.........
The device that created the Project

Version
.........
File format version in semver format

Date Created
...............
The date and time the Experiment was created, as a datetime.datetime timestamp

Date Modified
................
The date and time the Experiment was last modified, as a datetime.datetime timestamp

Original Filename
..................

The filename of the file the Experiment was created from

Original Filetype
...................

The filetype of the file the Experiment was created from

Method
................
The name of the file containing the Method used to create the Experiment


