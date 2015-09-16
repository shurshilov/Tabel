#!/usr/bin/env python 
# -*- coding: utf-8 -*-
import re
import math
import compute_hash
import time_format
import time
import hashlib
import openerp
from openerp import models, fields
from openerp import api, exceptions
from openerp.osv import  osv
import datetime
#old api work
class res_users(osv.osv):
    _inherit='res.users'
    _rec_name='name'
    _description = ''
    def _get_emp_ids(self, cr, uid, ids, field_name, args, context=None):
	result = {}
	for user in self.browse(cr, uid, ids, context=context):
		#выбираем текущего юзера
		user = self.browse(cr,uid,ids,context=context)
		#вытаскиваем его имя + пробел вначале такой формат у паруса, для Ldap  фио в другом порядке
		fio = user.name.split(' ')
		username= u' ' + user.name
		reverse_username = u' '
		if len (fio) == 3:
			surname = fio [0]
			firstname = fio [1]
			secondname = fio [2]
			reverse_username = reverse_username + fio[2]+u' '+fio[0]+u' '+fio[1]
		#ищем все ид записей в которых совпадает фамилия имя и отчество текущего юзера
	        id_person=self.pool.get('tabel.person').search(cr,uid,['|',('full_name','=',username),('full_name','=',reverse_username)])
		#по всем ид пробегаем и получаем все ид сотрудников которые ссылаются на фамилии в person( такой ид обычно один)
		mas=[]
		for i in user.category_ids:
			mas.append(i.id)
		for i in id_person:
			id_ank=self.pool.get('tabel.ank').search(cr,uid,[('orgbase_rn.id','=',i)])
			#ищем текущий лицевой счет сотрудника
			for k in id_ank:
			    id_fcac=self.pool.get('tabel.fcac').search(cr,uid,[('ank_rn.id','=',k),('enddate','=',datetime.date(8888, 12, 31))])
			    #далее из модели берем ид отдела
			    for j in id_fcac:
				id_div = self.pool.get('tabel.fcac').browse(cr, uid, j)
				mas.append(id_div.subdiv_rn.id)
		result[user.id]= mas
		return result
    _columns = {
	#Подразделения по дефаулту + дополнительные
	'ids_division': openerp.osv.fields.function(_get_emp_ids,method=True,string='Сотрудник',type='many2many',store=False,relation='tabel.division',help='Employee'),
	#Подразделения введенные вручную(дополнительные)
	'category_ids':   openerp.osv.fields.many2many('tabel.division','tabel_division_user_rel','user_id','division_id', 'Divisions'),

	}
#odoo v8 dont work
#class res_users(models.Model):
#    _name= 'res.users'
#    _inherit= 'res.users'
#    ids_division = fields.Char( string="п.ю.")
#    ids_divisio = fields.Char(compute='div_default',   string="п.ю.", store=False)
#    @api.depends('ids_divisio','ids_division')
#    def div_default (self):
#	self._cr.execute("UPDATE res_users SET  ids_division = "+str(111)+" ;")
#	mas =None
#	#выбираем текущего юзера
#	user = self.env['res.users'].browse(self._uid)
#	#вытаскиваем его имя + пробел вначале такой формат у паруса
#	username= u' ' + user.name
#	#ищем все ид записей в которых совпадает фамилия имя и отчество текущего юзера
#        id_person=self.pool.get('tabel.person').search(self._cr,self._uid,[('full_name','=',username)])
#	#по всем ид пробегаем и получаем все ид сотрудников которые ссылаются на фамилии в person( такой ид обычно один)
#	for i in id_person:
#		id_ank=self.pool.get('tabel.ank').search(self._cr,self._uid,[('orgbase_rn.id','=',i)])
#		#ищем текущий лицевой счет сотрудника
#		for k in id_ank:
#		    id_fcac=self.pool.get('tabel.fcac').search(self._cr,self._uid,[('ank_rn.id','=',k),('enddate','=',datetime.date(8888, 12, 31))])
#		    #далее из модели берем ид отдела
#		    for j in id_fcac:
#			id_div = self.pool.get('tabel.fcac').browse(self._cr, self._uid, j)
#			mas = id_div.subdiv_rn
#			for r in self:
#			    r.ids_divisio = str(id_div.subdiv_rn.id)
#			    self._cr.execute("UPDATE res_users SET  ids_division="+str(id_div.subdiv_rn.id)+" WHERE  res_users.id = "+str(user.id) +" ;")

class Temp(models.TransientModel):
	#функция для дефаулта юзера (идет во вьюху с валидацией простой подписи)
	def user(self):
        	return self._uid
	_name = 'tabel.temp'
	user_id = fields.Many2one('res.users','Пользователь',default = user)
	password = fields.Char(string="password")
	
	#функция проверки существует ли такой пароль у такого юзера в базе (проверка идет похешу)	
	def validation(self, cr, uid, values, context):
		if not context['password']:
		    raise exceptions.ValidationError("Забыли ввести пароль!")

		if len(context['password'])!=8:
		    raise exceptions.ValidationError("Неправильная длина пароля!")

		code_private=context['password']
		code_public=code_private.upper()[4:8]
		user_id=context['user_id']
                code_private=code_private.upper()[:8]
                vals = {}
                vals ['user_id']=user_id
                vals ['password']=code_private

                check_flag=False
                id_emp_sec=self.pool.get('tabel.password').search(cr,uid,[('user_id.id','=',user_id)])
                for r in self.pool.get('tabel.password').browse(cr, uid, id_emp_sec, context=context):
                        h = hashlib.sha256()
                        h.update(code_private)
                        if r.password==h.hexdigest():
                                check_flag=True

                recs = self.pool.get('tabel.tabel').browse(cr, uid, context['tabel_id'], context=context)

                if check_flag:
                        if(context['state']=='draft'):
                                recs.signal_workflow('draft')
                        if(context['state']=='confirm'):
				recs.signature_public_tabel=code_public
				recs.ank_signature_tabel=user_id
                                recs.signal_workflow('confirm')
                        if(context['state']=='confirm2'):
				recs.signature_public_boss=code_public
				recs.ank_signature_boss=user_id
                                recs.signal_workflow('confirm2')
                        if(context['state']=='done'):
				recs.signature_public_accountant=code_public
				recs.ank_signature_accountant=user_id
                                recs.signal_workflow('done')

			return {
			'type':'ir.actions.act_window_close',
				}
                else:
                        raise exceptions.ValidationError("Не правильный пароль(Повторите ввод)!")

#Таблица логов работы с табелями
class Log(models.Model):
    _name = 'tabel.log'

    id_tabel = fields.Many2one('tabel.tabel',  ondelete='cascade', string="tabel_id")
    user_id = fields.Many2one('res.users','Пользователь')
    action = fields.Char(string="Действие")
    status = fields.Integer(string="Состояние действия")



#Значение нормы часов для конкретного дня месяца по конкретному виду часов
class Grday (models.Model):
	_name = 'tabel.grday'

	grmonth_rn = fields.Many2one('tabel.grmonth', ondelete='cascade',string="GRMONTH_RN",index=True)
	monthday = fields.Integer(string="MONTHDAY",index=True)
	hourinday = fields.Float(string="HOUR IN DAY")



#Таблица с категориями работников, не используется
class Katper (models.Model):
	_name = 'tabel.katper'
#	_rec_name = 'num'
	_order = 'num'
	code = fields.Char(string="code of katper")
	name = fields.Char(string="name of katper")
	nick = fields.Char(string="nick of katper")
	num = fields.Integer(string="NUM")



#Количество нормо-дней и часов за конкретный месяц конкретного года, по виду из таблицы Grrgdc
class Grmonth (models.Model):
	_name = 'tabel.grmonth'
	_rec_name = 'grrbdc_rn'
	
	grrbdc_rn = fields.Many2one('tabel.grrbdc', ondelete='cascade',string="GRRBDC_RN",index=True)
	year = fields.Integer(string="YEAR",index=True)
	month = fields.Integer(string="MONTH",index=True)
	dayall = fields.Integer(string="DAYALL")
	hourall = fields.Float(string="HOURALL")



#Вид трудового дня, он же график работы, т.е. по 8 часов по 7,7 по 6 часов 5 дневка 6 дневка и т.д.
class Grrbdc (models.Model):
	_name = 'tabel.grrbdc'

	code = fields.Char(string="CODE")
	name = fields.Char(string="NAME")
	daysmean = fields.Float(string="DAYSMEAN")
	hourmean = fields.Float(string="HOURMEAN")
	workweek = fields.Integer(string="WORKWEEK")
	daysmin = fields.Float(string="DAYSMIN")
	hourmin = fields.Float(string="HOURMIN")



#Расшифровка дня неявки О-отпуск К-командировка и т.д.
class Daytype(models.Model):
	_name = 'tabel.daytype'
	
	nick = fields.Char(string="nick of Vidisp")
	name = fields.Char(string="name of Vidisp")



#Сформированные бухгалтером дни явок для каждого сотрудника за каждый день месяца, большая таблица
#Не используется, если бух. формирует дни после приема табелей
class Fcacwtd(models.Model):
	_name = 'tabel.fcacwtd'
	
	fcac_rn = fields.Many2one('tabel.fcac',  ondelete='cascade', string="fcac_id")
	daytype_rn = fields.Many2one('tabel.daytype',  ondelete='cascade', string="daytype_id")
	date=  fields.Date(string="time of day tabel", index = True)



#Сформированные бухгалтером отработанные часы за каждый день месяца для каждого сотрудника, очень большая таблица
#Не используется, если бух. формирует часы после приема табелей
class Fcacwth(models.Model):
	_name = 'tabel.fcacwth'
	_rec_name = 'hourqnt'

	fcac_rn = fields.Many2one('tabel.fcac',  ondelete='cascade', string="fcac_id")
	hrtype_rn = fields.Integer(string="HRTYPE_RN")
	hourqnt = fields.Float(string="chasi hourqnt")
	date =  fields.Date(string="time of hour tabel", index = True)



#Таблица ставок для каждого лицевого счета
class Fcacch(models.Model):
	_name = 'tabel.fcacch'
	_rec_name = 'stqnt'

	stqnt = fields.Float(string="stavka stqnt", required=True)
	fcacbs_rn = fields.Integer(string="FCACBS_RN",index=True)
	grrbdc_rn = fields.Integer(string="grrbdc_rn")



#Таблица вида исполнения (основной, совместительство и т.д.)
class Vidisp(models.Model):
	_name = 'tabel.vidisp'
	_rec_name = 'code'

	code = fields.Char(string="code of Vidisp", required=True)
	name = fields.Char(string="name of Vidisp", required=True)



#Таблица должностей
class Post(models.Model):
	_name = 'tabel.post'
	_rec_name = 'name'
	_order = 'num'

	num = fields.Integer(string="num")
	name = fields.Char(string="name of Post", required=True)
	enddate = fields.Date(string="enddate post")
	startdate = fields.Date(string="startdate post")



#Таблица типовых должностей
class Tipdol(models.Model):
	_name = 'tabel.tipdol'
	_rec_name = 'code'
	_order = 'num'

	num = fields.Integer(string="num")
	name = fields.Char(string="name of Tipdol")
	code = fields.Char(string="code of Tipdol")


#Таблица персон, содержит только фамилию имя и отчества, значения могут повторяться
class Person(models.Model):
	_name = 'tabel.person'
	_rec_name= 'full_name'
	_order = 'full_name'

	surname = fields.Char(string="Фамилия", required=True)
	firstname = fields.Char(string="Имя", required=True)
	secondname = fields.Char(string="Отчество", required=True)
	initials_first = fields.Char(compute='_compute_first',string="Инициал Имени")
	initials_second = fields.Char(compute='_compute_second',string="Инициал Отчества")
	full_name = fields.Char (string="Полное имя")
#	init_name  = fields.Char(compute='_compute_init',string="Фамилии инициалы")

	@api.depends('firstname')
	def _compute_first (self):
		for record in self:
		    if type (record.firstname) != bool:
			if len(record.firstname) >1:
				record.initials_first = u"\u00A0"+ record.firstname [1]+"."
			else:
			    record.full_name = "пусто"
		    else:
			record.full_name = "пусто"


	@api.depends('secondname')
        def _compute_second (self):
		for record in self:
		    if type (record.secondname) != bool:
			if len (record.secondname) >1:
				record.initials_second = record.secondname [1]+"."

#	@api.depends('surname','firstname','secondname')
#        def _compute_init (self):
#		for record in self:
#		    record.init_name=surname+initials_first+initials_second

	def name_get(self, cr, uid, ids, context):
        	if not len(ids):
        	    return []
        	res=[]
		ank=" "
        	for emp in self.browse(cr, uid, ids):
			if emp.surname and emp.initials_first and emp.initials_second:
			    ank=emp.surname+emp.initials_first+emp.initials_second
			res.append((emp.id,ank))
		return res



#Таблица сотрудников
class Ank(models.Model):
	_name = 'tabel.ank'
	_rec_name = 'orgbase_rn'
	_order = 'orgbase_rn'

	orgbase_rn = fields.Many2one('tabel.person',  ondelete='cascade', string="orgbase_rn")
	tab_num = fields.Integer(string="TAB_NUM")
	jobbegin = fields.Date(string="time begin of work")
	jobend = fields.Date(string="time end of work")



#Таблица лицевых счетов, основная таблица
class Fcac(models.Model):
	_name = 'tabel.fcac'
	_rec_name = 'ank_rn'
	_order = 'katper_rn'

	tipdol_rn = fields.Many2one('tabel.tipdol',ondelete='cascade', string="tipdol_rn")
	katper_rn = fields.Many2one('tabel.katper',ondelete='cascade', string="katper_rn")
	fcacch_rn =fields.One2many('tabel.fcacch', 'fcacbs_rn', string="fcacch_rn")
	ank_rn = fields.Many2one('tabel.ank',  ondelete='cascade', string="ank_rn")
	post_rn = fields.Many2one('tabel.post',  ondelete='cascade', string="post_rn",index=True)
	subdiv_rn = fields.Many2one('tabel.division',  ondelete='cascade', string="subdiv_rn")
	vidisp_rn = fields.Many2one('tabel.vidisp', ondelete='cascade', string="vidisp_rn",index =True)
	startdate = fields.Date(string="time begin of fcac")
	enddate = fields.Date(string="time end of fcac")

	def name_get(self, cr, uid, ids, context):
    	    if not len(ids):
    		return []
    	    res=[]
    	    for emp in self.browse(cr, uid, ids,context=context):
		ank = " "
		for line in emp.ank_rn:
		    for r in line.orgbase_rn:
			ank=r.surname+r.initials_first+r.initials_second
		res.append((emp.id,ank))
	    return res



#Таблица подразделений
class Division(models.Model):
    _name = 'tabel.division'

    name = fields.Char(string="name of Division", required=True)
    enddate = fields.Date(string="enddate div")
    startdate = fields.Date(string="startdate div")



#Таблица строк табелей, основная таблица
class String(models.Model):
    _name = 'tabel.string'
    _rec_name = 'id_fcac'
    _order = 'id_tipdol, id_person'

    id_fcac = fields.Many2one('tabel.fcac',  ondelete='cascade', string="fcac_id")
    id_katper = fields.Many2one('tabel.katper',  ondelete='cascade', string="категории")
#    id_ank = fields.Many2one('tabel.ank',  ondelete='cascade', string="сотрудник")
    id_tipdol = fields.Many2one('tabel.tipdol',string="тип должности")
    #используется для сортировки по алфавиту,во вью невидимое
    id_person = fields.Many2one('tabel.person',  ondelete='cascade', string="фамилии")
    id_tabel = fields.Many2one('tabel.tabel',  ondelete='cascade', string="tabel_id",index=True)
    #не используется
    id_post = fields.Many2one('tabel.post',string="должность")
    id_vidisp = fields.Many2one('tabel.vidisp',string="вид л.с.")
    stqnt = fields.Float(string="ставка",digits=(12,3))

    hours1 = fields.Char(string="1")
    hours2 = fields.Char(string="2")
    hours3 = fields.Char(string="3")
    hours4 = fields.Char(string="4")
    hours5 = fields.Char(string="5")
    hours6 = fields.Char(string="6")
    hours7 = fields.Char(string="7")
    hours8 = fields.Char(string="8")
    hours9 = fields.Char(string="9")
    hours10 = fields.Char(string="10")
    hours11 = fields.Char(string="11")
    hours12 = fields.Char(string="12")
    hours13 = fields.Char(string="13")
    hours14 = fields.Char(string="14")
    hours15 = fields.Char(string="15")
    hours16 = fields.Char(string="16")
    hours17 = fields.Char(string="17")
    hours18 = fields.Char(string="18")
    hours19 = fields.Char(string="19")
    hours20 = fields.Char(string="20")
    hours21 = fields.Char(string="21")
    hours22 = fields.Char(string="22")
    hours23 = fields.Char(string="23")
    hours24 = fields.Char(string="24")
    hours25 = fields.Char(string="25")
    hours26 = fields.Char(string="26")
    hours27 = fields.Char(string="27")
    hours28 = fields.Char(string="28")
    hours29 = fields.Char(string="29")
    hours30 = fields.Char(string="30")
    hours31 = fields.Char(string="31")

    days_appear = fields.Char(string="Дни",compute='_compute_days_appear')
    hours_main = fields.Char(string="Осн",compute='_compute_days_appear')
    hours_night = fields.Char(string="Ноч")
    hours_holiday = fields.Char(string="Пра")
    hours_internal = fields.Char(string="Вну",compute='_compute_days_appear')
    days_absences = fields.Char (string="Неяв",compute='_compute_days_appear')
    days_absences_sum = fields.Char (string="Сум",compute='_compute_days_appear')
    counter = fields.Integer (string = "Счет",default=0)
    percent = fields.Char (string = "Прц")
    complet = fields.Char (string = "Разнести")
    time_start_s = fields.Date (related='id_tabel.time_start_t', string="дата начала(строка в каком месяце)")

    
    def create(self, cr, uid, values, context):
			context = {}
			values ['counter']=1
			#записываем соответствующее поле персоны при создании записи
			model_fcac= self.pool.get('tabel.fcac').browse(cr, uid, values ['id_fcac'] )
			values ['id_person'] = model_fcac.ank_rn.orgbase_rn.id
			id = super(String, self).create(cr, uid, values)
			return id

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',context=None, toolbar=False, submenu=False):

	 result = super(String, self).fields_view_get(cr, uid, view_id, view_type,context, toolbar, submenu)
         # use lxml to compose the arch XML
         arch=result['arch']
         fields = result['fields']
         tb = {'print': [], 'action': [], 'relate': []}
         if view_type=='search':
             return result
         if view_type=='tree':
             return result


#         if view_type=='search':
#             return result
#
#         if view_type=='tree':
#             return result

         if view_type=='form':
#	    now_date = datetime.date.today()
#	    now_date = now_date.replace(day=1).strftime('%Y-%m-%d')
#        <field name="id_post" string="должность" readonly= "True" domain="[('enddate','&gt;=',' '''+str(time)+''' '),('startdate','&lt;=',' '''+str(time2)+''' '),('startdate','&gt;=',' '''+time3+''' ')   ]"/>
	    time3=datetime.date(2014, 03, 1).strftime('%Y-%m-%d')
	    time=context['time_start_t']
	    time2=context['time_end_t']
	    arch = ''' <form string="Analytic" create="false" edit="false" write="false">
            <group>
        <field name="id_fcac" string="ФИО" readonly= "True" domain="[('enddate','&gt;=',' '''+str(time)+''' '),('startdate','&lt;=',' '''+str(time2)+''' ')   ]"  placeholder="Начните вводить ФИО"/>
        <field name="id_vidisp" string="вид л.с." readonly= "True" domain="[('code','not like','----')]"  placeholder="Начните вводить Вид л.с."/>
        <field name="id_tipdol" string="должность" readonly= "True"  placeholder="Начните вводить должность"/>

        <field name="stqnt" string="кол-во ст." readonly= "True"  placeholder="Введите ставку"/>
        </group>
        <table border="3" bordercolor="white"  style="border-collapse: collapse;">
        <tr>
            <th style="border: 1px solid #7C7BAD;">сумма дней</th>
            <th style="border: 1px solid #7C7BAD;">основные </th>
            <th style="border: 1px solid #7C7BAD;">внутренние</th>
            <th style="border: 1px solid #7C7BAD;">неявки</th>
            <th style="border: 1px solid #7C7BAD;">сумма неявок</th>
            <th style="border: 1px solid #7C7BAD;">проценты</th>
            <th style="border: 1px solid #7C7BAD;">ночные</th>
            <th style="border: 1px solid #7C7BAD;">праздничные</th>
        </tr>
        <tr>
    	    <td style="border: 1px solid #7C7BAD;"><field name="days_appear" string ="сумма дней"/> </td>
    	    <td style="border: 1px solid #7C7BAD;"><field name="hours_main" string="Основные часы"/> </td>
    	    <td style="border: 1px solid #7C7BAD;"><field name="hours_internal" string="Внутренние часы"/> </td>
    	    <td style="border: 1px solid #7C7BAD;"><field name="days_absences" string="Неявки"/> </td>
    	    <td style="border: 1px solid #7C7BAD;"><field name="days_absences_sum" string="Сумма Неявок"/> </td>

    	    <td style="border: 1px solid #7C7BAD;"><field name="percent"  placeholder="Введите проценты"/> </td>
    	    <td style="border: 1px solid #7C7BAD;"><field name="hours_night"  placeholder="Введите ночные часы"/> </td>
    	    <td style="border: 1px solid #7C7BAD;"><field name="hours_holiday"  placeholder="Введите праздничные часы"/></td>
        </tr>
        </table>

	<table border="3" bordercolor="white" style="width: 100%; white-space: nowrap; table-layout: fixed;m border-collapse: collapse; margin-top: 30px;">
	<tr>
	<th style=" border: 1px solid #7C7BAD;"><p align="center">Понедельник</p></th>
        <th style=" border: 1px solid #7C7BAD;"><p align="center">Вторник</p></th>
        <th style=" border: 1px solid #7C7BAD;"><p align="center">Среда</p></th>
        <th style=" border: 1px solid #7C7BAD;"><p align="center">Четверг</p></th>
        <th style=" border: 1px solid #7C7BAD;"><p align="center">Пятница</p></th>
        <th style=" border: 1px solid #7C7BAD;"><p align="center">Суббота</p></th>
        <th style=" border: 1px solid #7C7BAD;"><p align="center">Воскресенье</p></th>
        </tr>
             '''
	    dayweek =  int(datetime.datetime.strptime(time, '%Y-%m-%d').date().weekday())
	    cnt=dayweek
	    for i in range (1,32):
		if i == 1:
		    arch+=''' <tr>  '''
		    for j in range (0,dayweek):
			arch+=''' <td style="border: 1px solid #7C7BAD;"></td>  '''
		if cnt%7 == 0:
		    arch+=''' </tr> <tr> '''
		if cnt%7 == 6 or cnt%7 == 5:
		    arch+=''' <td style="border: 1px solid #7C7BAD;" bgcolor="#EADEE0"><p align="center"><b><font color="#7C7BAD">''' +str(i)+'''</font></b></p>  <field name="hours%s" string="%s. %s" /></td> '''%(i,i,i)
		else:
		    arch+=''' <td style="border: 1px solid #7C7BAD;"><p align="center"><b><font color="#7C7BAD">''' +str(i)+'''</font></b></p>  <field name="hours%s" string="%s. %s" /></td> '''%(i,i,i)
		if i==31:
		    arch+=''' </tr>  '''
		cnt=cnt+1
	    arch+=''' </table>
			<table style="margin-top: 20px;">
			<tr>
			<td><field name="complet" string="введите общее значение"/></td>
			<td><button
				name="compute_complet"
				type="object"
				string="Разнести"
				class="oe_inline oe_stat_button"
				icon="fa-pencil"
			/></td>
			</tr>
			</table>
			</form> '''

            fields = result['fields']
	    result = {
             'arch': arch,
             'fields': fields,
             'toolbar': tb,
         }
	#Set readonly mode for field ['days_appear','hours_main','hours_internal','days_absences','days_absences_sum']
	    from lxml import etree
	    from openerp.osv.orm import setup_modifiers
	    doc = etree.XML(result['arch'])
            for node in doc.xpath("//field[@name='days_appear']"):
                            node.set('readonly', "1")
                            setup_modifiers(node, result['fields']['days_appear'])

            for node in doc.xpath("//field[@name='hours_main']"):
                            node.set('readonly', "1")
                            setup_modifiers(node, result['fields']['hours_main'])

            for node in doc.xpath("//field[@name='hours_internal']"):
                            node.set('readonly', "1")
                            setup_modifiers(node, result['fields']['hours_internal'])

            for node in doc.xpath("//field[@name='days_absences']"):
                            node.set('readonly', "1")
                            setup_modifiers(node, result['fields']['days_absences'])

            for node in doc.xpath("//field[@name='days_absences_sum']"):
                            node.set('readonly', "1")
                            setup_modifiers(node, result['fields']['days_absences_sum'])

            result['arch'] = etree.tostring(doc)

         return result

    #функция разнести
    @api.one
    def compute_complet (self):
		    #прогон по колонкам 1-31
		    for j in range(1, 32):
			    hours='hours{0}'.format(j)
			    setattr(self, hours, self.complet)

    #функция вычисляющая количетсво дней неявок,явок,отработанных часов и т.д.
    @api.depends('hours1','hours2','hours3','hours4','hours5','hours6','hours7','hours8','hours9','hours10','hours11','hours12','hours13','hours14','hours15','hours16','hours17','hours18','hours19','hours20','hours21','hours22','hours23','hours24','hours25','hours26','hours27','hours28','hours29','hours30','hours31')
    def _compute_days_appear(self):
	
        id_emp_sec=self.pool.get('tabel.daytype').search(self._cr,self._uid,[('nick','!=','')])#получаем ид всех строк из таблице daytype где есть ник
	model_daytype= self.pool.get('tabel.daytype').browse(self._cr, self._uid, id_emp_sec)

#	self=self.sorted(key=lambda r: r.id_fcac.katper_rn)
	for record in self:
#		проверка на то чтобы должности и типовые должности совпадали
#		if record.id_tipdol.code != record.id_post.name:
#		    record.counter=1

#		if record.counter:
#		    record.counter = str(float (record.counter) +1)
#		else:
#		    record.counter="0"
		#record.stqnt=round(record.stqnt,3)
		record.days_absences_sum = "0"#количество дней неявок в сумме
		record.days_absences = " "#строка неявок в формате (код/кол-во;)
		record.days_appear = "0"#дни явок в сумме
		record.hours_main = "0.0"#количество основных отработанных часов
		record.hours_internal= "0.0"#количество внутренних(совместительство) отработанных часов

		d_abse ={}#заполняем словарь из кодов неявок для дальнейшего подсчета
		for r in model_daytype:
		    a = r.nick.replace (' ','')
#		    a = a.upper()
		    d_abse[a] = 0
		#vidisp = record.id_fcac.vidisp_rn.name
		vidisp= record.id_vidisp.name
		if vidisp:
            	    vidisp1 = u' Внутренний совместитель'#если внутренний совместитель то считаются часы не основные а внутренние
		    current_model = self.pool.get('tabel.tabel').browse(self._cr, self._uid, record.id_tabel.id,self._context)
		    global flag#флаг который показывает какие часы считать внутренние или основные
		    flag =1 
		    for i in range ( 0,  min ( len (vidisp), len (vidisp1) ) ):
			    if vidisp[i] != vidisp1[i] :
				    flag =0
				    break
		    def summ (a):
			
			global flag
			flagEx = False
			if a:
			    #проверяем если поле является временем в формате hh:mm (or h:m) или числом,тогда все ок
			    a=a.replace(' ', '')
			    if re.search('^(([0,1][0-9])|(2[0-4])|([0-9])):(([0-5][0-9])|([0-9]))$',a)>=0 or re.search('^\-?\d+((,|\.)\d+)?$',a)>=0:
				a =time_format.timeToFloat  (a)
			    #иначе предполагаем что это код. смотрим в словарь кодов и если не код возвращаем ошибку (-1)
			    else:
				if len(a)>0:
				    if a not in d_abse:
					return -1
			
			    try:#проверяем если в поле число значит считаем часы
				float(a)
			    except ValueError:#если встретили код
				a=a.replace(' ', '')
#				a=a.upper()
				flagEx = True#показываем что уже был посчитан код
				if a in d_abse:
				    d_abse[a]=d_abse[a]+1#добавляем в словарь кода 1
				    record.days_absences_sum= str(int(record.days_absences_sum)+1)#добавляем неявку
				    record.days_absences = " "#пересчитываем строку кодов. т.к. может быть добавлен еще код
				    for i in d_abse:#генерируем строку неявок код/число неявок
					if d_abse[i]>0:
					    record.days_absences=record.days_absences+ i+u'/'+str(d_abse[i]).decode('utf-8')+u'; '
				#если нет такого кода возвращаем ошибку
				
			    if flagEx==False:#если у нас число то пересчитываем основные или внутренние часы. переводим в числа.

				if record.hours_internal.find(':')>=0:
				    record.hours_internal = time_format.timeToFloat (record.hours_internal)
				if record.hours_main.find(':')>=0:
				    record.hours_main = time_format.timeToFloat (record.hours_main)

				if flag == 1:#считаем внутренние
				    record.hours_internal = str (float(record.hours_internal)+ float(a))
				else:
				    record.hours_main = str (float(record.hours_main)+ float(a))

				record.days_appear = str (int(record.days_appear) + 1)#в любом случае это явка
			return 1


		    #прогон по колонкам 1-31
		    for j in range(1, 32):
				hours='hours{0}'.format(j)
				if summ (getattr(record, hours)) == -1:
					setattr(record, 'counter', 2)

	            record.id_person = record.id_fcac.ank_rn.orgbase_rn.id

		    if record.days_absences_sum == "0":
			    record.days_absences_sum = " "
		    if record.days_appear == "0":
			     record.days_appear = " "
		    #Не печатаем ноль только в основном виде исполнения и внутреннем совместительстве
		    if record.hours_main == "0.0" and (vidisp==u' Основной работник' or  vidisp==u' Внутренний совместитель'):
			    record.hours_main = " "
		    if record.hours_internal == "0.0":
			    record.hours_internal = " "
		    if record.percent:
			    record.days_appear= " "

		    # переделать округление?
		    try:
			aaa=float(record.hours_internal)
			record.hours_internal = str (round (aaa,2)  )
		    except:
			print 1
		    try:
			bbb=float(record.hours_main)
			record.hours_main = str (round(bbb,2) )
		    except:
			print 1

		

class Password(models.Model):

	_name = 'tabel.password'

	#функция для дефаулта юзера (идет во вьюху с валидацией простой подписи)
	def user(self):
        	return self._uid

	user_id = fields.Many2one('res.users','Пользователь',default = user)
	password = fields.Char(string="Простая электронная подпись")
	public_key = fields.Char(string="Открытый ключ")
	#перед тем как сохранить пароль берем от него хеш и сохраняем не сам пароль а хеш
	_sql_constraints = [
	        ('public_key_uniq', 'unique (public_key)', 'Public key must be unique.'),
	        ('password_uniq', 'unique (password)', 'Password must be unique.'),
	    ]
	def create(self, cr, uid, values, context):
		if  context['state']=='create':
			if not values['password']:
			    raise exceptions.ValidationError("Забыли ввести пароль!")
			if len(values['password'])!=8:
			    raise exceptions.ValidationError("Неправильная длина пароля!")

			context = {}
			vals = {}
			h = hashlib.sha256()
			code_private=values['password']
			code_public=code_private.upper()[4:8]
			user_id=values['user_id']
			#8 - password fixed length!!!
			code_private=code_private.upper()[:8]
			h.update(code_private)
			vals ['user_id']=user_id
			vals ['public_key']=code_public
			vals ['password']=h.hexdigest()
			id = super(Password, self).create(cr, uid, vals, context=None)
			return id

		id = super(Password, self).create(cr, uid, values)
		return id


class Tabel(models.Model):
    _name = 'tabel.tabel'

    #_rec_name = 'id_ank'
    _order = 'orgbase_rn'
    _inherits = {
	'tabel.ank':'id_ank',
}
    
    #первый день текущего месяца
    def time_first (self):
	now_date = datetime.date.today()
	now_date = now_date.replace(day=1)
	return now_date

    #последний день текущего месяца
    def time_last (self):
	now_date = datetime.date.today()
	now_date = now_date.replace(month=now_date.month+1, day=1) - datetime.timedelta(days=1)
	return now_date

    def ank_default (self):
	for user in self.env['res.users'].browse(self._uid):
	    fio = user.name.split(' ')
	    username= u' ' + user.name
	    reverse_username = u' '
	    if len (fio) == 3:
		reverse_username = reverse_username + fio[2]+u' '+fio[0]+u' '+fio[1]
	    id_person=self.pool.get('tabel.person').search(self._cr,self._uid,['|',('full_name','=',username),('full_name','=',reverse_username)])
	    for i in id_person:
			id_ank=self.pool.get('tabel.ank').search(self._cr,self._uid,[('orgbase_rn.id','=',i)])
			#как только нашли ид ank то сразу возвращаем его
			for j in id_ank:
				    return j

    def div_default (self):
	for user in self.env['res.users'].browse(self._uid):
	    fio = user.name.split(' ')
	    username= u' ' + user.name
	    reverse_username = u' '
	    if len (fio) == 3:
		reverse_username = reverse_username + fio[2]+u' '+fio[0]+u' '+fio[1]
	    id_person=self.pool.get('tabel.person').search(self._cr,self._uid,['|',('full_name','=',username),('full_name','=',reverse_username)])
	    for i in id_person:
			id_ank=self.pool.get('tabel.ank').search(self._cr,self._uid,[('orgbase_rn.id','=',i)])
			for k in id_ank:
			    id_fcac=self.pool.get('tabel.fcac').search(self._cr,self._uid,[('ank_rn.id','=',k),('enddate','=',datetime.date(8888, 12, 31))])
			    #далее из модели берем ид отдела
			    for j in id_fcac:
				id_div = self.pool.get('tabel.fcac').browse(self._cr, self._uid, j)
				return id_div.subdiv_rn


    name = fields.Char ('КГБУЗ ККОКБ им. П.Г. Макарова',default="КГБУЗ ККОКБ им. П.Г. Макарова" )
    comment = fields.Text (string="Комментарии к табелю")
    signature_tabel      =  fields.Char(string="signature tabel")
    signature_boss       =  fields.Char(string="signature boss")
    signature_accountant =  fields.Char(string="signature accountant")
    signature_public_tabel      =  fields.Char(string="Открытая часть табельщика")
    signature_public_boss       =  fields.Char(string="Открытая часть начальника")
    signature_public_accountant =  fields.Char(string="Открытая часть бухгалтера")
    check_signature = fields.Boolean(string="проверка подписи",default=True)#для пользователей сырой документ считается валидным.
    ank_signature_tabel      = fields.Many2one('res.users', string="имя сотрудника подписи (табельщик)")
    ank_signature_boss       = fields.Many2one('res.users', string="имя сотрудника подписи (нач.отдела)")
    ank_signature_accountant = fields.Many2one('res.users', string="имя сотрудника подписи (бухгалтер)")

    format = fields.Boolean (string = "десятичные/минуты", default = False)
    num_tabel = fields.Integer(string="number of Tabel")
    time_start_t = fields.Date(string="time start of tabel", default = time_first,index=True)
    time_end_t = fields.Date(string="time end of tabel", default = time_last,index=True)
    id_ank = fields.Many2one('tabel.ank',  ondelete='cascade', string="ank_id", required=True,default= ank_default)
    ids_string = fields.One2many('tabel.string', 'id_tabel', string="string")
    ids_grstring = fields.One2many('tabel.grstring', 'id_tabel', string="string",  limit = 500)
    ids_log = fields.One2many('tabel.log', 'id_tabel', string="log")

    state = fields.Selection([
         ('draft', "Не подписанный"),
         ('confirmed', "Подписанный табельщиком"),
	 ('confirmed2', "Подписанный нач.отдела"),
         ('done', "На исполнение"),
    ])
    id_division = fields.Many2one('tabel.division',  ondelete='cascade', string="division_id", required=True,default= div_default)
    dayall = fields.Integer(string="Количество рабочих дней в месяце")

#Логгирование изменений
    def write(self, cr, uid, ids, vals, context=None):
	current_tabel = self.pool.get('tabel.tabel').browse(cr, uid, ids[0])
	current_state = current_tabel.state

        write_res = super(Tabel, self).write(cr, uid, ids, vals, context=context)

	log= u'изменения в табеле:'+u"\n"
	state_id = 0
	state_check = {'draft':0,'confirmed':1,'confirmed2':2,'done':3, }
	if vals.has_key('state') and current_state:
#	    raise exceptions.ValidationError(str(state_check[vals['state']])+str( state_check[current_state]) )
	    if state_check[vals['state']] > state_check[current_state]:
		log = u'подписание'
		state_id = 1
	    else:
		log = u'аннулирование'
		state_id = 2
	    self.pool.get('tabel.log').create(cr, uid, {'user_id':uid,'action':log,'id_tabel': ids[0],'status':state_id})

	if vals.has_key('ids_string'):
	    for i in vals['ids_string']:
		    if i[2]:
			    current_string=self.pool.get('tabel.string').browse(cr, uid, i[1])
			    log += unicode(i)+u" "+ current_string.id_person.surname
	    self.pool.get('tabel.log').create(cr, uid, {'user_id':uid,'action':log,'id_tabel': ids[0],'status':state_id})
        return write_res

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=True, toolbar=False, submenu=False):

        result = super(Tabel, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
        if view_type=='form':
	    state=context.get('state', False)
            if state!='draft':
		result['arch']=result['arch'].replace('<form','<form edit=\"false\"')
        return result

    @api.one
    def time_button (self):
	def ftohhmm(a):
	    if a: #проверка на заполненность
		a = re.sub(',' , '.' , a) #замена запятых точками (6,5 --> 6.5)
		if (re.search ('^\-?\d+((,|\.)\d+)?$',a) >= 0): #проверка на число
		    if float(a)<24: #проверка корректности ввода
			a=float(a)*60
			minutes=a%60
			hours=a/60
			if int(round(minutes))<10:
			    return str(int(hours))+":0"+str(int(round(minutes)))
			else:
			    return str(int(hours))+":"+str(int(round(minutes)))
	    return a

	if self:
	    for i in self.ids_string:
		for j in range(1, 32):
		    hours='hours{0}'.format(j)
		    setattr(i, hours, ftohhmm(getattr(i, hours))) #прогон по колонкам 1-31


    #Обновить данные по пропускам(приказам),если появился новый сотрудник или больничный или отпуск и т.д. то данные обновятся не стирая введеные часы
    @api.one
    def action_tabel(self):
	#Добавляем лицевые счета (сотрудники) Нужно сделать через промежуточную таблицу апдейт
	self._cr.execute("INSERT INTO tabel_string (id_fcac,id_tabel) (SELECT T.id,"+str(self.id)+"  FROM tabel_fcac AS T LEFT JOIN (SELECT * from tabel_string WHERE id_tabel="+str(self.id)+") AS P  ON T.id = P.id_fcac  WHERE P.id_fcac IS NULL and T.startdate::date <='"+str(self.time_end_t)+"' and T.enddate::date >= '"+str(self.time_start_t)+"' and T.subdiv_rn = "+str(self.id_division.id)+"   )  ;")

#	id_emp_sec=self.pool.get('tabel.string').search(self._cr,self._uid,[(1,'=',1)])#получаем ид всех строк из таблице daytype где есть ник
	#Если строка была создана вручную или уже есть, то ее не обновляем. Обновляем только новые пустые строки.... 
	#(возможна неправильная ситуация (не сработает обновление на уже созданном) надо подумать)
	#Обновляем должности и вид л.с.
        id_emp_sec=self.pool.get('tabel.string').search(self._cr,self._uid,[('id_tabel','=',self.id)])#получаем ид всех строк из таблице daytype где есть ник
	for i in id_emp_sec:
		
		model_string= self.pool.get('tabel.string').browse(self._cr, self._uid, i)

		#обновляем ставки, если поле пустое
		if model_string.stqnt:
		    continue
		else:
		    id_emp_sec2=self.pool.get('tabel.fcacch').search(self._cr,self._uid,[('fcacbs_rn','=',model_string.id_fcac.id)])
		    for j in id_emp_sec2:
			model_fcacch= self.pool.get('tabel.fcacch').browse(self._cr, self._uid, j)
			model_string.stqnt=model_fcacch.stqnt

		#обновляем должности если поле пустое
		if model_string.id_post:
		    continue
		else:
		    model_string.id_post=model_string.id_fcac.post_rn.id

		#обновляем типовые должности, которые используются, если поле пустое
		if model_string.id_tipdol:
		    continue
		else:
		    model_string.id_tipdol=model_string.id_fcac.tipdol_rn.id

		#обновляем ФИО, если поле пустое
		if model_string.id_person:
		    continue
		else:
		    model_string.id_person=model_string.id_fcac.ank_rn.orgbase_rn.id

		#обновляем виды исполнения, если поле пустое
		if model_string.id_vidisp:
		    continue
		else:
		    model_string.id_vidisp=model_string.id_fcac.vidisp_rn.id

		#обновляем категории, если поле пустое
		if model_string.id_katper:
		    continue
		else:
		    model_string.id_katper=model_string.id_fcac.katper_rn.id

	#Обновляем данные по дням(кодам), создаем промежуточную таблицу, в нее записываем данные по дням и далее проходи по всем дням и обновляем
	self._cr.execute("CREATE TEMP TABLE tmp_z (ID int unique, FCAC_RN  int, DAYTYPE_RN int, DATE date);") 
	a = datetime.datetime.strptime(self.time_start_t, '%Y-%m-%d').date()
	for i in self.ids_string:
		self._cr.execute("INSERT INTO tmp_z (id, fcac_rn, daytype_rn, date) SELECT T.id, T.FCAC_RN, T.DAYTYPE_RN, T.DATE FROM tabel_fcacwtd AS T  WHERE T.FCAC_RN = "+str(i.id_fcac.id)+" and T.date::date <='"+str(self.time_end_t)+"' and T.date::date >= '"+str(self.time_start_t)+"' ;")
	i = 1
	while i < 32:
		self._cr.execute("UPDATE tabel_string SET  hours"+str(i)+" = P.nick FROM tabel_daytype AS P WHERE P.id   IN (SELECT tmp_z.DAYTYPE_RN  FROM tmp_z WHERE  tmp_z.FCAC_RN = tabel_string.id_fcac "+" and "+str(self.id)+" =tabel_string.id_tabel  and tmp_z.date::date ='"+a.strftime('%Y-%m-%d')+"') ;")
		a+=datetime.timedelta(days=1)
		i+=1	
	self._cr.execute("DROP TABLE tmp_z;")

    @api.one 
    def action_tabell(self):
	#Добавляем лицевые счета (сотрудники) Нужно сделать через промежуточную таблицу апдейт
	self._cr.execute("INSERT INTO tabel_string (id_fcac,id_tabel) (SELECT T.id,"+str(self.id)+"  FROM tabel_fcac AS T LEFT JOIN (SELECT * from tabel_string WHERE id_tabel="+str(self.id)+") AS P  ON T.id = P.id_fcac  WHERE P.id_fcac IS NULL and T.startdate::date <='"+str(self.time_end_t)+"' and T.enddate::date >= '"+str(self.time_start_t)+"' and T.subdiv_rn = "+str(self.id_division.id)+"   )  ;")

	#Обновляем данные по ставкам
	self._cr.execute("UPDATE tabel_string SET  stqnt = tabel_fcacch.stqnt  FROM tabel_fcacch WHERE  tabel_fcacch.fcacbs_rn = tabel_string.id_fcac "+" and tabel_string.id_tabel = "+str(self.id)+"  ;")

        id_emp_sec=self.pool.get('tabel.string').search(self._cr,self._uid,[('id_tabel','=',self.id)])#получаем ид всех строк из таблице daytype где есть ник
	for i in id_emp_sec:
		model_string= self.pool.get('tabel.string').browse(self._cr, self._uid, i)
		model_string.id_post=model_string.id_fcac.post_rn.id
		model_string.id_tipdol=model_string.id_fcac.tipdol_rn.id
		model_string.id_vidisp=model_string.id_fcac.vidisp_rn.id
		model_string.id_katper=model_string.id_fcac.katper_rn.id
		model_string.id_person=model_string.id_fcac.ank_rn.orgbase_rn.id
#"""
#Вариант 1
#Если бухгалтерия не формирует часы зараннее, то нужно их импортировать из графиков
#Причем в графике указано количество часов за конкретный день для определенного графика работы
#Например для 7.7 часов в день или 8.0 и т.д.
#Обновляем данные по часам"""
	year =  datetime.datetime.strptime(self.time_start_t, '%Y-%m-%d').date().year
	month =  datetime.datetime.strptime(self.time_start_t, '%Y-%m-%d').date().month

	for i in self.ids_string:
		    if i.id_fcac.vidisp_rn.id in [17,14,23,24]:
			i.percent=str(i.stqnt*100)
			continue
		    id_month=self.pool.get('tabel.grmonth').search(self._cr,self._uid,[('month','=',month),('year','=',year),('grrbdc_rn.id','=',i.id_fcac.fcacch_rn.grrbdc_rn)])
		    for j in id_month:
			month_model= self.pool.get('tabel.grmonth').browse(self._cr, self._uid, j)
			self.dayall=month_model.dayall
			c = 1
			while c < 32:
			    id_day= self.pool.get('tabel.grday').search(self._cr,self._uid,[('monthday','=',c),('grmonth_rn','=',month_model.id)])
			    self._cr.execute("UPDATE tabel_string SET  hours"+str(c)+" = NULL  where  tabel_string.id="+str(i.id)+" ;")
			    for k in id_day:
				day= self.pool.get('tabel.grday').browse(self._cr, self._uid, k)
				norma = day.hourinday*i.stqnt
				self._cr.execute("UPDATE tabel_string SET  hours"+str(c)+" = '"+time_format.floatToTime(norma)+"' where  tabel_string.id="+str(i.id)+" ;")
				break
			    c+=1
			break
#"""
#Вариант 2
#Есди бухгалтерия формирует часы, то можно загружать данные из готовых(сформированных) таблиц. 
#В которых есть данные на каждый конкретный день и час для каждого конкретного сотрудника (лицевого счета)
#Очень большая таблица порядка 1.5М строк но работает довольно быстро если проиндексировать
#обновляем данные по часам (если они уже сформированны)
#"""
#        self._cr.execute("CREATE TEMP TABLE tmp_z (ID int unique, FCAC_RN  int, HRTYPE_RN int, HOURQNT double precision, DATE date);")
#        a = datetime.datetime.strptime(self.time_start_t, '%Y-%m-%d').date()
#        for i in self.ids_string:
#		self._cr.execute("INSERT INTO tmp_z (id, fcac_rn, hrtype_rn, hourqnt, date) SELECT T.id, T.FCAC_RN, T.HRTYPE_RN, T.HOURQNT, T.DATE FROM tabel_fcacwth AS T  WHERE T.FCAC_RN ="+str(i.id_fcac.id)+" and T.date::date <='"+str(self.time_end_t)+"' and T.date::date >= '"+str(self.time_start_t)+"' ;")
#        i = 1
#        while i < 32:
#		self._cr.execute("UPDATE tabel_string SET  hours"+str(i)+" = NULL  FROM tmp_z WHERE  tmp_z.FCAC_RN = tabel_string.id_fcac "+" and tabel_string.id_tabel ="+str(self.id)+" ;")
#                self._cr.execute("UPDATE tabel_string SET  hours"+str(i)+" = tmp_z.HOURQNT  FROM tmp_z WHERE  tmp_z.FCAC_RN = tabel_string.id_fcac "+" and tabel_string.id_tabel ="+str(self.id)+" and tmp_z.date::date ='"+a.strftime('%Y-%m-%d')+"' ;")
#                a+=datetime.timedelta(days=1)
#                i+=1
#        self._cr.execute("DROP TABLE tmp_z;")



	#Обновляем данные по дням(кодам), создаем промежуточную таблицу, в нее записываем данные по дням и далее проходи по всем дням и обновляем
	self._cr.execute("CREATE TEMP TABLE tmp_z (ID int unique, FCAC_RN  int, DAYTYPE_RN int, DATE date);") 
	a = datetime.datetime.strptime(self.time_start_t, '%Y-%m-%d').date()
	for i in self.ids_string:
		self._cr.execute("INSERT INTO tmp_z (id, fcac_rn, daytype_rn, date) SELECT T.id, T.FCAC_RN, T.DAYTYPE_RN, T.DATE FROM tabel_fcacwtd AS T  WHERE T.FCAC_RN = "+str(i.id_fcac.id)+" and T.date::date <='"+str(self.time_end_t)+"' and T.date::date >= '"+str(self.time_start_t)+"' ;")
	i = 1
	while i < 32:
		self._cr.execute("UPDATE tabel_string SET  hours"+str(i)+" = P.nick FROM tabel_daytype AS P WHERE P.id   IN (SELECT tmp_z.DAYTYPE_RN  FROM tmp_z WHERE  tmp_z.FCAC_RN = tabel_string.id_fcac "+" and "+str(self.id)+" =tabel_string.id_tabel  and tmp_z.date::date ='"+a.strftime('%Y-%m-%d')+"') ;")
		a+=datetime.timedelta(days=1)
		i+=1	
	self._cr.execute("DROP TABLE tmp_z;")

	#ставим счетчик =0 положение когда в табеле ничего не изменено.
	for r in self.ids_string:
#		r.counter = 0
		r.hours_night = ""
		r.hours_holiday = ""

    #функция start workflow
    @api.one
    def action_draft(self):
	self.signature_boss = ""
	self.signature_tabel = ""
	self.signature_accountant = ""
	self.signature_public_tabel =  ""
	self.signature_public_boss =  ""
	self.signature_public_accountant = ""
	self.ank_signature_tabel = 0
	self.ank_signature_boss = 0
	self.ank_signature_accountant = 0
        self.state = 'draft'

    #Функция хеширования табеля, хэширует весь документ(т.е. каждое поле)
    @api.one
    def action_confirm(self):
	#считаем хеш документа, меняем статус, поле кто подписал(табельщик) уже заполнено автоматически при создании табеля
	self.signature_tabel = compute_hash.compute_hash(self)
        self.state = 'confirmed'

    @api.one
    def action_confirm2(self):
	if self.signature_tabel != compute_hash.compute_hash(self):
		self.check_signature = False
		raise exceptions.ValidationError("Ошибка при валидации подписи нач.отдела")

	#делаем новую подпись на основе старого хеш (валидного) + новый сотрудник
	h = hashlib.sha256()
	h.update(self.signature_tabel)
#	self.ank_signature_boss = self._uid
	h.update(str(self.ank_signature_boss))
	self.signature_boss =  h.hexdigest()
        self.state = 'confirmed2'

    @api.one
    def action_done(self):
	h = hashlib.sha256()
	h.update(compute_hash.compute_hash(self))
	h.update(str(self.ank_signature_boss))
#	raise exceptions.ValidationError(h.hexdigest()+"|"+self.signature_boss)
	if self.signature_boss != h.hexdigest():
		self.check_signature = False
		raise exceptions.ValidationError("Ошибка при валидации подписи (бухгалтера)")

	#делаем новую подпись на основе старого хеш (валидного) + новый сотрудник
	h = hashlib.sha256()
	h.update(self.signature_boss)
#	self.ank_signature_accountant = self._uid
	h.update(str(self.ank_signature_accountant))
	self.signature_accountant =  h.hexdigest()
        self.state = 'done'




    #Всплывающее окошко валидации
    def validation1(self,cr,uid,ids,context):
        if context is None:
            context = {}
	view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'Tabel', 'my_specific_view')[1]
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
	    'view_id': view_id,
#	    'search_view_id':',
            'context': context,
            'res_model': 'tabel.password',
            'nodestroy': True,
#	    'target': 'new',
	    'res_id': False,
	    'create':False,
	}
class Ustring(models.Model):
    _name = 'tabel.ustring'
    id_upload = fields.Many2one('tabel.upload', ondelete='cascade', string="upload_id")
    id_fcac = fields.Many2one('tabel.fcac', ondelete='cascade', string="fcac_id",index=True)
    id_tabel = fields.Many2one('tabel.tabel', ondelete='cascade', string="tabel_id",index=True)
    id_tipdol = fields.Many2one('tabel.tipdol',string="Должность")
    #используется для сортировки по алфавиту,во вью невидимое
    id_person = fields.Many2one('tabel.person',  ondelete='cascade', string="фамилии")
    id_vidisp = fields.Many2one('tabel.vidisp',string="Вид л.с.")
    stqnt = fields.Float(string="Занятые ставки",digits=(12,3))
    id_division = fields.Many2one('tabel.division',  ondelete='cascade', string="Подразделение")
    id_string= fields.Integer( string="id")
    ids_string = fields.Many2one('tabel.string', string="ФИО")

    hours1 = fields.Char(string="1")
    hours2 = fields.Char(string="2")
    hours3 = fields.Char(string="3")
    hours4 = fields.Char(string="4")
    hours5 = fields.Char(string="5")
    hours6 = fields.Char(string="6")
    hours7 = fields.Char(string="7")
    hours8 = fields.Char(string="8")
    hours9 = fields.Char(string="9")
    hours10 = fields.Char(string="10")
    hours11 = fields.Char(string="11")
    hours12 = fields.Char(string="12")
    hours13 = fields.Char(string="13")
    hours14 = fields.Char(string="14")
    hours15 = fields.Char(string="15")
    hours16 = fields.Char(string="16")
    hours17 = fields.Char(string="17")
    hours18 = fields.Char(string="18")
    hours19 = fields.Char(string="19")
    hours20 = fields.Char(string="20")
    hours21 = fields.Char(string="21")
    hours22 = fields.Char(string="22")
    hours23 = fields.Char(string="23")
    hours24 = fields.Char(string="24")
    hours25 = fields.Char(string="25")
    hours26 = fields.Char(string="26")
    hours27 = fields.Char(string="27")
    hours28 = fields.Char(string="28")
    hours29 = fields.Char(string="29")
    hours30 = fields.Char(string="30")
    hours31 = fields.Char(string="31")



    hours_main= fields.Char( string="Основной")
    hours_internal= fields.Char( string="Совместительство")

    hours_sov= fields.Char( string="Совмещение")
    hours_isp= fields.Char( string="Исполнение")
    hours_zon= fields.Char( string="Расш.зона")
    hours_uve= fields.Char( string="Увел.объема")

    hours_all= fields.Char( string="Итого",compute='_compute_all')
    norm_hours = fields.Char (string = "Норма")
    @api.one
    def _compute_all (self):
	self.hours_all="0"
	if self.hours_main:
	    self.hours_all=str(float(time_format.timeToFloat(self.hours_all))+float(time_format.timeToFloat(self.hours_main)))
	if self.hours_internal:
	    self.hours_all=str(float(time_format.timeToFloat(self.hours_all))+float(time_format.timeToFloat(self.hours_internal)))
	if self.hours_sov:
	    self.hours_all=str(float(time_format.timeToFloat(self.hours_all))+float(time_format.timeToFloat(self.hours_sov)))
	if self.hours_isp:
	    self.hours_all=str(float(time_format.timeToFloat(self.hours_all))+float(time_format.timeToFloat(self.hours_isp)))
	if self.hours_zon:
	    self.hours_all=str(float(time_format.timeToFloat(self.hours_all))+float(time_format.timeToFloat(self.hours_zon)))
	if self.hours_uve:
	    self.hours_all=str(float(time_format.timeToFloat(self.hours_all))+float(time_format.timeToFloat(self.hours_uve)))

class Upload(models.Model):
    _name = 'tabel.upload'
    time_start = fields.Date(string="time start of tabel")
    time_end = fields.Date(string="time end of tabel")
    id_division = fields.Many2one('tabel.division',  ondelete='cascade', string="Подразделение")
    ids_ustring = fields.One2many('tabel.ustring', 'id_upload', string="ustring")
    checker = fields.Boolean(string="Выгрузка или численность? (галочка-выгрузка)")


    @api.one 
    def action_upload(self):

	if self.checker == True:
	    if not self.id_division:
		#Добавляем лицевые счета (сотрудники) Нужно сделать через промежуточную таблицу апдейт
		self._cr.execute("INSERT INTO tabel_ustring (id_string,id_upload,id_tipdol,id_person,id_vidisp,stqnt,id_tabel,id_fcac) (SELECT T.id,"+str(self.id)+",T.id_tipdol,T.id_person,T.id_vidisp,T.stqnt,T.id_tabel,T.id_fcac  FROM tabel_string AS T  WHERE  ( (SELECT time_start_t FROM tabel_tabel where tabel_tabel.id= T.id_tabel)::date <='"+str(self.time_end)+"' ) and (SELECT time_end_t FROM tabel_tabel where tabel_tabel.id= T.id_tabel)::date >= '"+str(self.time_start)+"'   )  ;")
	    else:
		#Добавляем лицевые счета (сотрудники) Нужно сделать через промежуточную таблицу апдейт
		self._cr.execute("INSERT INTO tabel_ustring (id_string,id_upload,id_tipdol,id_person,id_vidisp,stqnt,id_tabel,id_fcac) (SELECT T.id,"+str(self.id)+",T.id_tipdol,T.id_person,T.id_vidisp,T.stqnt,T.id_tabel,T.id_fcac  FROM tabel_string AS T  WHERE  ( (SELECT time_start_t FROM tabel_tabel where tabel_tabel.id= T.id_tabel)::date <='"+str(self.time_end)+"' ) and (SELECT time_end_t FROM tabel_tabel where tabel_tabel.id= T.id_tabel)::date >= '"+str(self.time_start)+"' and (SELECT id_division FROM tabel_tabel where tabel_tabel.id= T.id_tabel)="+str(self.id_division.id)+" )  ;")
	else:
	    if not self.id_division:
		#Добавляем лицевые счета (сотрудники) Нужно сделать через промежуточную таблицу апдейт
		self._cr.execute("INSERT INTO tabel_ustring (id_string,id_upload,id_tipdol,id_person,id_vidisp,stqnt,id_tabel,id_fcac) (SELECT T.id,"+str(self.id)+",T.id_tipdol,T.id_person,T.id_vidisp,T.stqnt,T.id_tabel,T.id_fcac  FROM tabel_string AS T  WHERE  ( (SELECT time_start_t FROM tabel_tabel where tabel_tabel.id= T.id_tabel)::date <='"+str(self.time_end)+"' ) and (SELECT time_end_t FROM tabel_tabel where tabel_tabel.id= T.id_tabel)::date >= '"+str(self.time_start)+"' and T.id_vidisp in (5,4,1)  )  ;")
	    else:
		#Добавляем лицевые счета (сотрудники) Нужно сделать через промежуточную таблицу апдейт
		self._cr.execute("INSERT INTO tabel_ustring (id_string,id_upload,id_tipdol,id_person,id_vidisp,stqnt,id_tabel,id_fcac) (SELECT T.id,"+str(self.id)+",T.id_tipdol,T.id_person,T.id_vidisp,T.stqnt,T.id_tabel,T.id_fcac  FROM tabel_string AS T  WHERE  ( (SELECT time_start_t FROM tabel_tabel where tabel_tabel.id= T.id_tabel)::date <='"+str(self.time_end)+"' ) and (SELECT time_end_t FROM tabel_tabel where tabel_tabel.id= T.id_tabel)::date >= '"+str(self.time_start)+"' and T.id_vidisp in (5,4,1) and (SELECT id_division FROM tabel_tabel where tabel_tabel.id= T.id_tabel)="+str(self.id_division.id)+" )  ;")

	for i in self.ids_ustring:
	    #Выбираем из даты отдельно год и месяц для поиска
	    year =  datetime.datetime.strptime(self.time_start, '%Y-%m-%d').date().year
	    month =  datetime.datetime.strptime(self.time_start, '%Y-%m-%d').date().month

	    i.ids_string=i.id_string

	    #Load division
	    if i.id_tabel:
	        id_emp_sec=self.pool.get('tabel.tabel').search(self._cr,self._uid,[('id','=',i.id_tabel.id)])
	        for j in id_emp_sec:
	    	    model_tabel= self.pool.get('tabel.tabel').browse(self._cr, self._uid, j)
	    	    i.id_division=model_tabel.id_division

#################################################################################
#		ВЫГРУЗКА							#
#										#
#										#
#										#
	    if self.checker == True:
		#Считаем часы для выгрузки
		#Каждый вид записываем в соответствующее поле
		if i.id_vidisp.name==u" Совмещение":
		    i.hours_sov=str(float(i.ids_string.hours_main)*i.ids_string.stqnt)
		if i.id_vidisp.name==u" Исполнение обязанностей":
		    i.hours_isp=str(float(i.ids_string.hours_main)*i.ids_string.stqnt)
		if i.id_vidisp.name==u" Расширение зоны обслуживания":
		    i.hours_zon=str(float(i.ids_string.hours_main)*i.ids_string.stqnt)
		if i.id_vidisp.name==u" Увеличение объема работ":
		    i.hours_uve=str(float(i.ids_string.hours_main)*i.ids_string.stqnt)

		#Три вида пишутся в основной
		if i.id_vidisp.name==u" Основной работник":
		    i.hours_main=i.ids_string.hours_main
		if i.id_vidisp.name==u" Внешний совместитель":
		    i.hours_main=i.ids_string.hours_main
		if i.id_vidisp.name==u" Временный работник":
		    i.hours_main=i.ids_string.hours_main

		#" Внутренний совместитель всегда пишется во внутренний
		i.hours_internal=i.ids_string.hours_internal

		#Считаем норму часов для Выгрузки

		id_month=self.pool.get('tabel.grmonth').search(self._cr,self._uid,[('month','=',month),('year','=',year),('grrbdc_rn.id','=',i.ids_string.id_fcac.fcacch_rn.grrbdc_rn)])
	        for j in id_month:
		    month_model= self.pool.get('tabel.grmonth').browse(self._cr, self._uid, j)
		    i.norm_hours=str(0)
		    c = 1
		    while c < 32:
		        id_day= self.pool.get('tabel.grday').search(self._cr,self._uid,[('monthday','=',c),('grmonth_rn','=',month_model.id)])
			for k in id_day:
			    day= self.pool.get('tabel.grday').browse(self._cr, self._uid, k)
			    #считаем норму с учетом сокращенных дней
			    if day.hourinday:
				i.norm_hours=str(float(i.norm_hours)+day.hourinday)
				break
			c+=1				
		
		    #умножаем норму на ставку
		    i.norm_hours=str( float(i.norm_hours)*i.stqnt)
		    break
#################################################################################
#		СРЕДНЕСПИСОЧНАЯ							#
#										#
#										#
#										#
#№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№№#################################################
	    if self.checker == False:
		dayweek =  int(datetime.datetime.strptime(self.time_start, '%Y-%m-%d').date().weekday())
		cnt=dayweek

		id_month=self.pool.get('tabel.grmonth').search(self._cr,self._uid,[('month','=',month),('year','=',year),('grrbdc_rn.id','=',i.ids_string.id_fcac.fcacch_rn.grrbdc_rn)])
		for j in id_month:
			month_model= self.pool.get('tabel.grmonth').browse(self._cr, self._uid, j)
			break

		vidisp= i.id_vidisp.name
		if vidisp:
		    j=1
		    #изменить на то сколько в месяце!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
		    while j<32:
		        #Если в текущий день лицевой счет еще действует, то ставим, иначе поднимаем флаг
		        flagEx = True
		        nowDate =  datetime.datetime.strptime(self.time_start, '%Y-%m-%d').date()
		        nowDate2 =  datetime.datetime.strptime(self.time_end, '%Y-%m-%d').date()
		        fcacDateStart = datetime.datetime.strptime(i.id_fcac.startdate, '%Y-%m-%d').date()
		        fcacDateEnd = datetime.datetime.strptime(i.id_fcac.enddate, '%Y-%m-%d').date()
		        countDays=nowDate2.day
		        if countDays >= j:
			    newdate = nowDate.replace(day=j)
			    if newdate <= fcacDateEnd and newdate >= fcacDateStart:
				    flagEx=True
			    else:
				    flagEx=False
			    #Данные за определенный день, если человек в отпуске без содердания(А),родах(Р) и т.д. то ставку не ставим
			    self._cr.execute("SELECT hours"+str(j)+" FROM tabel_string WHERE tabel_string.id = "+str(i.ids_string.id)+";")
			    a=self._cr.dictfetchone()['hours'+str(j)]
#			    raise exceptions.ValidationError(a)
			    if a:
					if a in [u'А',u'Р', u'ОУ', u'р']:
					    flagEx = False
					else:
					    flagEx = True
			    if flagEx:
	    			id_day= self.pool.get('tabel.grday').search(self._cr,self._uid,[('monthday','=',j),('grmonth_rn','=',month_model.id)])
				#Если не рабочий день (Праздничный или выходной, то берем данные из предыдущего дня)
				if not id_day:
				    if j>1:
					self._cr.execute("UPDATE tabel_ustring SET  hours"+str(j)+" = hours"+str(j-1)+" where tabel_ustring.id = "+str(i.id)+";")
				    else:
					#из первого числа месяца вычитаем 1 и получаем предудущую дату
					date_start =  datetime.datetime.strptime(self.time_start, '%Y-%m-%d').date()
					date_last = date_start - datetime.timedelta(days=1)
					day=int(date_last.day)

					id_string=self.pool.get('tabel.string').search(self._cr,self._uid,[('id_tabel.time_end_t','=',date_last),('id_fcac','=',i.id_fcac.id),('id_vidisp','=',i.id_vidisp.id),('id_tabel.id_division','=',i.id_division.id)])
					if not id_string:
					    self._cr.execute("UPDATE tabel_ustring SET  hours"+str(j)+" = tabel_ustring.stqnt where tabel_ustring.id = "+str(i.id)+";")
					else:
					    for k in id_string:
						#БАЯН БАБАЯН
						model_string= self.pool.get('tabel.string').browse(self._cr, self._uid, k)
						flagLast = True
						if day == 31:
						    if  model_string.hours31  in [u'А',u'Р', u'ОУ', u'р']:
							flagLast = False
						if day == 30:
						    if  model_string.hours30  in [u'А',u'Р', u'ОУ', u'р']:
							flagLast = False
						if day == 29:
						    if  model_string.hours29  in [u'А',u'Р', u'ОУ', u'р']:
							flagLast = False
						if day == 28:
						    if  model_string.hours28  in [u'А',u'Р', u'ОУ', u'р']:
							flagLast = False
						if flagLast:
							self._cr.execute("UPDATE tabel_ustring SET  hours1 = tabel_ustring.stqnt where tabel_ustring.id = "+str(i.id)+";")

						break
#<-----><------><------><------><------>raise exceptions.ValidationError(date_last)

#					raise exceptions.ValidationError(date_last)
				else:
				    self._cr.execute("UPDATE tabel_ustring SET  hours"+str(j)+" = tabel_ustring.stqnt where tabel_ustring.id = "+str(i.id)+";")
				
			
			j=j+1


class Grstring(models.Model):
    _name = 'tabel.grstring'
    _rec_name = 'id_fcac'
    _order = 'tipdol_rn,id_person'
    _inherits = {
		    'tabel.fcac':'id_fcac',
		}
    id_fcac = fields.Many2one('tabel.fcac',required="True",  ondelete='cascade', string="fcac_id")
    #используется для сортировки по алфавиту,во вью невидимое
    id_person = fields.Many2one('tabel.person',  ondelete='cascade', string="фамилии")
    id_tabel = fields.Many2one('tabel.tabel',  ondelete='cascade', string="tabel_id")
    time_start_s = fields.Date (related='id_tabel.time_start_t', string="время начала")


    hours1  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="1")
    hours2  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="2")
    hours3  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="3")
    hours4  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="4")
    hours5  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="5")
    hours6  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="6")
    hours7  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="7")
    hours8  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="8")
    hours9  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="9")
    hours10  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="10")
    hours11  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="11")
    hours12  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="12")
    hours13  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="13")
    hours14  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="14")
    hours15  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="15")
    hours16  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="16")
    hours17  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="17")
    hours18  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="18")
    hours19  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="19")
    hours20  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="20")
    hours21  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="21")
    hours22  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="22")
    hours23  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="23")
    hours24  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="24")
    hours25  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="25")
    hours26  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="26")
    hours27  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="27")
    hours28  = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="28")
    hours29 = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="29")
    hours30 = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="30")
    hours31 = fields.Selection([
         (u'день', u"День"),
         (u'ночь', u"Ночь"),
    ],string="31")
    days_appear = fields.Integer(string="Всего",compute='_compute_days_appear')
    days_night_appear = fields.Integer(string="Ноч",compute='_compute_days_appear')
    def create(self, cr, uid, values, context):
			context = {}
			
			#записываем соответствующее поле персоны при создании записи
			model_fcac= self.pool.get('tabel.fcac').browse(cr, uid, values ['id_fcac'] )
			values ['id_person'] = model_fcac.ank_rn.orgbase_rn.id

			id = super(Grstring, self).create(cr, uid, values)
			return id
    #функция вычисляющая количетсво дней неявок,явок,отработанных часов и т.д.
    @api.depends('hours1','hours2','hours3','hours4','hours5','hours6','hours7','hours8','hours9','hours10','hours11','hours12','hours13','hours14','hours15','hours16','hours17','hours18','hours19','hours20','hours21','hours22','hours23','hours24','hours25','hours26','hours27','hours28','hours29','hours30','hours31')
    def _compute_days_appear(self):
	for record in self:
	    ret=0
	    night=0
	    for j in range(1, 32):
			hours='hours{0}'.format(j)
			if getattr(record, hours):
			    if getattr(record, hours) == u'ночь':
				night+=8
			    ret+=12

	    record.days_appear=ret
	    record.days_night_appear=night




