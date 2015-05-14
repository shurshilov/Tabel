#!/usr/bin/env python 
# -*- coding: utf-8 -*-
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
		for i in id_person:
			id_ank=self.pool.get('tabel.ank').search(cr,uid,[('orgbase_rn.id','=',i)])
			#ищем текущий лицевой счет сотрудника
			for k in id_ank:
			    id_fcac=self.pool.get('tabel.fcac').search(cr,uid,[('ank_rn.id','=',k),('enddate','=',datetime.date(8888, 12, 31))])
			    #далее из модели берем ид отдела
			    for j in id_fcac:
				id_div = self.pool.get('tabel.fcac').browse(cr, uid, j)
				mas = id_div.subdiv_rn
				result[user.id]= id_div.subdiv_rn.id
				return result
    _columns = {
	'ids_division': openerp.osv.fields.function(_get_emp_ids,method=True,string='Сотрудник',type='many2one',store=False,relation='tabel.division',help='Employee'),
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
		code_private=context['password']
		user_id=context['user_id']
                code_private=code_private.upper()[:8]
                vals = {}
                vals ['user_id']=user_id
                vals ['password']=code_private

                check_flag=False
                id_emp_sec=self.pool.get('tabel.password').search(cr,uid,[('user_id.id','=',uid)])
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
                                recs.signal_workflow('confirm')
                        if(context['state']=='confirm2'):
                                recs.signal_workflow('confirm2')
                        if(context['state']=='done'):
                                recs.signal_workflow('done')

			return {
			'type':'ir.actions.act_window_close',
				}
                else:
                        raise exceptions.ValidationError("Не правильный пароль(Повторите ввод)!")


class Grday (models.Model):
	_name = 'tabel.grday'

	grmonth_rn = fields.Many2one('tabel.grmonth', ondelete='cascade',string="GRMONTH_RN",index=True)
	monthday = fields.Integer(string="MONTHDAY",index=True)
	hourinday = fields.Float(string="HOUR IN DAY")

class Grmonth (models.Model):
	_name = 'tabel.grmonth'
	_rec_name = 'grrbdc_rn'
	
	grrbdc_rn = fields.Many2one('tabel.grrbdc', ondelete='cascade',string="GRRBDC_RN",index=True)
	year = fields.Integer(string="YEAR",index=True)
	month = fields.Integer(string="MONTH",index=True)
	dayall = fields.Integer(string="DAYALL")
	hourall = fields.Float(string="HOURALL")

class Grrbdc (models.Model):
	_name = 'tabel.grrbdc'

	code = fields.Char(string="CODE")
	name = fields.Char(string="NAME")
	daysmean = fields.Float(string="DAYSMEAN")
	hourmean = fields.Float(string="HOURMEAN")
	workweek = fields.Integer(string="WORKWEEK")
	daysmin = fields.Float(string="DAYSMIN")
	hourmin = fields.Float(string="HOURMIN")

class Daytype(models.Model):
	_name = 'tabel.daytype'
	
	nick = fields.Char(string="nick of Vidisp")
	name = fields.Char(string="name of Vidisp")
	
class Fcacwtd(models.Model):
	_name = 'tabel.fcacwtd'
	
	fcac_rn = fields.Many2one('tabel.fcac',  ondelete='cascade', string="fcac_id")
	daytype_rn = fields.Many2one('tabel.daytype',  ondelete='cascade', string="daytype_id")
	date=  fields.Date(string="time of day tabel", index = True)

class Fcacwth(models.Model):
	_name = 'tabel.fcacwth'
	_rec_name = 'hourqnt'

	fcac_rn = fields.Many2one('tabel.fcac',  ondelete='cascade', string="fcac_id")
	hrtype_rn = fields.Integer(string="HRTYPE_RN")
	hourqnt = fields.Float(string="chasi hourqnt")
	date =  fields.Date(string="time of hour tabel", index = True)

class Fcacch(models.Model):
	_name = 'tabel.fcacch'
	_rec_name = 'stqnt'
	stqnt = fields.Float(string="stavka stqnt", required=True)
	fcacbs_rn = fields.Integer(string="FCACBS_RN",index=True)
	grrbdc_rn = fields.Integer(string="grrbdc_rn")
    
class Vidisp(models.Model):
	_name = 'tabel.vidisp'

	code = fields.Char(string="code of Vidisp", required=True)
	name = fields.Char(string="name of Vidisp", required=True)
class Post(models.Model):
	_name = 'tabel.post'

	name = fields.Char(string="name of Post", required=True)
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

	@api.depends('firstname')
	def _compute_first (self):
		for record in self:
		    if type (record.firstname) != bool:
			if len(record.firstname) >1:
				record.initials_first = " "+record.firstname [1]+". "
			else:
			    record.full_name = "пусто"
		    else:
			record.full_name = "пусто"


	@api.depends('secondname')
        def _compute_second (self):
		for record in self:
		    if type (record.secondname) != bool:
			if len (record.secondname) >1:
				record.initials_second = record.secondname [1]+". "

class Ank(models.Model):
	_name = 'tabel.ank'
	_rec_name = 'orgbase_rn'
	_order = 'orgbase_rn'
	orgbase_rn = fields.Many2one('tabel.person',  ondelete='cascade', string="orgbase_rn")
	tab_num = fields.Integer(string="TAB_NUM")
	jobbegin = fields.Date(string="time begin of work")
	jobend = fields.Date(string="time end of work")
class Fcac(models.Model):
	_name = 'tabel.fcac'

	#name = fields.Char(compute='_compute_name')
	_rec_name = 'ank_rn'
	_order = 'ank_rn'
	fcacch_rn =fields.One2many('tabel.fcacch', 'fcacbs_rn', string="fcacch_rn")
	ank_rn = fields.Many2one('tabel.ank',  ondelete='cascade', string="ank_rn")
	post_rn = fields.Many2one('tabel.post',  ondelete='cascade', string="post_rn",index=True)
	subdiv_rn = fields.Many2one('tabel.division',  ondelete='cascade', string="subdiv_rn")
	vidisp_rn = fields.Many2one('tabel.vidisp', ondelete='cascade', string="vidisp_rn",index =True)
	startdate = fields.Date(string="time begin of fcac")
	enddate = fields.Date(string="time end of fcac")
#	stqnt = fields.One2many ('tabel.fcacch',)
	def name_get(self, cr, uid, ids, context):         
        	if not len(ids):
        	    return []
        	res=[]
        	for emp in self.browse(cr, uid, ids,context=context):

			post = ""
			for line in emp.post_rn:
				post=line.name
			ank = ""
			for line in emp.ank_rn:
				for r in line.orgbase_rn:
					ank=r.surname+r.initials_first+r.initials_second	
			vidisp = ""
			for line in emp.vidisp_rn:
				vidisp=line.name	
			
			res.append((emp.id,ank))
	        #res.sort()
		return res

class Division(models.Model):
    _name = 'tabel.division'

    name = fields.Char(string="name of Division", required=True)

class String(models.Model):
    _name = 'tabel.string'
    _rec_name = 'id_fcac'
    _order = 'id_fcac'

#    _defaults = {'order_line': lambda obj, cr, uid, context: '/',}
    id_fcac = fields.Many2one('tabel.fcac',  ondelete='cascade', string="fcac_id")
    id_tabel = fields.Many2one('tabel.tabel',  ondelete='cascade', string="tabel_id")
    id_post = fields.Char(string="должность")
    id_vidisp = fields.Char(string="вид л.с.")
    stqnt = fields.Float(string="ставка")

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
    counter = fields.Integer (string = "Счет", default = 0)
    percent = fields.Char (string = "Прц")

    complet = fields.Char (string = "Разнести")

    def fields_view_get(self, cr, uid,context, view_id=None, view_type='form', toolbar=False, submenu=False):
#	 for i in self:
#	    i.counter=1
#        raise osv.except_osv('info ',str(context['ids_string'][0][1]))
	 
	 result = super(String, self).fields_view_get(cr, uid, view_id, view_type,context, toolbar, submenu)
         # use lxml to compose the arch XML
         arch=result['arch']
         fields = result['fields']
         tb = {'print': [], 'action': [], 'relate': []}
         if view_type=='search':
             return result
         if view_type=='form':
             #return result
            #raise osv.except_osv('info ',str(result['fields']))
	    arch = ''' <form string="Analytic" >
            <group>
        <field name="id_fcac" string="ФИО" readonly= "True"/>
        <field name="id_vidisp" string="вид л.с." readonly= "True"/>
        <field name="id_post" string="должность" readonly= "True"/>
        <field name="stqnt" string="кол-во ст." readonly= "True"/>
        </group>
        <table>
            <tr>
            <th>сумма дней</th>
            <th>основные </th>
            <th>внутренние</th>
            <th>неявки</th>
            <th>сумма неявок</th>
            <th>проценты</th>
            <th>ночные</th>
            <th>праздничные</th>
            </tr>
        <tr>
        <td><field name="days_appear" string ="сумма дней"/> </td>
        <td><field name="hours_main" string="Основные часы"/> </td>
        <td><field name="hours_internal" string="Внутренние часы"/> </td>
        <td><field name="days_absences" string="Неявки"/> </td>

        <td><field name="days_absences_sum" string="Сумма Неявок"/> </td>
        <td><field name="percent"/> </td>
        <td><field name="hours_night"/> </td>
        <td><field name="hours_holiday"/></td>
        </tr>
        </table>

	<table border="3" bordercolor="#7C7BAD">
	<tr>
	<th><p align="center">Понедельник</p></th>
        <th><p align="center">Вторник</p></th>
        <th><p align="center">Среда</p></th>
        <th><p align="center">Четверг</p></th>
        <th><p align="center">Пятница</p></th>
        <th><p align="center">Суббота</p></th>
        <th><p align="center">Воскресенье</p></th>
        </tr>
             '''
	    time=context['time_start_t']
	    dayweek =  int(datetime.datetime.strptime(time, '%Y-%m-%d').date().weekday())
	    cnt=dayweek
	    for i in range (1,32):
		if i == 1:
		    arch+=''' <tr>  '''
		    for j in range (0,dayweek):
			arch+=''' <td></td>  '''
		if cnt%7 == 0:
		    arch+=''' </tr> <tr> '''
		if cnt%7 == 6 or cnt%7 == 5:
		    arch+=''' <td bgcolor="#EADEE0"><p align="center"><b><font color="#7C7BAD">''' +str(i)+'''</font></b></p>  <field name="hours%s" string="%s. %s" /></td> '''%(i,i,i)
		else:
		    arch+=''' <td><p align="center"><b><font color="#7C7BAD">''' +str(i)+'''</font></b></p>  <field name="hours%s" string="%s. %s" /></td> '''%(i,i,i)
		if i==31:
		    arch+=''' </tr>  '''
		cnt=cnt+1
	    arch+=''' </table>
			<table>
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
         return result

#   поле используемое для вычисления изменений в строке, если они есть то counter > 0
    @api.depends('hours1','hours2','hours3','hours4','hours5','hours6','hours7','hours8','hours9','hours10','hours11','hours12','hours13','hours14','hours15','hours16','hours17','hours18','hours19','hours20','hours21','hours22','hours23','hours24','hours25','hours26','hours27','hours28','hours29','hours30','hours31','stqnt','id_fcac','hours_night','hours_holiday')
    @api.one
    def _compute_counter (self):
	self.counter = self.counter + 1
#функция разнести
    @api.one
    def compute_complet (self):
		    self.hours1= self.complet
            	    self.hours2= self.complet
            	    self.hours3= self.complet
            	    self.hours4= self.complet
            	    self.hours5= self.complet
		    self.hours6= self.complet
            	    self.hours7= self.complet
            	    self.hours8= self.complet
            	    self.hours9= self.complet
            	    self.hours10= self.complet
            	    self.hours11= self.complet
            	    self.hours12= self.complet
            	    self.hours13= self.complet
            	    self.hours14= self.complet
            	    self.hours15= self.complet
            	    self.hours16= self.complet
            	    self.hours17= self.complet
            	    self.hours18= self.complet
            	    self.hours19= self.complet
            	    self.hours20= self.complet
            	    self.hours21= self.complet
            	    self.hours22= self.complet
            	    self.hours23= self.complet
            	    self.hours24= self.complet
            	    self.hours25= self.complet
            	    self.hours26= self.complet
            	    self.hours27= self.complet
            	    self.hours28= self.complet
            	    self.hours29= self.complet
            	    self.hours30= self.complet
		    self.hours31= self.complet

    @api.one
    @api.depends('id_fcac','post_rn','vidisp_rn')
    def _compute_post_vidisp (self):
	self.id_post=self.id_fcac.post_rn.name
	self.id_vidisp=self.id_fcac.vidisp_rn.code
    #функция вычисляющая количетсво дней неявок,явок,отработанных часов и т.д.
    @api.depends('hours1','hours2','hours3','hours4','hours5','hours6','hours7','hours8','hours9','hours10','hours11','hours12','hours13','hours14','hours15')
    @api.depends('hours16','hours17','hours18','hours19','hours20','hours21','hours22','hours23','hours24','hours25','hours26','hours27','hours28','hours29','hours30','hours31')
    def _compute_days_appear(self):

	def floatToTime (a):#перевод из десятичного в часы:минуты
	    a = float(a)*60
	    minutes = a%60
	    hours =  a/60
	    if int(round(minutes)) < 10:
		return str(int(hours))+":0"+str(int(round (minutes)))
	    else:
		return str(int(hours))+":"+str(int(round(minutes)))

	def timeToFloat (a):#перевод из часы:минуты в десятичное
	    time= a.split(':')
	    hours = float (time[0])
	    minutes = float (time[1])
	    t = hours*60.0 + minutes
	    t = t/60
	    return round(t,3)

	def timeToFloat2 (a):#перевод из часы:минуты в десятичное
	    time= a.split(',')
	    hours = float (time[0])
	    minutes = float (time[1])
	    t = hours*60.0 + minutes*6.0
	    t = t/60
	    return round(t,3)

        id_emp_sec=self.pool.get('tabel.daytype').search(self._cr,self._uid,[('nick','!=','')])#получаем ид всех строк из таблице daytype где есть ник
	model_daytype= self.pool.get('tabel.daytype').browse(self._cr, self._uid, id_emp_sec)


	for record in self:
		record.days_absences_sum = "0"#количество дней неявок в сумме
		record.days_absences = " "#строка неявок в формате (код/кол-во;)
		record.days_appear = "0"#дни явок в сумме
		record.hours_main = "0.0"#количество основных отработанных часов
		record.hours_internal= "0.0"#количество внутренних(совместительство) отработанных часов

		d_abse ={}#заполняем словарь из кодов неявок для дальнейшего подсчета
		for r in model_daytype:
		    a = r.nick.replace (' ','')
		    d_abse[a] = 0
		vidisp = record.id_fcac.vidisp_rn.name
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
			    if a.find(':')>=0 or a.find(',')>=0:
				if a.find(':')>=0:
				    a =timeToFloat(a)
				else:
				    a = timeToFloat2(a)
			    
			    try:#проверяем если в поле число значит считаем часы
				float(a)
			    except ValueError:#если встретили код
				a=a.replace(' ', '')
				flagEx = True#показываем что уже был посчитан код
				if a in d_abse:
				    d_abse[a]=d_abse[a]+1#добавляем в словарь кода 1
				    record.days_absences_sum= str(int(record.days_absences_sum)+1)#добавляем неявку
				    record.days_absences = " "#пересчитываем строку кодов. т.к. может быть добавлен еще код
				    for i in d_abse:#генерируем строку неявок код/число неявок
					if d_abse[i]>0:
					    record.days_absences=record.days_absences+ i+u'/'+str(d_abse[i]).decode('utf-8')+u'; '

			    if flagEx==False:#если у нас число то пересчитываем основные или внутренние часы. переводим в числа.

				if record.hours_internal.find(':')>=0:
				    record.hours_internal = timeToFloat (record.hours_internal)
				if record.hours_main.find(':')>=0:
				    record.hours_main = timeToFloat (record.hours_main)

				if flag == 1:#считаем внутренние
				#    if current_model.format:#сморим какой нужен формат вывода
				#	record.hours_internal = floatToTime (float(record.hours_internal)+ float(a))
				#    else:
					record.hours_internal = str (float(record.hours_internal)+ float(a))
				else:
				#    if current_model.format:#сморим какой нужен формат вывода
				#	record.hours_main = floatToTime (float(record.hours_main)+ float(a))
				#    else:
			    		record.hours_main = str (float(record.hours_main)+ float(a))
				record.days_appear = str (int(record.days_appear) + 1)#в любом случае это явка




		    summ (record.hours1)
            	    summ (record.hours2)
            	    summ (record.hours3)
            	    summ (record.hours4)
            	    summ (record.hours5)
		    summ (record.hours6)
            	    summ (record.hours7)
            	    summ (record.hours8)
            	    summ (record.hours9)
            	    summ (record.hours10)
            	    summ (record.hours11)
            	    summ (record.hours12)
            	    summ (record.hours13)
            	    summ (record.hours14)
            	    summ (record.hours15)
            	    summ (record.hours16)
            	    summ (record.hours17)
            	    summ (record.hours18)
            	    summ (record.hours19)
            	    summ (record.hours20)
            	    summ (record.hours21)
            	    summ (record.hours22)
            	    summ (record.hours23)
            	    summ (record.hours24)
            	    summ (record.hours25)
            	    summ (record.hours26)
            	    summ (record.hours27)
            	    summ (record.hours28)
            	    summ (record.hours29)
            	    summ (record.hours30)
		    summ (record.hours31)

		    if record.days_absences_sum == "0":
			    record.days_absences_sum = " "
		    if record.days_appear == "0":
			     record.days_appear = " "
		    if record.hours_main == "0.0":
			    record.hours_main = " "
		    if record.hours_internal == "0.0":
			    record.hours_internal = " "
		    if record.percent:
			record.days_appear= " "

class Password(models.Model):

	_name = 'tabel.password' 
	#функция для дефаулта юзера (идет во вьюху с валидацией простой подписи)
	def user(self):
        	return self._uid

	user_id = fields.Many2one('res.users','Пользователь',default = user)
	password = fields.Char(string="password")
	#перед тем как сохранить пароль берем от него хеш и сохраняем не сам пароль а хеш
	def create(self, cr, uid, values, context):
		if  context['state']=='create':
			context = {}
			vals = {}
			h = hashlib.sha256()
			code_private=values['password']
			user_id=values['user_id']
			#8 - change len to dynamic!!!
			code_private=code_private.upper()[:8]
			h.update(code_private)
			vals ['user_id']=user_id
			vals ['password']=h.hexdigest()
			id = super(Password, self).create(cr, uid, vals, context=None)
			return id

		id = super(Password, self).create(cr, uid, values)
		return id


class Tabel(models.Model):
    _name = 'tabel.tabel'
    
    #_rec_name = 'id_ank'
    #_order = 'id_ank'

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

    signature_tabel      =  fields.Char(string="signature tabel")
    signature_boss       =  fields.Char(string="signature boss")
    signature_accountant =  fields.Char(string="signature accountant")
    check_signature = fields.Boolean(string="проверка подписи",default=True)#для пользователей сырой документ считается валидным.
#    ank_signature_tabel      = fields.Many2one('tabel.ank', string="имя сотрудника подписи (табельщик)")
    ank_signature_boss       = fields.Many2one('res.users', string="имя сотрудника подписи (нач.отдела)")
    ank_signature_accountant = fields.Many2one('res.users', string="имя сотрудника подписи (бухгалтер)")

    format = fields.Boolean (string = "десятичные/минуты", default = False)
    num_tabel = fields.Integer(string="number of Tabel")
    time_start_t = fields.Date(string="time start of tabel", default = time_first)
    time_end_t = fields.Date(string="time end of tabel", default = time_last)
    id_ank = fields.Many2one('tabel.ank',  ondelete='cascade', string="ank_id", required=True,default= ank_default, order ='surname')
    ids_string = fields.One2many('tabel.string', 'id_tabel', string="string",  limit = 500)
    state = fields.Selection([
         ('draft', "Не подписанный"),
         ('confirmed', "Подписанный табельщиком"),
	 ('confirmed2', "Подписанный нач.отдела"),
         ('done', "На исполнение"),
    ])
    id_division = fields.Many2one('tabel.division',  ondelete='cascade', string="division_id", required=True,default= div_default)
    dayall = fields.Integer(string="Количество рабочих дней в месяце")

    @api.one
    def time_button (self):
	if self.format:
		self.format = False
	else:
		self.format = True
	time_format.time_format (self)

    #Обновить данные по пропускам(приказам),если появился новый сотрудник или больничный или отпуск и т.д. то данные обновятся не стирая введеные часы
    @api.one
    def action_tabel(self):
	#Добавляем лицевые счета (сотрудники) Нужно сделать через промежуточную таблицу апдейт
	self._cr.execute("INSERT INTO tabel_string (id_fcac,id_tabel) (SELECT T.id,"+str(self.id)+"  FROM tabel_fcac AS T LEFT JOIN (SELECT * from tabel_string WHERE id_tabel="+str(self.id)+") AS P  ON T.id = P.id_fcac  WHERE P.id_fcac IS NULL and T.startdate::date <='"+str(self.time_end_t)+"' and T.enddate::date >= '"+str(self.time_start_t)+"' and T.subdiv_rn = "+str(self.id_division.id)+"   )  ;")
	#Обновляем данные по ставкам
	self._cr.execute("UPDATE tabel_string SET  stqnt = tabel_fcacch.stqnt  FROM tabel_fcacch WHERE  tabel_fcacch.fcacbs_rn = tabel_string.id_fcac "+" and tabel_string.id_tabel = "+str(self.id)+"  ;")

	#обновляем данные вдолжности и виды л.с.
	self._cr.execute("UPDATE tabel_string SET  id_post = tabel_post.name  FROM tabel_post WHERE  tabel_post.id = (SELECT tabel_fcac.post_rn FROM tabel_fcac WHERE tabel_fcac.id = tabel_string.id_fcac  "+" and tabel_string.id_tabel = "+str(self.id)+")  ;")
	self._cr.execute("UPDATE tabel_string SET  id_vidisp = tabel_vidisp.code  FROM tabel_vidisp WHERE  tabel_vidisp.id = (SELECT tabel_fcac.vidisp_rn FROM tabel_fcac WHERE tabel_fcac.id = tabel_string.id_fcac  "+" and tabel_string.id_tabel = "+str(self.id)+")  ;")

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

	#обновляем данные вдолжности и виды л.с.
	self._cr.execute("UPDATE tabel_string SET  id_post = tabel_post.name  FROM tabel_post WHERE  tabel_post.id = (SELECT tabel_fcac.post_rn FROM tabel_fcac WHERE tabel_fcac.id = tabel_string.id_fcac  "+" and tabel_string.id_tabel = "+str(self.id)+")  ;")
	self._cr.execute("UPDATE tabel_string SET  id_vidisp = tabel_vidisp.code  FROM tabel_vidisp WHERE  tabel_vidisp.id = (SELECT tabel_fcac.vidisp_rn FROM tabel_fcac WHERE tabel_fcac.id = tabel_string.id_fcac  "+" and tabel_string.id_tabel = "+str(self.id)+")  ;")

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
				self._cr.execute("UPDATE tabel_string SET  hours"+str(c)+" = "+str(norma)+" where  tabel_string.id="+str(i.id)+" ;")
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
		r.counter = 0
		r.hours_night = ""
		r.hours_holiday = ""

    #функция start workflow
    @api.one
    def action_draft(self):
	self.signature_boss = ""
	self.signature_tabel = ""
	self.signature_accountant = ""
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
	self.ank_signature_boss = self._uid
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
	self.ank_signature_accountant = self._uid
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



