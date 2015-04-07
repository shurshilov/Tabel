 def action_tabell(self, cr, uid, values, context):
	def getRec():
		for r in self:
			if str (r.id) == str(context['tabel_idd']):
				return r	
	cr.execute("CREATE TEMP TABLE tmp_z (ID int unique, FCAC_RN  int, HRTYPE_RN int, HOURQNT double precision, DATE date);") 
	r = getRec()
	a = datetime.datetime.strptime(r.time_start_t, '%Y-%m-%d').date()	
	
	#for i in r.ids_string:
		#cr.execute("INSERT INTO tmp_z (id, fcac_rn, hrtype_rn, hourqnt, date) SELECT T.id, T.FCAC_RN, T.HRTYPE_RN, T.HOURQNT, T.DATE FROM tabel_fcacwth AS T  WHERE T.FCAC_RN = "+str(i.id_fcac)+" and T.startdate::date <='"+str(self.time_end_t)+"' and T.enddate::date >= '"+str(self.time_start_t)+"' ;")
	#i = 1
	#while i < 30:
	#	cr.execute("UPDATE tabel_string SET  hours"+str(i)+" = tmp_z.HOURQNT  FROM tmp_z WHERE  tmp_z.FCAC_RN = tabel_string.id_fcac "+" and tabel_string.id_tabel = "+str(self.id)+" and tmp_z.date::date ='"+a.strftime('%Y-%m-%d')+"' ;")
	#	a+=datetime.timedelta(days=1)
	#	i+=1	

	cr.execute("DROP TABLE tmp_z;")



######################
   @api.one 
    def action_tabell(self):
	self._cr.execute("UPDATE tabel_string SET  stqnt = tabel_fcacch.stqnt  FROM tabel_fcacch WHERE  tabel_fcacch.fcacbs_rn = tabel_string.id_fcac "+" and tabel_string.id_tabel = "+str(self.id)+"  ;")
	self._cr.execute("CREATE TEMP TABLE tmp_z (ID int unique, FCAC_RN  int, HRTYPE_RN int, HOURQNT double precision, DATE date);") 
	a = datetime.datetime.strptime(self.time_start_t, '%Y-%m-%d').date()
	self.directory=str(len(self))	
	for i in self.ids_string:
		def is_mychar(x):
			return x.isdigit()
		d="".join((x for x in str(i.id_fcac) if is_mychar(x)))
		self._cr.execute("INSERT INTO tmp_z (id, fcac_rn, hrtype_rn, hourqnt, date) SELECT T.id, T.FCAC_RN, T.HRTYPE_RN, T.HOURQNT, T.DATE FROM tabel_fcacwth AS T  WHERE T.FCAC_RN = "+str(d)+" and T.date::date <='"+str(self.time_end_t)+"' and T.date::date >= '"+str(self.time_start_t)+"' ;")
	i = 1
	while i < 30:
		self._cr.execute("UPDATE tabel_string SET  hours"+str(i)+" = tmp_z.HOURQNT  FROM tmp_z WHERE  tmp_z.FCAC_RN = tabel_string.id_fcac "+" and tabel_string.id_tabel = "+str(self.id)+" and tmp_z.date::date ='"+a.strftime('%Y-%m-%d')+"' ;")
		a+=datetime.timedelta(days=1)
		i+=1	

	self._cr.execute("DROP TABLE tmp_z;")
