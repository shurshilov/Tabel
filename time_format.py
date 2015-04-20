#!/usr/bin/env python
# -*- coding: utf-8 -*-
def time_format (self):
	def floatToTime (a):#перевод из десятичного в часы:минуты
	    a = float(a)*60
	    a= int(a)
	    minutes = int (a%60)
	    hours = int (a/60)
	    if minutes < 10:
		return str(hours)+":0"+str(minutes)
	    else:
		return str(hours)+":"+str(minutes)

	def timeToFloat (a):#перевод из часы:минуты в десятичное
	    time= a.split(':')
	    hours = float (time[0])
	    minutes = float (time[1])
	    t = hours*60.0 + minutes
	    t = t/60
	    return round(t, 2)

	for record in self:
		def summ (a,cnt,parent):
		    if a:
			if a.find(':')>=0:
			    a = timeToFloat(a)
			try:#проверяем если в поле число значит считаем часы
			    float(a)
#			    if type(inNumber) == float :
#			    if isinstance(a, float):
			    if record.format:#сморим какой нужен формат вывода
					self._cr.execute("UPDATE tabel_string SET  hours"+str(cnt)+" = '"+str(floatToTime(a))+"'   WHERE  tabel_string.id= "+ str(parent.id)+"  ;")
			    else:
					self._cr.execute("UPDATE tabel_string SET  hours"+str(cnt)+" = '"+str(a)+"'   WHERE  tabel_string.id= "+ str(parent.id)+"  ;")
			except ValueError:#если встретили код
			    print "error"
			    
		for i in record.ids_string:
		    summ (i.hours1,1,i)
		    summ (i.hours2,2,i)
            	    summ (i.hours3,3,i)
            	    summ (i.hours4,4,i)
            	    summ (i.hours5,5,i)
		    summ (i.hours6,6,i)
            	    summ (i.hours7,7,i)
            	    summ (i.hours8,8,i)
            	    summ (i.hours9,9,i)
            	    summ (i.hours10,10,i)
            	    summ (i.hours11,11,i)
            	    summ (i.hours12,12,i)
            	    summ (i.hours13,13,i)
            	    summ (i.hours14,14,i)
            	    summ (i.hours15,15,i)
            	    summ (i.hours16,16,i)
            	    summ (i.hours17,17,i)
            	    summ (i.hours18,18,i)
            	    summ (i.hours19,19,i)
            	    summ (i.hours20,20,i)
            	    summ (i.hours21,21,i)
            	    summ (i.hours22,22,i)
            	    summ (i.hours23,23,i)
            	    summ (i.hours24,24,i)
            	    summ (i.hours25,25,i)
            	    summ (i.hours26,26,i)
            	    summ (i.hours27,27,i)
            	    summ (i.hours28,28,i)
            	    summ (i.hours29,29,i)
            	    summ (i.hours30,30,i)
		    summ (i.hours31,31,i)


