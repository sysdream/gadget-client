#!/usr/bin/env python
"""
Gadget interactive shell

Provices interactive access to Gadget and Fino primitives
for remote inspection of Android applications.
The shell has autocompletion abilities for easy browsing
inside the remote memory.
"""

import sys
import os
import gadget
import traceback
import readline

def completer(base, state):
    """
    Autocompletion utility
    """
    if "." in base:
        split = base.rfind(".")
        options = map(lambda x: base[:split+1] + x, filter(
            lambda x: x.startswith(base[split+1:]) and not x.startswith("_"),
            dir(eval(base[:split]))))
    else:
        options = filter(
            lambda x: x.startswith(base),
            globals().keys())
    return options[state] if state < len(options) else None

# check for correct usage
if len(sys.argv) < 3:
    print "Usage: %s host port [package]" % sys.argv[0]
    sys.exit(2)

# get the remote endpoint address
remote = (sys.argv[1], int(sys.argv[2]))

# list the available packages if necessary
if len(sys.argv) < 4:
    print "Available packages: " + ",".join(
        gadget.proto.list_applications(remote))
    sys.exit(0)

# get the package name
package = sys.argv[3]

try:
    app = gadget.proto.Application(remote, package)
except Exception as e:
    print "Could not connect to the remote application"
    traceback.print_exc()
    sys.exit(1)

# set some variables
R = app.R

# launch the shell
os.system('clear')
print """\033[29m
   ___________                     ______
  |            | |..          |  .~      ~.
  |______      | |  ``..      | |          |
  |            | |      ``..  | |          |
  |            | |          ``|  `.______.'
  \033[0m
  Fino  Copyright (C) 2012 Sysdream
  This program comes with ABSOLUTELY NO WARRANTY.
  This is free software, and you are welcome to redistribute it
  under certain conditions, for details see COPYING.

  Built-ins:
  app    -- the current application
  gadget -- the main gadget package
  R      -- the standard resource namespace

  """
os.environ['PYTHONINSPECT'] = 'True'
readline.parse_and_bind("tab: complete")
readline.set_completer(completer)
