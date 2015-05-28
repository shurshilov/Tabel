#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
def timeToFloat (a):#перевод из часы:минуты в десятичное
	    time1= re.sub(',' , '.' , a)
	    time= re.split(':|-',a)
	    try:
		if len(time)==4:
		    hours = float (time[0])
	    	    minutes = float (time[1])
		    t = hours*60.0 + minutes
		    hours1 = float (time[2])
	    	    minutes1 = float (time[3])
		    t1 = hours1*60.0 + minutes1
		    return abs((t1-t))/60
		if len(time)==2:
		    hours = float (time[0])
	    	    minutes = float (time[1])
		    t = hours*60.0 + minutes
		    t = t/60
		    return t
		if len(time)==1:
		    return float(time1)
	    except ValueError:
		return 0
	    
def floatToTime (a):#перевод из десятичного в часы:минуты
	    a = float(a)*60
	    minutes =  a%60
	    hours =  a/60
	    if int(round(minutes)) < 10:
		return str(int(hours))+":0"+str(int(round(minutes)))
	    else:
		return str(int(hours))+":"+str(int(round(minutes)))
