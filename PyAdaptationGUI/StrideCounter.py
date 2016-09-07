import ParseRoot
import serial
import time
import Tkinter
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import tkMessageBox
import imp

def ControlLoop(STDARGS):

    print(STDARGS["controller"])
    Controller = imp.load_source(STDARGS["controller"],STDARGS["controller"])
    
    sport = serial.Serial()
    sport.port = "COM1"
    rstrides = 0
    lstrides = 0
    new_stanceR = False
    new_stanceL = False
    old_stanceR = False
    old_stanceL = False
    Fzthreshold = -30 #for event detection
    gaitphase = 0
    prevvelL = STDARGS["velL"][0]
    prevvelR = STDARGS["velR"][0]
    maxstridecount = len(STDARGS["velL"])
    CARGS = {}#create dictionary of arguments to be passed to the controller
    CARGS["q3"] = STDARGS["q3"]
    CARGS["q5"] = STDARGS["q5"]
    CARGS["speedlist"] = STDARGS["speedlist"]
    CARGS["maxstridecount"] = maxstridecount
    CARGS["stopevent"] = STDARGS["stopevent"]
    CARGS["pauseevent"] = STDARGS["pauseevent"]
    CARGS["velL"] = STDARGS["velL"]
    CARGS["velR"] = STDARGS["velR"]
    CARGS["inclineang"] = STDARGS["inclineang"]
    CARGS["prevvelL"] = prevvelL
    CARGS["prevvelR"] = prevvelR

    if isinstance(STDARGS["velL"],( int, long )):#check to make sure user loaded a profile
        print('Error: no speed profile has been loaded.')
	STDARGS["stopevent"].set()
    elif (len(STDARGS["velL"]) != len(STDARGS["velR"])):
        print('Error: Uneven lengths of velocity profiles')
        STDARGS["stopevent"].set()
    else:
        #send the first speed command...
	speedlist = [int(1000*STDARGS["velR"][0]),int(1000*STDARGS["velL"][0]),1000,1000,STDARGS["inclineang"]]
	STDARGS["q3"].put(speedlist)
	print('First speed command sent.')

    #before starting check to see if we need to start Nexus
##    print(STDARGS["nexusvar"].get())
    if (STDARGS["nexusvar"]==1):
##        print('starting nexus....')
	sport.open()
##	time.sleep(0.1)
	sport.close()
	check = tkMessageBox.askyesno(title=None,message="Is Nexus recording?")
	
    CARGS["starttime"] = time.time()#allow the control loop to calculate how much time has elapsed, if it desires

    while (not STDARGS["stopevent"].is_set()):
        
	root = STDARGS["q1"].get()
	data = ParseRoot.ParseRoot(root)
	Rz = float(data["Rz"])
	Lz = float(data["Lz"])

	old_stanceR = new_stanceR
	old_stanceL = new_stanceL

	new_stanceR = Rz<Fzthreshold
	new_stanceL = Lz<Fzthreshold

	LHS = new_stanceL and not old_stanceL
	RHS = new_stanceR and not old_stanceR
	LTO = old_stanceL and not new_stanceL
	RTO = old_stanceR and not new_stanceR

	if (gaitphase == 0): #initial double support during standing
            if RTO:
                gaitphase = 1
                rstrides += 1
            if LTO:
                gaitphase = 2
                lstrides += 1
        elif (gaitphase == 1): #single stance L
            if RHS:
                gaitphase = 3
                STDARGS["Rspdind"].configure(state='normal')
                STDARGS["Rspdind"].delete(1.0,Tkinter.END)
                STDARGS["Rspdind"].insert(Tkinter.END,str(rstrides))
                STDARGS["Rspdind"].configure(state='disabled')#don't let anyone type in this
                STDARGS["axe"].plot(rstrides,STDARGS["velR"][rstrides],'r',marker='o',fillstyle='full')
                STDARGS["canvas"].draw()
                if LTO:
                    gaitphase = 2
                    lstrides += 1
        elif (gaitphase == 2):
            if LHS:
                gaitphase = 4
                STDARGS["Lspdind"].configure(state='normal')
                STDARGS["Lspdind"].delete(1.0,Tkinter.END)
                STDARGS["Lspdind"].insert(Tkinter.END,str(lstrides))
                STDARGS["Lspdind"].configure(state='disabled')#don't let anyone type in this
                STDARGS["axe"].plot(lstrides,STDARGS["velL"][lstrides],'b',marker='o',fillstyle='full')
                STDARGS["canvas"].draw()
                if RTO:
                    gaitphase = 1
                    rstrides += 1
        elif (gaitphase == 3):
            if LTO:
                gaitphase = 2
                lstrides += 1
        elif (gaitphase == 4):
            if RTO:
                gaitphase = 1
                rstrides += 1

        CARGS["rstrides"] = rstrides
        CARGS["lstrides"] = lstrides

        out = Controller.ControlLoop(CARGS)

        CARGS["prevvelL"] = out[0]
        CARGS["prevvelR"] = out[1]

	savestring = [data["FN"],Rz,Lz,int(RHS),int(LHS),int(RTO),int(LTO),int(STDARGS["pauseevent"].is_set())]
	STDARGS["q2"].put(savestring)

    if (STDARGS["nexusvar"]==1):
	sport.open()
	sport.close()
##	check = tkMessageBox.askyesno(title=None,message="Is Nexus recording?")
	
    STDARGS["StatusText"].configure(state='normal')
    STDARGS["StatusText"].delete(1.0,Tkinter.END)
    STDARGS["StatusText"].insert(Tkinter.END,'Ready')
    STDARGS["StatusText"].configure(background='#00D400')
    STDARGS["StatusText"].configure(state='disabled')#don't let anyone type in this
##    StartNexus.configure(state='normal')
    STDARGS["startbut"].configure(state='normal')

	














##def OpenLoop_wda(root,q1,speedlist,q3,savestring,q2,velL,velR,nexusvar,stopevent,axe,canvas,stopatendvar,Rspdind,Lspdind):
####		global sport
####		global firstframe
##		histzL=0
##		histzR=0
##		rstrides = 0
##		lstrides = 0
##
##		sport = serial.Serial()
##                sport.port = "COM1"
##		
##		if isinstance(velL,( int, long )):#check to make sure user loaded a profile
##			print('No speed profile has been loaded.')
##			stopvar = 1
##		else:
##			#send the first speed command...
##			speedlist = [int(1000*velR[0]),int(1000*velL[0]),1000,1000,0]
##			q3.put(speedlist)
##			print('first speed command sent')
##			
##		maxstridecount = len(velL)
####		print(maxstridecount)
##
##		#before starting check to see if we need to start Nexus
##		if nexusvar==1:
##			sport.open()
####			time.sleep(0.1)
##			sport.close()
##			
##		while (not stopevent.is_set()):
##			root = q1.get()
####			data = ParseRoot(root)
##			data = ParseRoot.ParseRoot(root)
##			
##			Rz = float(data["Rz"])
##			Lz = float(data["Lz"])
##
####			while PAUSE==1: #what to do if the pause button gets pressed
####                                time.sleep(0.2)
####                                print('Paused...')
####                                speedlist = [0,0,1000,1000,0]
####				q3.put(speedlist)
##			
##			if (Rz<-30) & (histzR>-30): #RHS
####				print('rhs')
##				Rspdind.configure(state='normal')
##				Rspdind.delete(1.0,Tkinter.END)
##				Rspdind.insert(Tkinter.END,str(rstrides))
##				Rspdind.configure(state='disabled')#don't let anyone type in this
##				axe.plot(rstrides,velR[rstrides],'r',marker='o',fillstyle='full')
##				canvas.draw()
##
##			elif (Rz>-30) & (histzR<-30): #RTO
##				rstrides +=1
####				print('rto',rstrides)
##				if (rstrides<maxstridecount):
##					speedlist = [int(1000*velR[rstrides]),int(1000*velL[lstrides]),1000,1000,0]
##					q3.put(speedlist)
####					print('speed command requested R')
####					print('q3 size: ',q3.qsize())
##				else:
##					stopevent.set()
##					continue
##				
##			if (Lz<-30) & (histzL>-30): #LHS
####				print('lhs')
##				Lspdind.configure(state='normal')
##				Lspdind.delete(1.0,Tkinter.END)
##				Lspdind.insert(Tkinter.END,str(lstrides))
##				Lspdind.configure(state='disabled')#don't let anyone type in this
##				axe.plot(lstrides,velL[lstrides],'b',marker='o',fillstyle='full')
##				canvas.draw()
##			elif (Lz>-30) & (histzL<-30): #LTO
##				lstrides +=1
####				print('lto',lstrides)
##				if (lstrides<maxstridecount):
##					speedlist = [int(1000*velR[rstrides]),int(1000*velL[lstrides]),1000,1000,0]
##					q3.put(speedlist)
####					print('speed command requested L')
##				else:
##					stopevent.set()
##					continue
##			savestring = [data["FN"],Rz,Lz]
##			q2.put(savestring)
##			
##			histzL = Lz
##			histzR = Rz
##
##		if stopatendvar==1:
##			speedlist = [int(0),int(0),1000,1000,0]
##			q3.put(speedlist)
####		t1.join()
##		
##		if nexusvar.get()==1:#stop data collection in nexus
##			sport.open()
####			time.sleep(0.1)
##			sport.close()
##			
####		cpps.kill()
##		print('CPP server killed')