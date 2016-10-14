from gui_xrc import *
import os, stat
import urllib
import urllib2
import sys
import threading
import wx
import shutil
import zipfile
import traceback
import time
from subprocess import Popen
from datetime import date
from wx.lib.embeddedimage import PyEmbeddedImage

##
#MINECRAFT CLIENT DOWNLOAD LINK
##
#
#http://assets.minecraft.net/1_4_2/minecraft.jar
#
##

def log_box(text):
    global log_tc
    if os.name == "nt":
        log_tc.AppendText(text)
    else:
        print text,

def myReportHook( count, blockSize, totalSize):
    global download_gge
    percent = int(count * blockSize * 100 / totalSize)
    download_gge.SetValue(percent)

responses = {
    100: ('Continue', 'Request received, please continue'),
    101: ('Switching Protocols',
          'Switching to new protocol; obey Upgrade header'),

    200: ('OK', 'Request fulfilled, document follows'),
    201: ('Created', 'Document created, URL follows'),
    202: ('Accepted',
          'Request accepted, processing continues off-line'),
    203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
    204: ('No Content', 'Request fulfilled, nothing follows'),
    205: ('Reset Content', 'Clear input form for further input.'),
    206: ('Partial Content', 'Partial content follows.'),

    300: ('Multiple Choices',
          'Object has several resources -- see URI list'),
    301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
    302: ('Found', 'Object moved temporarily -- see URI list'),
    303: ('See Other', 'Object moved -- see Method and URL list'),
    304: ('Not Modified',
          'Document has not changed since given time'),
    305: ('Use Proxy',
          'You must use proxy specified in Location to access this '
          'resource.'),
    307: ('Temporary Redirect',
          'Object moved temporarily -- see URI list'),

    400: ('Bad Request',
          'Bad request syntax or unsupported method'),
    401: ('Unauthorized',
          'No permission -- see authorization schemes'),
    402: ('Payment Required',
          'No payment -- see charging schemes'),
    403: ('Forbidden',
          'Request forbidden -- authorization will not help'),
    404: ('Not Found', 'Nothing matches the given URI'),
    405: ('Method Not Allowed',
          'Specified method is invalid for this server.'),
    406: ('Not Acceptable', 'URI not available in preferred format.'),
    407: ('Proxy Authentication Required', 'You must authenticate with '
          'this proxy before proceeding.'),
    408: ('Request Timeout', 'Request timed out; try again later.'),
    409: ('Conflict', 'Request conflict.'),
    410: ('Gone',
          'URI no longer exists and has been permanently removed.'),
    411: ('Length Required', 'Client must specify Content-Length.'),
    412: ('Precondition Failed', 'Precondition in headers is false.'),
    413: ('Request Entity Too Large', 'Entity is too large.'),
    414: ('Request-URI Too Long', 'URI is too long.'),
    415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
    416: ('Requested Range Not Satisfiable',
          'Cannot satisfy request range.'),
    417: ('Expectation Failed',
          'Expect condition could not be satisfied.'),

    500: ('Internal Server Error', 'Server got itself in trouble'),
    501: ('Not Implemented',
          'Server does not support this operation'),
    502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
    503: ('Service Unavailable',
          'The server cannot process the request due to a high load'),
    504: ('Gateway Timeout',
          'The gateway server did not receive a timely response'),
    505: ('HTTP Version Not Supported', 'Cannot fulfill request.'),
    }

class CHECK_UPDATE(threading.Thread):
    def create_file_list(self,dir_name):
        fileList = []
        for file in os.listdir(dir_name):
            dirfile = os.path.join(dir_name, file)
            if os.path.isfile(dirfile):
                fileList.append(dirfile)
            elif os.path.isdir(dirfile):
                fileList.extend(self.create_file_list(dirfile))
        return fileList
    
    def check_jarmods(self):
        if os.path.isfile(current_folder+"/jar_info.cfg"):
            #here we open the existing jar_info.cfg
            #read its lines and close its file
            #we also set rebuildjar to 0 untill certain
            #conditions are met.
            #and we start to build the install list
            f=open(current_folder+"/jar_info.cfg")
            lines=f.readlines()
            f.close()
            rebuildjar=0
            instlist=rjarlist[:]
            
            #checking for outdated jar mods
            log_box("Checking for outdated jar mods:\n")
            for rjname in rjarlist:
                #if rjname=="PlayerAPI":
                #    pr=1
                #else:
                #    pr=0
                for line in lines:
                    line=line.replace("\r\n","")
                    line=line.replace("\n","")
                    if "=" in line:
                        name,lversion=line.split("=")
                        if rjname==name:
                            log_box("  Checking "+rjname+" (Version: "+lversion+"): ")
                            url="http://gmod.zapto.org/minecraft/mods/"+rmcversion+"/client/"+name+"/info.txt"
                            req = urllib2.Request(url)
                            response = urllib2.urlopen(req)
                            for r in response:
                                r=r.replace("\r\n","")
                                r=r.replace("\n","")
                                if "[version]" in r:
                                    skip=1
                                    ver=1
                                if skip==0:
                                    if ver==1:
                                        ver=0
                                        if not r == lversion:
                                            log_box("Outdated\n")
                                            rebuildjar=1
                                        else:
                                            log_box("Up to Date\n")
                                skip=0
            #checking for outdated optional jar mods
            log_box("\nChecking for outdated optional jar mods:\n")
            for line in lines:
                line=line.replace("\r\n","")
                line=line.replace("\n","")
                if "=" in line:
                    name,lversion=line.split("=")
                    if name in rojarlist:
                        log_box("  Checking "+name+" (Version: "+lversion+"): ")
                        url="http://gmod.zapto.org/minecraft/mods/"+rmcversion+"/client/"+name+"/info.txt"
                        req = urllib2.Request(url)
                        response = urllib2.urlopen(req)
                        for r in response:
                            r=r.replace("\r\n","")
                            r=r.replace("\n","")
                            if "[version]" in r:
                                skip=1
                                ver=1
                            if skip==0:
                                if ver==1:
                                    ver=0
                                    if not r == lversion:
                                        log_box("Outdated\n")
                                        rebuildjar=1
                                    else:
                                        log_box("Up to Date\n")
                            skip=0
            #checking for new jar mods
            rebuild1=0
            log_box("\nChecking for new jar mods:")
            for rj in rjarlist:
                found=0
                for line in lines:
                    line=line.replace("\r\n","")
                    line=line.replace("\n","")
                    if "=" in line:
                        name,version=line.split("=")
                        if rj == name:
                            found=1
                if found==0:
                    log_box("\n  Found: "+rj+"\n")
                    rebuildjar=rebuild1=1
            if rebuild1==0:
                log_box(" None Found")
            
            #checking for new optional jar mods
            rebuild2=0
            log_box("\nChecking for new optional jar mods:")
            for so in seloptional:
                if so in rojarlist:
                    found=0
                    for line in lines:
                        line=line.replace("\r\n","")
                        line=line.replace("\n","")
                        if "=" in line:
                            name,version=line.split("=")
                            if so == name:
                                found=1
                    if found==0:
                        log_box("\n  Found: "+so+"\n")
                        rebuildjar=rebuild2=1
            if rebuild2==0:
                log_box(" None Found")
            
            #checking for removed jar mods
            rebuild3=0
            log_box("\nChecking for removed jar mods:")
            for line in lines:
                remove=0
                line=line.replace("\r\n","")
                line=line.replace("\n","")
                if "=" in line:
                    name,lversion=line.split("=")
                    if not name in rojarlist:
                        if not name in rjarlist:
                            remove=1
                if remove==1:
                    log_box("\n  Removing: "+name+"\n")
                    rebuildjar=rebuild3=1
            if rebuild3==0:
                log_box(" None Found")
            
            #checking for removed optional jar mods
            rebuild4=0
            log_box("\nChecking for removed optional jar mods:")
            for line in lines:
                remove=0
                line=line.replace("\r\n","")
                line=line.replace("\n","")
                if "=" in line:
                    name,lversion=line.split("=")
                    if name in rojarlist:
                        if not name in seloptional:
                            remove=1
                    if remove==1:
                        log_box("\n  Removing: "+name+"\n")
                        rebuildjar=rebuild4=1
            if rebuild4==0:
                log_box(" None Found\n")
            log_box("\n")
            #incase we need to rebuild the jar
            #were adding the selected optional
            #jar mods to the install list
            for so in seloptional:
                if so in rojarlist:
                    instlist.append(so)
            
            #and we create the string that we want to send to the webpage
            lst="|".join(instlist)
            
            return rebuildjar,lst
        else:
            instlist=[]
            rebuildjar=1
            log_box("File Missing: jar_info.cfg\nInstalling fresh jar with mods.\n\n")
            for name in rjarlist:
                instlist.append(name)
                url="http://gmod.zapto.org/minecraft/mods/"+rmcversion+"/client/"+name+"/info.txt"
                req = urllib2.Request(url)
                response = urllib2.urlopen(req)
                for r in response:
                    r=r.replace("\r\n","")
                    r=r.replace("\n","")
                    if "[version]" in r:
                        skip=1
                        ver=1
                    if skip==0:
                        if ver==1:
                            ver=0
                            version=r
                    skip=0
            
            for name in seloptional:
                if not name in romodslist:
                    instlist.append(name)
                    url="http://gmod.zapto.org/minecraft/mods/"+rmcversion+"/client/"+name+"/info.txt"
                    req = urllib2.Request(url)
                    response = urllib2.urlopen(req)
                    version=""
                    for r in response:
                        r=r.replace("\r\n","")
                        r=r.replace("\n","")
                        if "[version]" in r:
                            skip=1
                            ver=1
                        if skip==0:
                            if ver==1:
                                ver=0
                                version=r
                        skip=0
        lst="|".join(instlist)
        return rebuildjar,lst
    
    def check_mods(self, temp4):
        if len(temp4) > 0:
            lines=temp4[:]
            
            instlist=[]
            instoplist=[]
            uplist=[]
            upoplist=[]
            remlist=[]
            remoplist=[]
            
            # check for mod updates
            log_box("\nChecking for outdated mods:\n")
            info=0
            gotver=0
            for l in lines:
                lversion=""
                if l == "": continue
                if l[0]=="/" and l[1]=="/": continue
                if l[0]=="#": continue
                if "[" in l and "]\n" in l:
                    name=l.split("[")[1].split("]")[0]
                if "{" in l:
                    info=1
                    skip=1
                if "}" in l:
                    info=0
                if info==1:
                    if skip==0:
                        if "version=" in l:
                            lversion=l.split("=")[1].replace("\n","")
                            gotver=1
                if gotver==1:
                    gotver=0
                    url="http://gmod.zapto.org/minecraft/mods/"+rmcversion+"/client/"+name+"/info.txt"
                    req = urllib2.Request(url)
                    fail=1
                    try:
                        response = urllib2.urlopen(req)
                        fail=0
                    except urllib.error.URLError, e:
                        f=open("./URLerror.txt","w")
                        f.write(str(e.reason[0])+": "+ e.reason[1])
                        f.close()
                        sys._exit()
                    except urllib.error.HTTPError, e:
                        f=open("./HTTPerror.txt","w")
                        f.write(str(e.code)+": "+responses[e.code][1])
                        f.close()
                        sys._exit()
                    if fail==0:
                        version=""
                        for r in response:
                            r=r.replace("\r\n","")
                            r=r.replace("\n","")
                            if "[version]" in r:
                                ver=1
                                skip=1
                            if skip==0:
                                if ver==1:
                                    ver=0
                                    version=r
                                    if not version == lversion:
                                        if not r in rojarlist:
                                            if not r in romodslist:
                                                log_box("  Checking Mod \""+name+"\" (Version: "+lversion+"): Out of Date\n")
                                                uplist.append(name)
                                            else:
                                                log_box("  Checking Optional Mod \""+name+"\" (Version: "+lversion+"): Out of Date\n")
                                                upoplist.append(name)
                                    else:
                                        if not r in rojarlist:
                                            log_box("  Checking Mod \""+name+"\" (Version: "+lversion+"): Up to Date\n")
                                        else:
                                            log_box("  Checking Optional Mod \""+name+"\" (Version: "+lversion+"): Up to Date\n")
                            skip=0
                skip=0
            
            combined=rmodslist[:]
            combined.extend(seloptional)
            #check for new mods
            log_box("\nChecking for new mods:")
            num=0
            for lname in combined:
                if not lname in rojarlist:
                    found=0
                    for l in lines:
                        if l == "": continue
                        if l[0]=="/" and l[0]=="/": continue
                        if l[0]=="#": continue
                        if "[" in l and "]\n" in l:
                            name=l.split("[")[1].split("]")[0]
                            if lname==name:
                                found=1
                    if found == 0:
                        num+=1
                        if not r in romodslist:
                            instlist.append(lname)
                            log_box("\n  New Mod Found: "+lname)
                        else:
                            instoplist.append(lname)
                            log_box("\n  New Optional Mod Found: "+lname)
            if num==0:
                log_box(" None Found\n")
            else:
                log_box("\n")
            
            #check for removed mods
            log_box("\nChecking for removed mods:")
            num=0
            for l in lines:
                remove=1
                info=0
                if l == "": continue
                if l[0]=="/" and l[1]=="/": continue
                if l[0]=="#": continue
                if "[" in l and "]\n" in l:
                    
                    lname=l.split("[")[1].split("]")[0]
                    if not lname in rojarlist:
                        for name in combined:
                            if lname==name:
                                remove=0
                    else:
                        remove=0
                else:
                    remove=0
                if remove == 1:
                    if not lname in rojarlist:
                        if not lname in romodslist:
                            remlist.append(lname)
                            num+=1
                        else:
                            remoplist.append(lname)
                            num+=1
            if num==0:
                log_box(" None Found\n")
            else:
                log_box("\n")
        else:
            remlist=[]
            remoplist=[]
            uplist=[]
            upoplist=[]
            instlist=rmodslist[:]
            instoplist=[]
            for so in seloptional:
                if not so in rojarlist:
                    instoplist.append(so)
        return uplist,upoplist,instlist,instoplist,remlist,remoplist
    
    def requestjar(self, lst):
        log_box("Rebuilding Jar:\n")
        log_box("  Downloading Jar: ")
        url="http://gmod.zapto.org/minecraft/get_mods2.py?mods="+lst+"&version="+rmcversion+"&jar=1"
        log_box(url+"\n")
        try:
            downloadedFile = urllib.urlretrieve(url,current_folder+"/minecraftjar.zip",myReportHook)
        except urllib.error.URLError, e:
            f=open("./URLerror.txt","w")
            f.write(url+"\n")
            f.write(str(e.reason[0])+": "+ e.reason[1])
            f.close()
            wx.MessageBox("Failed to download New Jar.\nCheck URLerror.txt\n\nProgram will now exit.(Hopefully)","Error")
            sys._exit()
        except urllib.error.HTTPError, e:
            f=open("./HTTPerror.txt","w")
            f.write(url+"\n")
            f.write(str(e.code)+": "+responses[e.code][1])
            f.close()
            wx.MessageBox("Failed to download New Jar.\nCheck HTTPerror.txt\n\nProgram will now exit.(Hopefully)","Error")
            sys._exit()
        time.sleep(.5)
        log_box("Done\n")
        log_box("Moving Jar to .minecraft/bin folder: ")
        zipf=zipfile.ZipFile(current_folder+"/minecraftjar.zip","r")
        zipf.extractall(current_folder+"/temp")
        zipf.close()
        if os.path.isfile(current_folder+"/minecraftjar.zip"):
            os.remove(current_folder+"/minecraftjar.zip")
        if os.path.isfile(current_folder+"/jar_info.cfg"):
            os.remove(current_folder+"/jar_info.cfg")
        shutil.copyfile(current_folder+"/temp/jar_info.cfg", current_folder+"/jar_info.cfg")
        if os.path.isfile(current_folder+"/temp/jar_info.cfg"):
            os.remove(current_folder+"/temp/jar_info.cfg")
        root_src_dir = current_folder+"/temp"
        for src_dir, dirs, files in os.walk(root_src_dir):
            dst_dir = src_dir.replace(root_src_dir, mcfolder)
            if not os.path.exists(dst_dir):
                os.mkdir(dst_dir)
            for file_ in files:
                src_file = os.path.join(src_dir, file_)
                dst_file = os.path.join(dst_dir, file_)
                if os.path.exists(dst_file):
                    os.remove(dst_file)
                shutil.move(src_file, dst_dir)
        shutil.rmtree(current_folder+"/temp")
        os.mkdir(current_folder+"/temp")
        log_box("Done\n")
    
    def instmod(self, zfile, name, temp4):
        log_box("  Extracting Mod: ")
        zipf=zipfile.ZipFile(zfile,"r")
        zipf.extractall(current_folder+"/temp/"+name)
        zipf.close()
        os.remove(zfile)
        log_box("Done\n")
        
        #parsing mod info.txt
        f=open(current_folder+"/temp/"+name+"/info.txt")
        lines=f.readlines()
        f.close()
        ex=cp=vr=0
        temp1=[]
        temp2=[]
        for line in lines:
            line=line.replace("\r\n","")
            line=line.replace("\n","")
            
            skip=0
            if line[0]=="[" and line[-1]=="]":
                key=line.split("[")[1].split("]")[0]
                skip=1
            
            if skip==0:
                if key=="version":
                    temp4.append("  version="+line+"\n")
                if key=="extract":
                    temp1.append(line)
                if key=="copy":
                    temp2.append(line)
        
        #extracting files as needed
        for t1 in temp1:
            if "*.zip" in t1:
                f_list=os.listdir(current_folder+"/temp/"+name)
                for f in f_list:
                    if ".zip" in f:
                        folders=[]
                        files=[]
                        z=zipfile.ZipFile(current_folder+"/temp/"+name+"/"+f)
                        for f2 in z.namelist():
                            if f2.endswith('/'):
                                if not os.path.isdir(mcfolder+"/"+f2):
                                    if not f2 in folders:
                                        os.makedirs(mcfolder+"/"+f2)
                                        folders.append(f2)
                            else:
                                files.append(f2)
                        z.extractall(mcfolder)
                        z.close()
                        #print "\n".join(files),
                        #print "\n-----\n",
                        #print "\n".join(folders)
                        for fil in files:
                            temp4.append("  CP="+mcfolder+"/"+fil+"\n")
                        for fol in folders:
                            temp4.append("  CP="+mcfolder+"/"+fol+"\n")
            else:
                z=zipfile.ZipFile(current_folder+"/temp/"+name+"/"+t1)
                for f2 in z.namelist():
                    if f2.endswith('/'):
                        if not os.path.isdir(mcfolder+"/"+f2):
                            if not f2 in folders:
                                os.makedirs(mcfolder+"/"+f2)
                                folders.append(f2)
                    else:
                        files.append(f2)
                z.close()
                #print "\n".join(files),
                #print "\n-----\n",
                #print "\n".join(folders)
                for fil in files:
                    temp4.append("  CP="+mcfolder+"/"+fil+"\n")
                for fol in folders:
                    temp4.append("  CP="+mcfolder+"/"+fol+"\n")
                z.extractall(mcfolder)
                z.close()
        
        #copying files as needed
        for t2 in temp2:
            ff,dest=t2.split("|")
            
            if dest=="/": dest=""
            
            if "*.zip" in t2:
                for item in os.listdir(current_folder+"/temp/"+name):
                    if ".zip" in item:
                        if fresh==1:
                            if os.path.isfile(mcfolder+dest+"/"+item):
                                os.remove(mcfolder+dest+"/"+item)
                        shutil.copyfile(current_folder+"/temp/"+name+"/"+item,mcfolder+dest+"/"+item)
                        temp4.append("  CP="+mcfolder+dest+"/"+item+"\n")
            elif "*.jar" in t2:
                for item in os.listdir(current_folder+"/temp/"+name):
                    if ".jar" in item:
                        if fresh==1:
                            if os.path.isfile(mcfolder+dest+"/"+item):
                                os.remove(mcfolder+dest+"/"+item)
                        shutil.copyfile(current_folder+"/temp/"+name+"/"+item,mcfolder+dest+"/"+item)
                        temp4.append("  CP="+mcfolder+dest+"/"+item+"\n")
            else:
                if os.path.isfile(current_folder+"/temp/"+name+"/"+ff):
                    if fresh==1:
                        if os.path.isfile(mcfolder+dest+"/"+ff):
                            os.remove(mcfolder+dest+"/"+ff)
                    shutil.copyfile(current_folder+"/temp/"+name+"/"+ff,mcfolder+dest+"/"+ff)
                    temp4.append("  CP="+mcfolder+dest+"/"+ff+"\n")
                else:
                    if ff=="config":
                        for fff in os.listdir(current_folder+"/temp/"+name+"/config"):
                            if fresh==1:
                                if os.path.isfile(mcfolder+dest+"/"+fff):
                                    os.remove(mcfolder+dest+"/"+fff)
                            if os.path.isfile(current_folder+"/temp/"+name+"/config/"+fff):
                                shutil.copyfile(current_folder+"/temp/"+name+"/config/"+fff,mcfolder+dest+"/"+fff)
                            else:
                                if os.path.isdir(mcfolder+dest) and not mcfolder+dest == mcfolder+"/" and not mcfolder+dest == mcfolder and not mcfolder+dest == mcfolder+"/mods" and not mcfolder+dest == mcfolder+"/config":
                                    shutil.rmtree(mcfolder+dest)
                                shutil.copytree(current_folder+"/temp/"+name+"/config/"+fff,mcfolder+dest)
                            temp4.append("  CP="+mcfolder+dest+"/"+fff+"\n")
                    else:
                        if fresh==1:
                            if os.path.isdir(mcfolder+dest) and not mcfolder+dest == mcfolder+"/" and not mcfolder+dest == mcfolder:
                                shutil.rmtree(mcfolder+dest)
                        shutil.copytree(current_folder+"/temp/"+name+"/"+ff,mcfolder+dest)
                        temp4.append("  CP="+mcfolder+dest+"\n")
        return temp4
    
    def remove_old_files(self, name, temp4):
        found=0
        for p,t in enumerate(temp4):
            if name in t and found==0:
                start=p
                found=1
            if found==1:
                if "}" in t:
                    stop=p
                    break
        for i in temp4[start:stop+1]:
            if "CP=" in i:
                pth=i.split("=")[1].replace("\n","")
                pth=pth.replace("\r\n","")
                
                if os.path.isdir(pth):
                    log_box("  Removing Old Folder: "+pth.replace(mcfolder,"")+"\n")
                    shutil.rmtree(pth)
                if os.path.isfile(pth):
                    log_box("  Removing Old File: "+pth.replace(mcfolder,"")+"\n")
                    os.remove(pth)
        del temp4[start:stop+1]
        return temp4
        
    def up_in_rm(self, uplist, upolist, instlist, instolist, remlist, remolist, temp4):
        #installing mods
        for il in instlist:
            log_box("\nInstalling Mod: "+il+"\n")
            log_box("  Downloading Mod: ")
            download_gge.SetValue(0)
            temp4.append("["+il+"]\n{\n")
            url="http://gmod.zapto.org/minecraft/get_mods2.py?mods="+il+"&version="+rmcversion
            downloadedFile = urllib.urlretrieve(url,current_folder+"/temp/"+il+".zip",myReportHook)
            log_box("Done\n")
            temp4=(self.instmod(downloadedFile[0],il,temp4))
            temp4.append("}\n")
        
        #installing optional mods
        for il in instolist:
            log_box("\nInstalling Optional Mod: "+il+"\n")
            log_box("  Downloading Mod: ")
            download_gge.SetValue(0)
            temp4.append("["+il+"]\n{\n")
            url="http://gmod.zapto.org/minecraft/get_mods2.py?mods="+il+"&version="+rmcversion
            downloadedFile = urllib.urlretrieve(url,current_folder+"/temp/"+il+".zip",myReportHook)
            log_box("Done\n")
            temp4=(self.instmod(downloadedFile[0],il,temp4))
            temp4.append("}\n")
        
        #updating mods:
        for ul in uplist:
            log_box("\nUpdating Mod: "+ul+"\n")
            log_box("  Downloading Mod: ")
            download_gge.SetValue(0)
            url="http://gmod.zapto.org/minecraft/get_mods2.py?mods="+ul+"&version="+rmcversion
            downloadedFile = urllib.urlretrieve(url,current_folder+"/temp/"+ul+".zip",myReportHook)
            log_box("Done\n")
            temp4=self.remove_old_files(ul,temp4)
            temp4.append("["+ul+"]\n{\n")
            temp4=(self.instmod(downloadedFile[0],ul,temp4))
            temp4.append("}\n")
        
        #updating optional mods:
        for ul in upolist:
            log_box("\nUpdating Optional Mod: "+ul+"\n")
            log_box("  Downloading Mod: ")
            download_gge.SetValue(0)
            url="http://gmod.zapto.org/minecraft/get_mods2.py?mods="+il+"&version="+rmcversion
            downloadedFile = urllib.urlretrieve(url,current_folder+"/temp/"+il+".zip",myReportHook)
            log_box("Done\n")
            temp4=self.remove_old_files(ul,temp4)
            temp4.append("["+il+"]\n{\n")
            temp4=(self.instmod(downloadedFile[0],ul,temp4))
            temp4.append("}\n")
        
        #removing mods
        for rl in remlist:
            log_box("\nRemoving Mod: "+rl)
            temp4=self.remove_old_files(rl,temp4)
            log_box(" - Done\n")
        
        #removing optional mods
        for rl in remolist:
            log_box("\nRemoving Optional Mod: "+rl+"\n")
            temp4=self.remove_old_files(rl,temp4)
            log_box(" - Done\n")
        
        self.save_mods_info(temp4)
    
    def run(self):
        global mcfolder, up_btn, pl_btn, forceup_btn, running
        
        log_box("Using server: "+selserveraddr+"\n\n")
        
        mcfolder=mc_folder_tc.GetValue()
        rebuildjar,lst=self.check_jarmods()
        
        if rebuildjar:
            self.requestjar(lst)
        else:
            log_box("No changes needed for minecraft.jar\n")
        
        temp4=[]
        info=self.load_mods_info_file()
        uplist,upolist,instlist,instolist,remlist,remolist=self.check_mods(info)
        if len(uplist)>0 or len(upolist)>0 or len(instlist)>0 or len(instolist)>0 or len(remlist)>0 or len(remolist)>0:
            self.up_in_rm(uplist,upolist,instlist,instolist,remlist,remolist,info)
        shutil.rmtree(current_folder+"/temp")
        log_box("\nRemoved temp folder.\n")
        log_box("--------------------\n")
        #log_tc.AppendText("Done Everything Minecraft Should Autostart.\n")
        #self.launchgame()
        log=log_tc.GetValue()
        f=open(current_folder+"/log.txt","w")
        f.write(log)
        f.close()
        play_btn.Enable(True)
        forceup_btn.Enable(True)
        running=0
        #os._exit(1)
    
    def load_mods_info_file(self):
        info=[]
        if os.path.isfile(current_folder+"/mods_info.cfg"):
            f=open(current_folder+"/mods_info.cfg","r")
            info=f.readlines()
            f.close()
        return info
    
    def save_mods_info(self,temp4):
        global current_folder
        if os.path.isfile(current_folder+"/mods_info.cfg"):
            os.remove(current_folder+"/mods_info.cfg")
        f=open(current_folder+"/mods_info.cfg","w")
        for t in temp4:
            f.write(t)
        f.close()

class App(wx.App):
    def OnInit(self):
        global log_tc, mc_folder_tc, mc_exe_tc, up_btn, play_btn, forceup_btn, version, mcversion, current_folder
        global infolines, gamestarted, seloptional, download_gge, running, selserveraddr
        self.res = get_resources()
        
        ##Frame 1
        self.frame = self.res.LoadFrame(None, 'frame')
        
        self.panel = xrc.XRCCTRL(self.frame, 'panel')
        self.mc_folder_tc = xrc.XRCCTRL(self.frame, 'mc_folder_tc')
        self.mc_exe_tc = xrc.XRCCTRL(self.frame, 'mc_exe_tc')
        self.log_tc = xrc.XRCCTRL(self.frame, 'log_tc')
        self.up_btn = xrc.XRCCTRL(self.frame, 'up_btn')
        self.forceup_btn = xrc.XRCCTRL(self.frame, 'forceup_btn')
        self.play_btn = xrc.XRCCTRL(self.frame, 'play_btn')
        self.optionalmods = xrc.XRCCTRL(self.frame, 'optional_chboxlst')
        self.download_gge = xrc.XRCCTRL(self.frame, 'download_gge')
        self.server_sel = xrc.XRCCTRL(self.frame, 'server_sel_cb')
        self.exe_label = xrc.XRCCTRL(self.frame, 'mc_exe_lbl')
        self.statusbar = xrc.XRCCTRL(self.frame, 'statusbar')
        self.frame.Bind(wx.EVT_BUTTON, self.OnUP, id=xrc.XRCID('up_btn'))
        self.frame.Bind(wx.EVT_BUTTON, self.OnForceUP, id=xrc.XRCID('forceup_btn'))
        self.frame.Bind(wx.EVT_BUTTON, self.OnPlayBtn, id=xrc.XRCID('play_btn'))
        self.frame.Bind(wx.EVT_BUTTON, self.OnBrowse1, id=xrc.XRCID('mc_browse_btn'))
        self.frame.Bind(wx.EVT_BUTTON, self.OnBrowse2, id=xrc.XRCID('mc_browseexe_btn'))
        self.frame.Bind(wx.EVT_BUTTON, self.OnExit, id=xrc.XRCID('exit_btn'))
        self.frame.Bind(wx.EVT_CHECKLISTBOX, self.OnCheck, id=xrc.XRCID('optional_chboxlst'))
        self.frame.Bind(wx.EVT_COMBOBOX, self.OnCBSelect, id=xrc.XRCID('server_sel_cb'))
        
        #server_sel=self.server_sel
        optionalmods=self.optionalmods
        log_tc=self.log_tc
        mc_folder_tc=self.mc_folder_tc
        mc_exe_tc=self.mc_exe_tc
        up_btn=self.up_btn
        forceup_btn=self.forceup_btn
        play_btn=self.play_btn
        download_gge = self.download_gge
        self.download_gge.SetRange(100)
        
        if os.name in ("nt","dos"):
            newLabel="Minecraft.exe File Location:"
        else:
            newLabel="Minecraft Jar File Location:"
        self.exe_label.SetLabel(newLabel)
        self.current_folder=os.path.dirname(os.path.abspath(__file__))
        current_folder=self.current_folder
        self.mcversion=""
        self.version="1"
        self.mcexe=""
        self.folder=""
        self.running=0
        running=self.running
        self.up_btn.Enable(False)
        self.forceup_btn.Enable(False)
        self.play_btn.Enable(False)
        self.init_frame()
        self.cfg_existed=0
        gamestarted=0
        infolines=[]
        self.check_for_info_file()
        error=self.get_remote_info_file()
        if error==0:
            for roj in rojarlist:
                self.optionalmods.Append(roj)
            for rom in romodslist:
                self.optionalmods.Append(rom)
            itms=len(rojarlist) + len(romodslist)
            self.checklistbox_defaults()
            self.check_updater_version()
            self.check_program_version()
            self.check_paths()
            version=self.version
            mcversion=self.mcversion
        return True
    
    def OnCBSelect(self,evt):
        global selserveraddr
        selserveraddr=self.server_sel.GetStringSelection()
        error=self.get_remote_info_file()
        if error==0:
            self.optionalmods.Clear()
            for roj in rojarlist:
                self.optionalmods.Append(roj)
            for rom in romodslist:
                self.optionalmods.Append(rom)
            self.checklistbox_defaults()
            self.up_btn.Enable(True)
            self.forceup_btn.Enable(True)
            self.check_paths()
        else:
            self.up_btn.Enable(False)
            self.forceup_btn.Enable(False)
            self.play_btn.Enable(True)
    
    def check_paths(self):
        self.log_tc.Clear()
        self.up_btn.Enable(False)
        self.forceup_btn.Enable(False)
        self.play_btn.Enable(False)
        if os.name in ("nt","dos"):
            ext="exe"
        else:
            ext="py"
        if os.path.isdir(self.folder):
            log_box("Valid Minecraft folder path loaded.\n")
        else:
            log_box("Minecraft folder NOT selected.\n")
        if os.path.isfile(self.mcexe):
            log_box("Valid Minecraft."+ext+" file path loaded.\n")
        else:
            log_box("Minecraft."+ext+" file NOT selected.\n")
        
        if os.path.isdir(self.folder) and os.path.isfile(self.mcexe):
            self.up_btn.Enable(True)
            self.forceup_btn.Enable(True)
            self.play_btn.Enable(True)
            log_box("\nClick Update to begin.\n\n")
        else:
            log_box("\n")
            
            if not os.path.isdir(self.folder) and os.path.isfile(self.mcexe):
                log_box("Please set your minecraft."+ext+" file path.\n")
            elif os.path.isdir(self.folder) and not os.path.isfile(self.mcexe):
                log_box("Please set your minecraft folder path.\n")
            else:
                log_box("Please use the browse buttons above.\n")
    
    def check_updater_version(self):
        global selserveraddr
        global download_gge
        url="http://gmod.zapto.org/minecraft/updaterversion.txt"
        req = urllib2.Request(url)
        try:
            error=0
            response = urllib2.urlopen(req)
        except :
            wx.MessageBox("Failed to connect to: Gmod.zapto.org\nSkipping Updater Version Check.\n\n","Error")
            self.statusbar.SetStatusText("Updater Version: "+self.upversion, 0)
            error=1
        if error==0:
            for r in response:
                r=r.replace("\r\n","")
                r=r.replace("\n","")
                if "version=" in r:
                    upversion=r.split("=")[1]
                if not self.upversion == upversion:
                    log_box("\nUpdater is outdated.\nUpdating... ")
                    if os.name in ("nt","dos"):
                        fname1="Updater.exe"
                        fname2="Updater.exe"
                    else:
                        fname1="updater.pytmp"
                        fname2="updater.py"
                    if os.path.isfile(current_folder+"/"+fname1):
                        os.remove(current_folder+"/"+fname1)
                    url="http://gmod.zapto.org/minecraft/"+fname1
                    download_gge.SetValue(0)
                    downloadedFile = urllib.urlretrieve(url,current_folder+"/"+fname2,myReportHook)
                    time.sleep(.5)
                    log_box("Done\n")
                    self.statusbar.SetStatusText("Updater Version: "+upversion, 0)
                    self.upversion=upversion
                    self.save_cfg()
                else:
                    self.statusbar.SetStatusText("Updater Version: "+self.upversion, 0)
    
    def check_program_version(self):
        global selserveraddr
        url="http://gmod.zapto.org/minecraft/programversion.txt"
        req = urllib2.Request(url)
        try:
            error=0
            response = urllib2.urlopen(req)
        except:
            wx.MessageBox("Failed to connect to: Gmod.zapto.org\nSkipping Launcher Update Check.\n\n","Error")
            self.statusbar.SetStatusText("Launcher Version: "+self.version, 1)
            error=1
        if error==0:
            for r in response:
                r=r.replace("\r\n","")
                r=r.replace("\n","")
                if "version=" in r:
                    rpversion=r.split("=")[1]
                if not self.version == rpversion:
                    wx.MessageBox("Program is out of date.\nRunning updater.")
                    if os.name in ("nt","dos"):
                        cmd='"'+self.current_folder+'/Updater.exe"'
                    else:
                        cmd=['python2',self.current_folder,'/updater.py']
                    #from asynproc import Process
                    #Process(cmd)
                    
                    DETACHED_PROCESS = 0x00000008
                    Popen(cmd,shell=False,stdin=None,stdout=None,stderr=None,close_fds=True,creationflags=DETACHED_PROCESS)
                    os._exit(1)
                else:
                    self.statusbar.SetStatusText("Launcher Version: "+self.version, 1)
    
    def checklistbox_defaults(self):
        global seloptional
        combined=rojarlist[:]
        combined.extend(romodslist)
        for p,name in enumerate(combined):
            for om in self.optionalmds:
                if name == om:
                    self.optionalmods.Check(p,True)
                    seloptional.append(name)
    
    def OnCheck(self,evt):
        global seloptional
        seloptional=self.optionalmods.GetCheckedStrings()
    
    def save_selections(self):
        f=open(current_folder+"/optionalmods.txt","w")
        f.write("\n".join(seloptional))
        f.close()
    
    def get_remote_info_file(self):
        global rmodslist,rjarlist,romodslist,rojarlist,rmcversion,rpversion
        url="http://"+selserveraddr+"/minecraft/info2.txt"
        req = urllib2.Request(url)
        try:
            stop=0
            response = urllib2.urlopen(req)
            error=0
        except:
            wx.MessageBox("Unable to access remote info file.\nServer: "+selserveraddr+"\n\nPlease select another server.","Error")
            self.forceup_btn.Enable(False)
            self.up_btn.Enable(False)
            self.play_btn.Enable(False)
            error=1
        if error==0:
            rmodslist=[]
            rjarlist=[]
            romodslist=[]
            rojarlist=[]
            rmcversion=""
            rpversion=""
            skip=0
            for r in response:
                r=r.replace("\r\n","")
                r=r.replace("\n","")
                if "version" in r:
                    if "mc" in r:
                        jar=0
                        mods=0
                        ojar=0
                        omods=0
                        rmcversion=r.split("=")[1]
                    else:
                        skip=1
                if "[jar]" in r:
                    jar=1
                    mods=0
                    ojar=0
                    omods=0
                    skip=1
                if "[mods]" in r:
                    jar=0
                    mods=1
                    ojar=0
                    omods=0
                    skip=1
                if "[optional-jar]" in r:
                    jar=0
                    mods=0
                    ojar=1
                    omods=0
                    skip=1
                if "[optional-mods]" in r:
                    jar=0
                    mods=0
                    ojar=0
                    omods=1
                    skip=1
                if skip==0:
                    if jar==1:
                        rjarlist.append(r)
                    if mods==1:
                        rmodslist.append(r)
                    if ojar==1:
                        rojarlist.append(r)
                    if omods==1:
                        romodslist.append(r)
                skip=0
        return error
    
    def check_for_info_file(self):
        global infolines, seloptional, selserveraddr, rmcversion, rpversion
        seloptional=[]
        #self.log_tc.Clear()
        if os.path.isfile(self.current_folder+"/info.cfg"):
            f=open(self.current_folder+"/info.cfg")
            infolines=f.readlines()
            f.close()
            mcver=0
            ver=0
            mcp=0
            mce=0
            mods=0
            skip=0
            error=0
            for l in infolines:
                if not l =="" and not l == "\n" and not l == "\r\n" and not "\\\\" in l:
                    l=l.replace("\n\r","")
                    l=l.replace("\n","")
                    if "version=" in l:
                        if "mc" in l:
                            upv=0
                            mcver=1
                            ver=0
                            mce=0
                            mcp=0
                            om=0
                            ls=0
                            ss=0
                        elif "up" in l:
                            upv=1
                            mcver=0
                            ver=0
                            mce=0
                            mcp=0
                            om=0
                            ls=0
                            ss=0
                        else:
                            upv=0
                            mcver=0
                            ver=1
                            mce=0
                            mcp=0
                            om=0
                            ls=0
                            ss=0
                    if "mcexe=" in l:
                        mcver=0
                        ver=0
                        mce=1
                        mcp=0
                        om=0
                        ls=0
                        ss=0
                        upv=0
                    if "mcpath=" in l:
                        mcver=0
                        ver=0
                        mce=0
                        mcp=1
                        om=0
                        ls=0
                        ss=0
                        upv=0
                    if "optionalmods=" in l:
                        mcver=0
                        ver=0
                        mce=0
                        mcp=0
                        om=1
                        ls=0
                        ss=0
                        upv=0
                    if "lastserver=" in l:
                        mcver=0
                        ver=0
                        mce=0
                        mcp=0
                        om=0
                        ls=1
                        ss=0
                        upv=0
                    if "servers=" in l:
                        mcver=0
                        ver=0
                        mce=0
                        mcp=0
                        om=0
                        ls=0
                        ss=1
                        upv=0
                    s=l.split("=")
                    name,value=s
                    if mcver==1:
                        url="http://Gmod.zapto.org/minecraft/info2.txt"
                        req = urllib2.Request(url)
                        try:
                            response = urllib2.urlopen(req)
                            for r in response:
                                r=r.replace("\r\n","")
                                r=r.replace("\n","")
                                if "mcversion=" in r:
                                    self.mcversion=r.split("=")[1]
                        except:
                            self.mcversion=value
                    if ver==1:
                        self.version=value
                    if mce==1:
                        if os.path.isfile(value):
                            self.mc_exe_tc.SetValue(value)
                            self.mcexe=value
                    elif mcp==1:
                        if os.path.isdir(value):
                            self.mc_folder_tc.SetValue(value)
                            self.folder=value
                    if om==1:
                        if not value=="":
                            if "|" in value:
                                self.optionalmds=value.split("|")
                            else:
                                self.optionalmds=[value]
                        else:
                            self.optionalmds=[]
                    
                    if ls==1:
                        if not value == "":
                            self.lastserver=value
                            selserveraddr=value
                            self.server_sel.SetValue(value)
                        else:
                            self.lastserver="Gmod.zapto.org"
                            selserveraddr=self.lastserver
                            self.server_sel.SetValue(self.lastserver)
                    if ss==1:
                        if not value == "":
                            if "|" in value:
                                for v in value.split("|"):
                                    self.server_sel.Append(v)
                            else:
                                self.server_sel.Append(value)
                        else:
                            self.server_sel.Append("Gmod.zapto.org")
                    if upv==1:
                        if not value == "":
                            self.upversion=value
            self.cfg_existed=1
            self.save_cfg()
        else:
            if os.name in ("nt","dos"):
                from win32com.shell import shellcon, shell
                mcpath=shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
            else:
                mcpath=""
            self.optionalmods.Clear()
            self.lastserver="Gmod.zapto.org"
            selserveraddr=self.lastserver
            self.upversion=1
            url="http://Gmod.zapto.org/minecraft/info2.txt"
            req = urllib2.Request(url)
            try:
                error=0
                response = urllib2.urlopen(req)
            except urllib.error.URLError, e:
                f=open("./URLerror.txt","w")
                f.write(url+"\n")
                f.write(str(e.reason[0])+": "+ e.reason[1])
                f.close()
            except urllib.error.HTTPError, e:
                f=open("./HTTPerror.txt","w")
                f.write(url+"\n")
                f.write(str(e.code)+": "+responses[e.code][1])
                f.close()
            except:
                wx.MessageBox("Failed to get current version.","Error")
                error=1
            if error==0:
                for r in response:
                    r=r.replace("\r\n","")
                    r=r.replace("\n","")
                    if "mcversion=" in r:
                        rmcversion=r.split("=")[1]
            url="http://Gmod.zapto.org/minecraft/programversion.txt"
            req = urllib2.Request(url)
            try:
                error=0
                response = urllib2.urlopen(req)
            except urllib.error.URLError, e:
                f=open("./URLerror.txt","w")
                f.write(url+"\n")
                f.write(str(e.reason[0])+": "+ e.reason[1])
                f.close()
            except urllib.error.HTTPError, e:
                f=open("./HTTPerror.txt","w")
                f.write(url+"\n")
                f.write(str(e.code)+": "+responses[e.code][1])
                f.close()
            except:
                wx.MessageBox("Failed to get current launcher version.","Error")
                error=1
            if error==0:
                for r in response:
                    r=r.replace("\r\n","")
                    r=r.replace("\n","")
                    if "version=" in r:
                        rpversion=r.split("=")[1]
                        
            self.servers=["Gmod.zapto.org"]
            self.optionalmds=[]
            if os.path.isdir(mcpath+"/.minecraft") and os.path.isdir(mcpath+"/.minecraft/bin"):
                self.mc_folder_tc.SetValue(mcpath+"/.minecraft")
                self.folder=mcpath+"/.minecraft"
                self.save_cfg()
                log_box("Minecraft folder Auto-Detected.\n\n")
                #log_box("Please use the browse buttons above.")
                self.check_for_info_file()
            else:
                log_box("Minecraft folder NOT selected.\n\n")
    
    def init_frame(self):
        size = (640,480)
        self.frame.SetSize(size)
        self.frame.Center()
        
        if not os.path.isdir(self.current_folder+"/temp"):
            os.mkdir(self.current_folder+"/temp")
        self.frame.Show(True)
    
    def save_cfg(self):
        global selserveraddr
        if os.path.isfile(self.current_folder+"/info.cfg"):
            f=open(self.current_folder+"/info.cfg","r")
            lines=f.readlines()
            f.close()
            for p,l in enumerate(lines):
                if not l =="" and not l == "\n" and not l == "\r\n*" and not "\\\\" in l:
                    if "version=" in l:
                        if "mc" in l:
                            lines[p]="mcversion="+self.mcversion+"\n"
                        elif "up" in l:
                            lines[p]="upversion="+self.upversion+"\n"
                        else:
                            lines[p]="version="+self.version+"\n"
                    if "mcexe=" in l:
                        lines[p]="mcexe="+self.mcexe+"\n"
                    if "mcpath=" in l:
                        lines[p]="mcpath="+self.folder+"\n"
                    if "optionalmods=" in l:
                        lines[p]="optionalmods="+"|".join(self.optionalmds)+"\n"
                    if "lastserver="in l:
                        lines[p]="lastserver="+selserveraddr+"\n"
                    if "servers=" in l:
                        tmp=[]
                        for i in range(self.server_sel.GetCount()):
                            tmp.append(self.server_sel.GetString(i))
                        lines[p]="servers="+"|".join(tmp)+"\n"
            
            cfgsettings=["optionalmods","lastserver","servers","upversion"]
            for n in cfgsettings:
                cnt=0
                for l in lines:
                    if n+"=" in l: cnt=1
                if n=="optionalmods" and cnt==0:
                    if os.path.isfile(current_folder+"/optionalmods.txt"):
                        f=open(current_folder+"/optionalmods.txt","r")
                        omds=f.read()
                        f.close()
                        if "\r\n" in omds:
                            omds=omds.split("\r\n")
                        elif "\n" in omds:
                            omds=omds.split("\n")
                        else:
                            omds=[omds]
                        if omds[-1] == "":
                            del omds[-1]
                        lines.append("optionalmods="+"|".join(omds)+"\n")
                        self.optionalmds=omds
                        os.remove(current_folder+"/optionalmods.txt")
                    else:
                        lines.append("optionalmods=\n")
                        self.optionalmds=[]
                if n=="lastserver" and cnt==0:
                    lines.append("lastserver=Gmod.zapto.org\n")
                    self.lastserver="Gmod.zapto.org"
                    selserveraddr=self.lastserver
                if n=="servers" and cnt==0:
                    lines.append("servers=Gmod.zapto.org|CoCo.zapto.org\n")
                    self.servers=["Gmod.zapto.org"]
                if n=="upversion" and cnt==0:
                    lines.append("upversion=1\n")
                    self.upversion=1
            if lines[-1] == "" or lines[-1] == "\n" or lines[-1] == "\r\n":
                del lines[-1]
            f=open(self.current_folder+"/info.cfg","w")
            for l in lines:
                f.write(l)
            f.close()
        else:
            f=open(self.current_folder+"/info.cfg","w")
            f.write("mcversion="+rmcversion+"\n")
            f.write("version="+rpversion+"\n")
            f.write("upversion="+str(self.upversion)+"\n")
            f.write("mcexe="+self.mcexe+"\n")
            f.write("mcpath="+self.folder+"\n")
            f.write("optionalmods=\n")
            f.write("servers=Gmod.zapto.org|CoCo.zapto.org\n")
            f.write("lastserver=Gmod.zapto.org")
            f.close()
    
    def folder_cleanup(self):
        global fresh
        log_box("Starting fresh install.\n\n")
        log_box("Performing Folder Cleanup:\n")
        folders=[["config",0],["mods",1],["coremods",0]]
        f_count=0
        for folder in folders:
            fol=folder[0]
            keep=folder[1]
            if os.path.isdir(self.folder+"/"+fol):
                f_count+=1
                if keep==1:
                    log_box("  Deleted all files from \""+fol+"\" Folder. (Folders will remain)\n")
                else:
                    log_box("  Deleted \""+fol+"\" Folder.\n")
                if os.path.isdir(self.folder+"/"+fol):
                    if keep==0:
                        shutil.rmtree(self.folder+"/"+fol)
                    else:
                        for pth in os.listdir(self.folder+"/"+fol):
                            if os.path.isfile(self.folder+"/"+fol+"/"+pth):
                                os.remove(self.folder+"/"+fol+"/"+pth)
        if f_count==0:
            log_box("Nothing to cleanup.\n")
    
    def launchgame(self):
        #DETACHED_PROCESS = 0x00000008
        if os.name in ("nt","dos"):
            cmd='"'+self.mc_exe_tc.GetValue()+'"'
        else:
            cmd=['java','-jar',self.mc_exe_tc.GetValue(),'-Xmx1024M','-Xms1024M']
            #cmd='java'
        Popen(cmd,shell=False) #,stdin=None,stdout=None,stderr=None,close_fds=True,creationflags=DETACHED_PROCESS)
        os._exit(1)

    def OnForceUP(self, evt):
        log_box("Force Reinstalling ALL Mods.\n\n")
        self.update_prep(1)
    
    def OnUP(self, evt):
        log_box("Performing Normal Update Routine.\n\n")
        self.update_prep(0)
    
    def update_prep(self, force):
        global infolines, fresh, running, selserveraddr
        error=0
        if force == 1:
            if os.path.isfile(current_folder+"/mods_info.cfg"):
                os.remove(current_folder+"/mods_info.cfg")
            if os.path.isfile(current_folder+"/jar_info.cfg"):
                os.remove(current_folder+"/jar_info.cfg")
        if running==0:
                url="http://"+selserveraddr+"/minecraft/info2.txt"
                req = urllib2.Request(url)
                try:
                    stop=0
                    response = urllib2.urlopen(req)
                    error=0
                except urllib.error.URLError, e:
                    f=open("./URLerror.txt","w")
                    f.write(url+"\n")
                    f.write(str(e.reason[0])+": "+ e.reason[1])
                    f.close()
                except urllib.error.HTTPError, e:
                    f=open("./HTTPerror.txt","w")
                    f.write(url+"\n")
                    f.write(str(e.code)+": "+responses[e.code][1])
                    f.close()
                except:
                    wx.MessageBox("Unable to access remote info file.\nServer: "+selserveraddr+"\n\nPlease select another server or click Play.","Error")
                    error=1
                if error==0:
                    try:
                        os.rename(self.folder+"/bin/minecraft.jar", self.folder+"/bin/minecraft1.jar")
                        time.sleep(.5)
                        os.rename(self.folder+"/bin/minecraft1.jar", self.folder+"/bin/minecraft.jar")
                    except:
                        error=1
                        wx.MessageBox("Minecraft is still open.\nPlease close Minecraft and try again.","Error")
                    if error==0:
                        #self.log_tc.Clear()
                        if not os.path.isfile(current_folder+"/mods_info.cfg"):
                            self.folder_cleanup()
                            fresh=1
                        else:
                            fresh=0
                        if not os.path.isdir(self.folder+"/config"):
                            os.makedirs(self.folder+"/config")
                        if not os.path.isdir(self.folder+"/mods"):
                            os.makedirs(self.folder+"/mods")
                        if not os.path.isdir(self.folder+"/coremods"):
                            os.makedirs(self.folder+"/coremods")
                        self.running=1
                        self.up_btn.Enable(False)
                        self.forceup_btn.Enable(False)
                        self.play_btn.Enable(False)
                        for p,ifs in enumerate(infolines):
                            ifs=ifs.replace("\r\n","")
                            ifs=ifs.replace("\n","")
                        self.optionalmds=seloptional
                        selserveraddr=self.server_sel.GetValue()
                        self.save_cfg()
                        #self.up_pl_btn.SetLabel("Stop")
                        self.up_btn.Enable(False) #Temperary till if figure out how to stop the updating process
                        self.server_sel.Enable(False)
                        self.optionalmods.Enable(False)
                        CHECK_UPDATE().start()
    
    def OnPlayBtn(self, evt):
        self.up_btn.Enable(False)
        self.forceup_btn.Enable(False)
        self.play_btn.Enable(False)
        self.launchgame()
    
    def OnBrowse1(self, evt):
        self.folder = self.mc_folder_tc.GetValue()
        dialog = wx.DirDialog(None, "Please choose your minecraft folder:",style=1 ,defaultPath=self.folder, pos = (10,10))
        if dialog.ShowModal() == 5100:
            if os.path.isdir(dialog.GetPath()+"/bin") and os.path.isfile(dialog.GetPath()+"/bin/minecraft.jar"):
                self.mc_folder_tc.SetValue(dialog.GetPath())
                self.folder = dialog.GetPath()
                self.check_paths()
            else:
                wx.MessageBox("Invalid minecraft folder selected.\nPlease try again.","Error")
    
    def OnBrowse2(self, evt):
        if os.name in ("nt","dos"):
            ext=".exe"
        else:
            ext=" jar"
        dialog = wx.FileDialog(None, "Please choose your Minecraft"+ext+" file:",style=1 , pos = (10,10))
        if dialog.ShowModal() == 5100:
            self.mc_exe_tc.SetValue(dialog.GetPath())
            self.mcexe = dialog.GetPath()
            self.check_paths()
            self.save_cfg()
        else:
            if os.name in ("nt","dos"):
                ext="exe"
            else:
                ext="py"
            wx.MessageBox("Invalid minecraft."+ext+" file selected.\nPlease try again.","Error")
    
    def OnExit(self, evt):
        sys.exit(1)

if __name__ == "__main__":
    try:
        app = App(False)
        app.MainLoop()
    except:
        print "Trigger Exception, traceback info forward to log file."
        if os.path.isfile("Launcher-errlog.txt"):
            os.remove("Launcher-errlog.txt")
        traceback.print_exc(file=open("Launcher-errlog.txt","a"))
    sys.exit(1)