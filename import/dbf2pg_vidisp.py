#!/usr/bin/env python 
# -*- coding: UTF-8 -*-
from dbfpy import dbf
import psycopg2
import datetime
import sys
import parus_id_to_odoo
def person_func(directory,dbname,userr,pas,hostt,portt):
	ank = dbf.Dbf(directory+"zvidisp.dbf")
	f_ank = open(directory+'vidisp.csv', 'w')
	f_ank.write ("ID; CODE; NAME\n")
	#print len(ank)
	for i in ank:
		if i.deleted or i["CODE"] == None or i["NAME"] == None:
			continue
		f_ank.write ( str ( parus_id_to_odoo.parusIndexToOdoo ( i ["VIDISP_RN"].decode('cp1251').encode('utf-8').decode('utf-8') )) +"; ")
		f_ank.write (i ["CODE"].decode('cp1251').encode('utf-8')  +"; ")
		f_ank.write (i ["NAME"].decode('cp1251').encode('utf-8')  +"\n")
	f_ank.close()
	print "zvidisp.dbf to vidisp.csv [ ok ]"
	#CONNECT TO DATABASE
	con = psycopg2.connect(database=dbname, user=userr,password=pas,host=hostt,port=portt)
	cur = con.cursor()
	#cur.execute ("DELETE from tabel_vidisp;")
	
	#OPEN CSV FILE GENERATED BY syncronize.py script
	my_file = open(directory+'vidisp.csv')

	#CREATE TEMP TABLE
	cur.execute("CREATE TEMP TABLE tmp_z (ID int unique, CODE  text, NAME text);") 
	cur.copy_expert("COPY tmp_z FROM STDIN WITH DELIMITER ';' CSV HEADER;", my_file)
	#cur.execute ("DELETE from tabel_fcac;")
	#UPDATE DATA
	cur.execute("UPDATE tabel_vidisp SET  NAME=tmp_z.NAME, CODE=tmp_z.CODE FROM tmp_z WHERE  tabel_vidisp.id = tmp_z.id;")

	#cur.execute("SELECT G.id, G.ANK_RN, G.POST_RN, G.SUBDIV_RN, G.VIDISP_RN, G.STARTDATE, G.ENDDATE FROM (SELECT T.id, T.ANK_RN, T.POST_RN, T.SUBDIV_RN, T.VIDISP_RN, T.STARTDATE, T.ENDDATE FROM tmp_z AS T LEFT JOIN tabel_fcac AS P  ON T.id = P.id WHERE P.id IS NULL) AS G, tabel_ank AS H where G.ank_rn = H.id  ;")
	#INSERT DATA add something which lacks
	cur.execute("INSERT INTO tabel_vidisp (id, code, name) SELECT T.id, T.CODE, T.NAME FROM tmp_z AS T LEFT JOIN tabel_vidisp AS P  ON T.id = P.id WHERE P.id IS NULL ;")
	
	#rows = cur.fetchall()
	#for i in rows:
	#	print i
	#DROP TEMP TABLE or auto drop after session
	cur.execute("DROP TABLE tmp_z;")

	#CLOSE CONNECTION
	con.commit()
	cur.close()
	con.close()
	print "sql requests for table vidisp [ ok ]"
#person_func ("/home/artem/Загрузки/Tabel/","KGBUZ","postgres","1","0.0.0.0","5432")
