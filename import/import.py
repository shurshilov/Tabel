#!/usr/bin/env python 
# -*- coding: UTF-8 -*-
import parus_id_to_odoo
import dbf2pg_fcacwtd
import dbf2pg_daytype
import dbf2pg_ank
import dbf2pg_fcac
import dbf2pg_fcacch
import dbf2pg_person
import dbf2pg_post
import dbf2pg_subdiv
import dbf2pg_vidisp
import dbf2pg_fcacwth
import psycopg2
import datetime
import sys
#CONNECT TO DATABASE
#con = psycopg2.connect(database="KGBUZ", user="postgres",password="1",host="0.0.0.0",port="5432")
#cur = con.cursor()
#cur.execute ("drop table tabel_string,tabel_fcac,tabel_ank,tabel_fcacch,tabel_person,tabel_division,tabel_vidisp,tabel_fcacwth,tabel_post, tabel_tabel cascade;")
#CLOSE CONNECTION
#con.commit()
#cur.close()
#con.close()
#print "delete completed"
path2database = "./database/"
dbf2pg_person.person_func (path2database,"openerp","postgres","1","0.0.0.0","5432")
#dbf2pg_subdiv.person_func (path2database,"openerp","postgres","1","0.0.0.0","5432")
#dbf2pg_post.person_func (path2database,"openerp","postgres","1","0.0.0.0","5432")
#dbf2pg_vidisp.person_func (path2database,"openerp","postgres","1","0.0.0.0","5432")
#dbf2pg_daytype.pfcac_func (path2database,"openerp","postgres","1","0.0.0.0","5432")
#dbf2pg_fcacwtd.pfcac_func (path2database,"openerp","postgres","1","0.0.0.0","5432")
#dbf2pg_ank.post_func (path2database,"openerp","postgres","1","0.0.0.0","5432")
#dbf2pg_fcacch.person_func (path2database,"openerp","postgres","1","0.0.0.0","5432")
#dbf2pg_fcac.pfcac_func (path2database,"openerp","postgres","1","0.0.0.0","5432")
#dbf2pg_fcacwth.pfcac_func (path2database,"openerp","postgres","1","0.0.0.0","5432")






