# OpenDict
# Copyright (c) 2003 Martynas Jocius <mjoc@akl.lt>
# Copyright (c) 2003 Mantas Kriauciunas <mantas@akl.lt>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your opinion) any later version.
#
# This program is distributed in the hope that will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MECHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more detals.
#
# You shoud have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# 02111-1307 USA
#
# Module: plugin

from wxPython.wx import *
import os
import zipfile
import imp
import string

from info import home, uhome, __version__
from misc import numVersion, printError
from gui.pluginwin import PluginLicenseWindow
from gui.errorwin import errDialog

_ = wxGetTranslation

class Plugin:

   """Class object contains information about the plugin,
   it can load plugin's code for use."""

   def __init__(self, dir):
       self.dir = dir

       if os.path.exists(os.path.join(uhome, "plugins", self.dir, "DESC")):
          fd = open(os.path.join(uhome, "plugins", self.dir, "DESC"), "r")
       else:
          fd = open(os.path.join(home, "plugins", self.dir, "DESC"), "r")
       lines = fd.readlines()

       for line in lines:
          if line.find("name=") == 0:
             self.name = line.replace("name=", "").strip()
          elif line.find("code=") == 0:
             self.code = line.replace("code=", "").strip()
          elif line.find("version=") == 0:
             self.version = line.replace("version=", "").strip()
          elif line.find("opendict=") == 0:
             self.opendict = line.replace("opendict=", "").strip()
          elif line.find("author=") == 0:
             self.author = line.replace("author=", "").strip()
          elif line.find("about=") == 0:
             self.about = line.replace("about=", "")
             self.about += string.join(lines[lines.index(line)+1:], "")


   def load(self, window):
      if os.path.exists(os.path.join(uhome, "plugins", self.dir)):
         p = os.path.join(uhome, "plugins", self.dir)
         h = uhome
      else:
         h = home
         p = os.path.join(uhome, "plugins", self.dir)

      modName = self.code[:self.code.rfind(".")]
      version = sys.version[:3].replace(".", "")

      if os.path.exists(os.path.join(p, "%s_py%s.py" % (modName, version))) or\
      os.path.exists(os.path.join(p, "%s_py%s.pyc" % (modName, version))):
         print "Version-specified module found:", "%s_py%s" % (modName, version)
         modName = "%s_py%s" % (modName, version)

      print "Loading module '%s'..." % modName

      if modName in sys.modules:
         del sys.modules[modName]
      if not p in sys.path:
         sys.path.append(p)
      m = imp.load_module(modName, *imp.find_module(modName))
      return m.Dictionary(os.path.join(h, "plugins", self.dir),
                          window)
   


def checkPluginVersion(plugin):

   if numVersion(plugin.opendict) > numVersion(__version__):
      msg = _("Plugin %s %s requires OpenDict %s\n" \
              "or newer, but this is version %s. Try " \
              "getting the newest version of OpenDict.") \
              % (plugin.name, plugin.version,
                 plugin.opendict, __version__)
      dialog = wxMessageDialog(wxGetApp().window, msg, "Version Error",
                               wxOK | wxICON_ERROR)
      dialog.CenterOnScreen()
      dialog.ShowModal()
      dialog.Destroy()
      return 1

   return 0

def pluginPreinstall(config, path, zip):
   """This method does things that are needed before plugin can be installed
   Returns 0 if all things are OK (ex. user agree with license), else 1"""
   ok = 0

   iModName = None
   for file in zip.namelist():
      if file.find("__install") == 0:
         name = file[:file.rfind(".")]
         ext = file[file.rfind(".")+1:]
         if name.find("_py") > -1:
            num = name[name.find("_py"):].replace("_py", "")
            if num == sys.version[:3].replace(".", ""):
               iModName = name
         elif not iModName:
            iModName = name

   print "Custom Install module name:", iModName

   if iModName:
      ok = 1
      # Load install script
      # This script contains GUI window class for custom install process.

      # Py2exe does not support direct imports.
      # This seems not very pretty... Any ideas?
      version = sys.version[:3].replace(".", "")

      if os.name != "posix" or int(version) < 23:
         # We have Python <2.3 or MS Windows with py2exe here...

         print "Hmm, Python %s at %s" % (version, os.name)
         file = iModName + "." + ext
         code = zip.read(file)
         remove = 0
         if not uhome in sys.path:
            remove = 1
            sys.path.append(uhome)

         tmpfd = open(os.path.join(uhome, file), "wb")
         tmpfd.write(code)
         tmpfd.close()
         __install = imp.load_module(iModName, *imp.find_module(iModName))

         try:
            if ext != "pyc":
               os.remove(os.path.join(uhome, file))
               os.remove(os.path.join(uhome, file+"c"))
            else:
               os.remove(os.path.join(uhome, file))
            if remove:
               sys.path.remove(uhome)
         except:
            print "Warning: couldn't remove", file
            pass
            
      # Vey well, but only python >=2.3
      else:
         print "Ok, Python %s at %s" % (version, os.name) 
         sys.path.append(path)
         import __install

      if "license.txt" in zip.namelist():
         license = zip.read("license.txt")
      else:
         license = "No license"

      pluginInstallWin = __install.PluginInstallWindow(config.window,
                                                       uhome, path,
                                                       license)
      pluginInstallWin.CenterOnScreen()
      if pluginInstallWin.run() == wxID_OK:
         ok = 0
   elif "license.txt" in zip.namelist():
      # Show standard license agreement window with the given
      # license text.
      licenseWindow = PluginLicenseWindow(config.window, -1,
                                          _("License Agreement"),
                                          zip.read("license.txt"),
                                          size=(400, 350))
      licenseWindow.CenterOnScreen()
      if licenseWindow.ShowModal() == wxID_OK:
         ok = 0

      licenseWindow.Destroy()

   print "Preinstall: ", ok
   return ok

def installPlugin(config, path):
    """This method is used to unzip plugin zip files and add
    new plugin object into plugins dict"""

    plugname = ""
    errmsg = ""
    file = os.path.split(path)[1]
    dir = file.replace(".zip", "")

    try:
     zip = zipfile.ZipFile(path)
     if not zip.testzip():
       desc = zip.read("DESC")
       for line in desc.split("\n"):
         if line.find("name=") == 0:
            line = line.replace("name=", "").strip()

            if not config.plugins.has_key(line):

               if not pluginPreinstall(config, path, zip):
                  config.checkDir("plugins")
                  config.checkDir(os.path.join("plugins", dir))

                  for name in zip.namelist():
                     file = os.path.join(uhome, "plugins", dir, name)
                     fd = open(file, "wb")
                     fd.write(zip.read(name))
                     fd.close()

                  zip.close()

                  p = Plugin(dir)

                  if not checkPluginVersion(p):
                    if not config.plugins.has_key(p.name):
                       config.plugins[p.name] = p
                       config.ids[p.name] = config.plugMenuIds
                       config.plugMenuIds += 1

                       item = wxMenuItem(config.window.menuDict,
                                         config.ids[p.name],
                                         p.name)
                       EVT_MENU(config.window, config.ids[p.name],
                                config.window.onDefault)
                       # wxPython 2.4.1.2 has a bug, menu items with bitmaps
                       # do not catch events.
                       #if wx.__version__ != "2.4.1.2":
                       #   item.SetBitmap(wxBitmap(os.path.join(home, "pixmaps", "plugin.xpm"),
                       #                           wxBITMAP_TYPE_XPM))

                       config.window.menuDict.InsertItem(config.window.menuDict.GetMenuItemCount()-2, item)
                    else:
                       config.plugins[p.name] = p

                    config.window.SetStatusText(_("Installation complete"))
                    plugname = p.name

            else:
               errmsg = _("Plugin named \"%s\"\nis already installed. " \
                       "Remove old plugin first if\nyou want to " \
                       "install the newer version.") \
                       % line

     else:
        errmsg = _("Plugin file is corrupted")
    except:
	errmsg = _("Selected file is corrupted or not OpenDict plugin")
        printError()

    if plugname == "":
        config.window.SetStatusText(_("Installation aborted"))
	if errmsg != "":
	    #dialog = wxMessageDialog(config.window, errmsg, _("Installation Error"),
            #                         wxOK | wxICON_ERROR)
            errDialog(errmsg)
            #dialog.CenterOnScreen()
            #dialog.ShowModal()
            #dialog.Destroy()

    return plugname

def initPlugins(config):

   dirs = []
   if os.path.exists(os.path.join(uhome, "plugins")):
      dirs = [file for file in os.listdir(os.path.join(uhome, "plugins")) \
              if os.path.isdir(os.path.join(uhome, "plugins", file))]
   if os.path.exists(os.path.join(home, "plugins")):
      dirs.extend([file for file in os.listdir(os.path.join(home, "plugins"))\
              if os.path.isdir(os.path.join(home, "plugins", file))])
   print "Plugin Init: found plugins:", ", ".join(dirs)

   for dir in dirs:
      p = Plugin(dir)
      config.plugins[p.name] = p
      config.ids[p.name] = config.plugMenuIds
      config.plugMenuIds += 1

