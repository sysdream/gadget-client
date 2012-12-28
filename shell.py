#!/usr/bin/env python

import sys
import os
import gadget
import traceback
import rlcompleter
import readline

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

os.system('clear')
print """
   ___________                     ______
  |            | |..          |  .~      ~.
  |______      | |  ``..      | |          |
  |            | |      ``..  | |          |
  |            | |          ``|  `.______.'

  Fino  Copyright (C) 2012 Sysdream
  This program comes with ABSOLUTELY NO WARRANTY.
  This is free software, and you are welcome to redistribute it
  under certain conditions, for details see COPYING.

  Built-ins:
  app    -- the current application
  gadget -- the main gadget package

  """
sys.ps1 = "\033[31m>>> \033[0m"
os.environ['PYTHONINSPECT'] = 'True'
readline.parse_and_bind("tab: complete")
