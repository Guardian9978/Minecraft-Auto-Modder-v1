#default python libraries
import os, sys, urllib2, urllib, zipfile, time, traceback, shutil, curses
from subprocess import Popen

#3rd party python libraries
#import MySQLdb

if os.name in ("nt","dos"):
    import win32api

def printlines(TEXT):
    sys.stdout.write(TEXT+"\n")
    #sys.stdout.flush()

def myReportHook(count, blockSize, totalSize):
    percent = int(count * blockSize * 100 / totalSize)
    if os.name in ("nt","dos"):
        stdscr.addstr(2, 0, " ")
        stdscr.addstr(2, 0, "Downloading: %d%% Complete" %(round(percent)))
        stdscr.refresh()
    else:
        printlines("Downloading: %d%% Complete" %(round(percent)))

def prog():
    current_folder=os.path.dirname(os.path.abspath(__file__))
    done=0
    gotver=0
    if os.name in ("nt","dos"):
        fname1="Launcher.exe"
        fname2="Launcher.exe"
    else:
        fname1="launcher.py"
        fname2="launcher.pytmp"
        fname3="gui_xrc.py"
        fname4="gui_xrc.pytmp"
    url="http://gmod.zapto.org/minecraft/"+fname2
    url2="http://gmod.zapto.org/minecraft/programversion.txt"
    if os.path.isfile(current_folder+"/info.cfg"):
        f=open(current_folder+"/info.cfg","r")
        lines=f.readlines()
        f.close()
        version=0
        for p,line in enumerate(lines):
            line=line.replace("\r\n","")
            line=line.replace("\n","")
            lines[p]=line
            if "=" in line:
                split1=line.split("=")
                name=split1[0]
                value=split1[1]
                if name=="version" and not "mc" in line:
                    version=value
                    gotver=1
        if gotver==1:
            req = urllib2.Request(url2)
            response = urllib2.urlopen(req)
            lst1=[]
            for p,r in enumerate(response):
                r=r.replace("\r\n","")
                r=r.replace("\n","")
                lst1.append(r)
                if "=" in r:
                    split1=r.split("=")
                    name=split1[0]
                    value=split1[1]
                    if p == 0:
                        if os.name in ("nt","dos"):
                            stdscr.addstr(0, 0, "Checking Launcher version.")
                        else:
                            printlines("Checking Launcher version.")
                    if "version=" in r:
                        if not value == version:
                            if os.name in ("nt","dos"):
                                stdscr.addstr(1, 0, "Launcher is outdated. Updating...")
                                stdscr.refresh()
                            else:
                                printlines("Launcher is outdated. Updating...")
                            fail=True
                            while fail:
                                try:
                                    if os.path.isfile(current_folder+"/"+fname1):
                                        os.remove(current_folder+"/"+fname1)
                                    fail=False
                                except:
                                    if os.name in ("nt","dos"):
                                        stdscr.addstr(3, 0, "Waiting for launcher to close.")
                                    else:
                                        printlines("Waiting for launcher to close.")
                            downloadedFile = urllib.urlretrieve(url,fname1,myReportHook)
                            if not os.name in ("nt","dos"):
                                url="http://gmod.zapto.org/minecraft/"+fname4
                                downloadedFile = urllib.urlretrieve(url,fname3,myReportHook)
                            for p,l in enumerate(lines):
                                if "version=" in l and not "mc" in l:
                                    lines[p]="version="+str(value)
                            done=1
                            stdscr.addstr(1, 0, "Launcher is outdated. Updating... Done")
                            stdscr.refresh()
                        else:
                            if os.name in ("nt","dos"):
                                stdscr.addstr(2, 0, "Launcher is Up to Date.")
                            else:
                                printlines("Launcher is Up to Date.")
            f=open(current_folder+"/info.cfg","w")
            f.write("\n".join(lines))
            f.close()
        if done==0:
            printlines("Launcher is Up to Date.")
    else:
        if not os.path.isfile(current_folder+"/"+fname1):
            downloadedFile = urllib.urlretrieve(url,fname1,myReportHook)
            forceupdate=0
        else:
            if os.name in ("nt","dos"):
                stdscr.addstr(0, 0, "No info.cfg found.  Donwloading newest launcher version...")
                stdscr.refresh()
            else:
                printlines("No info.cfg found.  Donwloading newest launcher version...")
            if os.path.isfile(current_folder+"/"+fname1):
                os.remove(current_folder+"/"+fname1)
            downloadedFile = urllib.urlretrieve(url,fname1,myReportHook)
            if os.name in ("nt","dos"):
                stdscr.addstr(0, 0, "No info.cfg found.  Donwloading newest launcher version... Done")
                stdscr.refresh()
            else:
                printlines("No info.cfg found.  Donwloading newest launcher version... Done")
    dot="Autostarting Launcher"
    for i in range(0,5):
        dot+=". "
        stdscr.addstr(4, 0, dot)
        stdscr.refresh()
    #if os.name in ("nt","dos"):
    DETACHED_PROCESS = 0x00000008
    curses.endwin()
    if os.name in ("nt","dos"):
        cmd = '"'+current_folder+'/'+fname1+'"'
    else:
        cmd = ['python2',current_folder+'/'+fname1]
    Popen(cmd,shell=False,stdin=None,stdout=None,stderr=None,close_fds=True,creationflags=DETACHED_PROCESS)
try:
    stdscr = curses.initscr()
    curses.start_color()
    curses.curs_set(0)
    prog()
except:
    printlines("Trigger Exception, traceback info forward to log file.")
    if os.path.isfile("Updater-errlog.txt"):
        os.remove("Updater-errlog.txt")
    traceback.print_exc(file=open("Updater-errlog.txt","a"))