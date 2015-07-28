#!/usr/bin/env python 
# -*- coding: UTF-8 -*-
from dbfpy import dbf
import psycopg2
import datetime
import sys
import parus_id_to_odoo
def post_func(directory,dbname,userr,pas,hostt,portt):
	ank = dbf.Dbf(directory+"zgrmonth.dbf")
	f_ank = open(directory+'grmonth.csv', 'w')
	f_ank.write ("ID; GRRBDC_RN; YEAR; MONTH; DAYALL; HOURALL \n")
	#print len(ank)
	for i in ank:
		if i.deleted or i["GRMONTH_RN"] == None or i["GRRBDC_RN"] == None or i["YEAR"] == None or i["MONTH"] == None or i["DAYALL"] == None or i["HOURALL"] == None:
			continue
		f_ank.write ( "\""+ str ( parus_id_to_odoo.parusIndexToOdoo ( i ["GRMONTH_RN"].decode('cp1251').encode('utf-8').decode('utf-8') )) +"\""+ "; ")
		f_ank.write ( "\""+ str ( parus_id_to_odoo.parusIndexToOdoo ( i ["GRRBDC_RN"].decode('cp1251').encode('utf-8').decode('utf-8') ))+"\""+ "; ")
		f_ank.write ( "\""+ str ( i["YEAR"] ).decode('cp1251').encode('utf-8')+"\""+ "; ")
		f_ank.write ( "\""+ str ( i["MONTH"] ).decode('cp1251').encode('utf-8')+"\""+ "; ")
		f_ank.write ( "\""+ str ( i["DAYALL"] ).decode('cp1251').encode('utf-8')+"\""+ "; ")
		f_ank.write ( "\""+ str ( i["HOURALL"] ).decode('cp1251').encode('utf-8')+"\""+ "\n")

	print "zgrmonth.dbf to grmonth.csv [ ok ]"
	f_ank.close()
	#CONNECT TO DATABASE
	con = psycopg2.connect(database=dbname, user=userr,password=pas,host=hostt,port=portt)
	cur = con.cursor()
	#cur.execute ("DELETE from tabel_ank;")
	
	#OPEN CSV FILE GENERATED BY syncronize.py script
	my_file = open(directory+'grmonth.csv')

	#CREATE TEMP TABLE
	cur.execute("CREATE TEMP TABLE tmp_z (ID int, GRRBDC_RN int, YEAR int, MONTH int, DAYALL int, HOURALL double precision);") 
	cur.copy_expert("COPY tmp_z FROM STDIN WITH DELIMITER ';' CSV HEADER;", my_file)

	#UPDATE DATA
	cur.execute("UPDATE tabel_grmonth SET  GRRBDC_RN=tmp_z.GRRBDC_RN, YEAR=tmp_z.YEAR, MONTH=tmp_z.MONTH, DAYALL=tmp_z.DAYALL, HOURALL=tmp_z.HOURALL FROM tmp_z WHERE  tabel_grmonth.id = tmp_z.id;")

	#INSERT DATA add something which lacks
	cur.execute("INSERT INTO tabel_grmonth (id, grrbdc_rn, year, month, dayall, hourall) SELECT T.id, T.GRRBDC_RN, T.YEAR, T.MONTH, T.DAYALL, T.HOURALL FROM tmp_z AS T LEFT JOIN tabel_grmonth AS P  ON T.id = P.id WHERE P.id IS NULL ;")

	#DROP TEMP TABLE or auto drop after session
	cur.execute("DROP TABLE tmp_z;")

	#CLOSE CONNECTION
	con.commit()
	cur.close()
	con.close()
	print "sql requests for grmonth table [ ok ]"