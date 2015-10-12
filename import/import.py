#!/usr/bin/env python 
# -*- coding: UTF-8 -*-
import parus_id_to_odoo
import dbf2pg_fcacwtd
import dbf2pg_oleav
import dbf2pg_grday
import dbf2pg_grmonth
import dbf2pg_grrbdc
import dbf2pg_daytype
import dbf2pg_ank
import dbf2pg_fcac
import dbf2pg_fcacch
import dbf2pg_person
import dbf2pg_tipdol
import dbf2pg_post
import dbf2pg_subdiv
import dbf2pg_vidisp
import dbf2pg_fcacwth
import dbf2pg_katper
import psycopg2
import datetime
import sys

#your password for example 1
password = "1"
#your path
path2database = "/usr/lib/python2.7/dist-packages/openerp/addons/Tabel/import/database/"

dbf2pg_katper.post_func (path2database,"openerp","postgres",password,"0.0.0.0","5432")
dbf2pg_person.person_func (path2database,"openerp","postgres",password,"0.0.0.0","5432")
dbf2pg_subdiv.person_func (path2database,"openerp","postgres",password,"0.0.0.0","5432")
dbf2pg_post.person_func (path2database,"openerp","postgres",password,"0.0.0.0","5432")
dbf2pg_tipdol.person_func (path2database,"openerp","postgres",password,"0.0.0.0","5432")
dbf2pg_vidisp.person_func (path2database,"openerp","postgres",password,"0.0.0.0","5432")
dbf2pg_daytype.pfcac_func (path2database,"openerp","postgres",password,"0.0.0.0","5432")
dbf2pg_ank.post_func (path2database,"openerp","postgres",password,"0.0.0.0","5432")
dbf2pg_fcacch.person_func (path2database,"openerp","postgres",password,"0.0.0.0","5432")
dbf2pg_grrbdc.post_func (path2database,"openerp","postgres",password,"0.0.0.0","5432")
dbf2pg_grmonth.post_func (path2database,"openerp","postgres",password,"0.0.0.0","5432")
dbf2pg_grday.post_func (path2database,"openerp","postgres",password,"0.0.0.0","5432")
dbf2pg_fcac.pfcac_func (path2database,"openerp","postgres",password,"0.0.0.0","5432")
dbf2pg_fcacwtd.pfcac_func (path2database,"openerp","postgres",password,"0.0.0.0","5432")
dbf2pg_oleav.post_func (path2database,"openerp","postgres",password,"0.0.0.0","5432")







