#!/usr/bin/env python 
# -*- coding: utf-8 -*-
import compute_hash
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

	fcac_rn = fields.Many2one('tabel.fcac',  ondelete='cascade', string="fcac_id", index = True)
	hrtype_rn = fields.Integer(string="HRTYPE_RN")
	hourqnt = fields.Float(string="chasi hourqnt")
	date =  fields.Date(string="time of hour tabel", index = True)

class Fcacch(models.Model):
	_name = 'tabel.fcacch'
	_rec_name = 'stqnt'
	stqnt = fields.Float(string="stavka stqnt", required=True)
	fcacbs_rn = fields.Integer(string="FCACBS_RN")
    
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
	ank_rn = fields.Many2one('tabel.ank',  ondelete='cascade', string="ank_rn")
	post_rn = fields.Many2one('tabel.post',  ondelete='cascade', string="post_rn")
	subdiv_rn = fields.Many2one('tabel.division',  ondelete='cascade', string="subdiv_rn")
	vidisp_rn = fields.Many2one('tabel.vidisp', ondelete='cascade', string="vidisp_rn")
	startdate = fields.Date(string="time begin of fcac")
	enddate = fields.Date(string="time end of fcac")
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
			
			res.append((emp.id,ank+" "+post+" "+vidisp))
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

    days_appear = fields.Char(string="Дни",compute ='_compute_days_appear')
    hours_main = fields.Char(string="Осн")
    hours_night = fields.Char(string="Ноч")
    hours_holiday = fields.Char(string="Пра")
    hours_internal = fields.Char(string="Вну")
    days_absences = fields.Char (string="Неяв")
    days_absences_sum = fields.Char (string="Сум")
    counter = fields.Integer (string = "Счет", default = 0)

#   поле используемое для вычисления изменений в строке, если они есть то counter > 0
    @api.onchange('hours1','hours2','hours3','hours4','hours5','hours6','hours7','hours8','hours9','hours10','hours11','hours12','hours13','hours14','hours15','hours16','hours17','hours18','hours19','hours20','hours21','hours22','hours23','hours24','hours25','hours26','hours27','hours28','hours29','hours30','hours31','stqnt','id_fcac','hours_night','hours_holiday')
    @api.one
    def _compute_counter (self):
	self.counter = self.counter + 1
	    
    #функция вычисляющая количетсво дней неявок,явок,отработанных часов и т.д.
    @api.depends('hours1','hours2','hours3','hours4','hours5','hours6','hours7','hours8','hours9','hours10','hours11','hours12','hours13','hours14','hours15')
    @api.depends('hours16','hours17','hours18','hours19','hours20','hours21','hours22','hours23','hours24','hours25','hours26','hours27','hours28','hours29','hours30','hours31')
    def _compute_days_appear(self):

	def floatToTime (a):#перевод из десятичного в часы:минуты
	    a = float(a)*60
	    minutes = int (a%60)
	    hours = int (a/60)
	    return str(hours)+":"+str(minutes)

	def timeToFloat (a):#перевод из часы:минуты в десятичное
	    time= a.split(':')
	    hours = float (time[0])
	    minutes = float (time[1])
	    t = hours*60.0 + minutes
	    t = t/60
	    return t

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
                vidisp1 = u' Внутренний совместитель'#если внутренний совместитель то считаются часы не основные а внутренние

		def sum (a):
		    current_model = self.pool.get('tabel.tabel').browse(self._cr, self._uid, record.id_tabel.id,self._context)

		    if a:
			    if a.find(':')>=0:
				a = timeToFloat(a)
			    if record.hours_internal.find(':')>=0:
				record.hours_internal = timeToFloat (record.hours_internal)
			    if record.hours_main.find(':')>=0:
				record.hours_main = timeToFloat (record.hours_main)

			    try:#проверяем если в поле число значит считаем часы
				float(a)
				float(record.hours_main)
				float(record.hours_internal)
				flag = 1
				for i in range ( 0,  min ( len (vidisp), len (vidisp1) ) ):
				    if vidisp[i] != vidisp1[i] :
					flag =0
					break

				if flag == 1:#считаем внутренние
				    if current_model.format:#сморим какой нужен формат вывода
					record.hours_internal = floatToTime (float(record.hours_internal)+ float(a))
				    else:
					record.hours_internal = str (float(record.hours_internal)+ float(a))
				else:
				    if current_model.format:#смотрим какой нужен формат вывода
				        record.hours_main = floatToTime (float(record.hours_main)+ float(a))
				    else:
				        record.hours_main = str (float(record.hours_main)+ float(a))

				record.days_appear = str (int(record.days_appear) + 1)#в любом случае это явка

				if current_model.format:#сморим какой нужен формат вывода
				    return floatToTime(a)
				return a

			    except ValueError:#если встретили код
				a=a.replace(' ', '')
				d_abse[a]=d_abse[a]+1#добавляем в словарь кода 1
				record.days_absences_sum= str(int(record.days_absences_sum)+1)#добавляем неявку
				record.days_absences = " "#пересчитываем строку кодов. т.к. может быть добавлен еще код
				for i in d_abse:
				    if d_abse[i]>0:
					record.days_absences=record.days_absences+ i+u'/'+str(d_abse[i]).decode('utf-8')+u'; '
				return a

		record.hours1 =sum (record.hours1)
                record.hours2 =sum (record.hours2)
                record.hours3 =sum (record.hours3)
                record.hours4 =sum (record.hours4)
                record.hours5 =sum (record.hours5)
		record.hours6 =sum (record.hours6)
                record.hours7 =sum (record.hours7)
                record.hours8 =sum (record.hours8)
                record.hours9 =sum (record.hours9)
                record.hours10 =sum (record.hours10)
                record.hours11 =sum (record.hours11)
                record.hours12 =sum (record.hours12)
                record.hours13 =sum (record.hours13)
                record.hours14 =sum (record.hours14)
                record.hours15 =sum (record.hours15)
                record.hours16 =sum (record.hours16)
                record.hours17 =sum (record.hours17)
                record.hours18 =sum (record.hours18)
                record.hours19 =sum (record.hours19)
                record.hours20 =sum (record.hours20)
                record.hours21 =sum (record.hours21)
                record.hours22 =sum (record.hours22)
                record.hours23 =sum (record.hours23)
                record.hours24 =sum (record.hours24)
                record.hours25 =sum (record.hours25)
                record.hours26 =sum (record.hours26)
                record.hours27 =sum (record.hours27)
                record.hours28 =sum (record.hours28)
                record.hours29 =sum (record.hours29)
                record.hours30 =sum (record.hours30)
		record.hours31 =sum (record.hours31)
		if record.days_absences_sum == "0":
			    record.days_absences_sum = " "
		if record.days_appear == "0":
			     record.days_appear = " "
		if record.hours_main == "0.0":
			    record.hours_main = " "
		if record.hours_internal == "0.0":
			    record.hours_internal = " "
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

    format = fields.Boolean (string = "десятичные/минуты", default = True)
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



#    @api.one
#    def action_tabel(self):
#	#Нужно сделать через промежуточную таблицу апдейт
#	self._cr.execute("INSERT INTO tabel_string (id_fcac,id_tabel) (SELECT T.id,"+str(self.id)+"  FROM tabel_fcac AS T LEFT JOIN (SELECT * from tabel_string WHERE id_tabel="+str(self.id)+") AS P  ON T.id = P.id_fcac  WHERE P.id_fcac IS NULL and T.startdate::date <='"+str(self.time_end_t)+"' and T.enddate::date >= '"+str(self.time_start_t)+"' and T.subdiv_rn = "+str(self.id_division.id)+"   )  ;")

    @api.one 
    def action_tabell(self):
	#Нужно сделать через промежуточную таблицу апдейт
	self._cr.execute("INSERT INTO tabel_string (id_fcac,id_tabel) (SELECT T.id,"+str(self.id)+"  FROM tabel_fcac AS T LEFT JOIN (SELECT * from tabel_string WHERE id_tabel="+str(self.id)+") AS P  ON T.id = P.id_fcac  WHERE P.id_fcac IS NULL and T.startdate::date <='"+str(self.time_end_t)+"' and T.enddate::date >= '"+str(self.time_start_t)+"' and T.subdiv_rn = "+str(self.id_division.id)+"   )  ;")

	#Обновляем данные по ставкам, в текущем табеле
	
	self._cr.execute("UPDATE tabel_string SET  stqnt = tabel_fcacch.stqnt  FROM tabel_fcacch WHERE  tabel_fcacch.fcacbs_rn = tabel_string.id_fcac "+" and tabel_string.id_tabel = "+str(self.id)+"  ;")
	
        #тоже самое с часами
        self._cr.execute("CREATE TEMP TABLE tmp_z (ID int unique, FCAC_RN  int, HRTYPE_RN int, HOURQNT double precision, DATE date);")
        a = datetime.datetime.strptime(self.time_start_t, '%Y-%m-%d').date()
	#self.directory=str(len(self))
        for i in self.ids_string:
                self._cr.execute("INSERT INTO tmp_z (id, fcac_rn, hrtype_rn, hourqnt, date) SELECT T.id, T.FCAC_RN, T.HRTYPE_RN, T.HOURQNT, T.DATE FROM tabel_fcacwth AS T  WHERE T.FCAC_RN ="+str(i.id_fcac.id)+" and T.date::date <='"+str(self.time_end_t)+"' and T.date::date >= '"+str(self.time_start_t)+"' ;")
        i = 1
	
        while i < 30:
		self._cr.execute("UPDATE tabel_string SET  hours"+str(i)+" = NULL  FROM tmp_z WHERE  tmp_z.FCAC_RN = tabel_string.id_fcac "+" and tabel_string.id_tabel ="+str(self.id)+" ;")
                self._cr.execute("UPDATE tabel_string SET  hours"+str(i)+" = tmp_z.HOURQNT  FROM tmp_z WHERE  tmp_z.FCAC_RN = tabel_string.id_fcac "+" and tabel_string.id_tabel ="+str(self.id)+" and tmp_z.date::date ='"+a.strftime('%Y-%m-%d')+"' ;")
                a+=datetime.timedelta(days=1)
                i+=1
	#ставим счетчик =0 положение когда в табеле ничего не изменено.
	for r in self.ids_string:
		r.counter = 0
		r.hours_night = ""
		r.hours_holiday = ""
        self._cr.execute("DROP TABLE tmp_z;")



	#Обновляем данные по дням(кодам), создаем промежуточную таблицу, в нее записываем данные по дням и далее проходи по всем часам и обновляем
	self._cr.execute("CREATE TEMP TABLE tmp_z (ID int unique, FCAC_RN  int, DAYTYPE_RN int, DATE date);") 
	a = datetime.datetime.strptime(self.time_start_t, '%Y-%m-%d').date()
	#self.directory=str(len(self))
	for i in self.ids_string:
		self._cr.execute("INSERT INTO tmp_z (id, fcac_rn, daytype_rn, date) SELECT T.id, T.FCAC_RN, T.DAYTYPE_RN, T.DATE FROM tabel_fcacwtd AS T  WHERE T.FCAC_RN = "+str(i.id_fcac.id)+" and T.date::date <='"+str(self.time_end_t)+"' and T.date::date >= '"+str(self.time_start_t)+"' ;")
	i = 1
	while i < 30:
		self._cr.execute("UPDATE tabel_string SET  hours"+str(i)+" = P.nick FROM tabel_daytype AS P WHERE P.id =  (SELECT tmp_z.DAYTYPE_RN  FROM tmp_z WHERE  tmp_z.FCAC_RN = tabel_string.id_fcac "+" and tabel_string.id_tabel = "+str(self.id)+" and tmp_z.date::date ='"+a.strftime('%Y-%m-%d')+"') ;")
		a+=datetime.timedelta(days=1)
		i+=1	
	self._cr.execute("DROP TABLE tmp_z;")

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



