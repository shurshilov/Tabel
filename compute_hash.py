#!/usr/bin/env python.
# -*- coding: utf-8 -*-
import hashlib
import datetime
def compute_hash (self):
    h = hashlib.sha256()
    h.update(str(self.num_tabel))
    h.update(self.time_start_t)
    h.update(self.time_end_t)
    h.update(str(self.id_ank))
    h.update(str(self.id_division))
    for r in self.ids_string:
		if r.days_appear:
			h.update(r.days_appear.encode('utf8'))
		if r.hours_main:
			h.update(r.hours_main.encode('utf8'))
		if r.hours_night:
			h.update(r.hours_night.encode('utf8'))
		if r.hours_holiday:
			h.update(r.hours_holiday.encode('utf8'))
		if r.hours_internal:
			h.update(r.hours_internal.encode('utf8'))
		if r.days_absences:
			h.update(r.days_absences.encode('utf8'))
		if r.days_absences_sum:
			h.update(str(r.days_absences_sum))

		if r.hours1:
			h.update(r.hours1.encode('utf8'))
                if r.hours2:
                        h.update(r.hours2.encode('utf8'))
                if r.hours3:
                        h.update(r.hours3.encode('utf8'))
                if r.hours4:
                        h.update(r.hours4.encode('utf8'))
                if r.hours5:
                        h.update(r.hours5.encode('utf8'))
                if r.hours6:
                        h.update(r.hours6.encode('utf8'))
                if r.hours7:
                        h.update(r.hours7.encode('utf8'))
                if r.hours8:
                        h.update(r.hours8.encode('utf8'))
                if r.hours9:
                        h.update(r.hours9.encode('utf8'))
                if r.hours10:
                        h.update(r.hours10.encode('utf8'))
                if r.hours11:
                        h.update(r.hours11.encode('utf8'))
                if r.hours12:
                        h.update(r.hours12.encode('utf8'))
                if r.hours13:
                        h.update(r.hours13.encode('utf8'))
                if r.hours14:
                        h.update(r.hours14.encode('utf8'))
                if r.hours15:
                        h.update(r.hours15.encode('utf8'))
                if r.hours16:
                        h.update(r.hours16.encode('utf8'))
                if r.hours17:
                        h.update(r.hours17.encode('utf8'))
                if r.hours18:
                        h.update(r.hours18.encode('utf8'))
                if r.hours19:
                        h.update(r.hours19.encode('utf8'))
                if r.hours20:
                        h.update(r.hours20.encode('utf8'))
                if r.hours21:
                        h.update(r.hours21.encode('utf8'))
                if r.hours22:
                        h.update(r.hours22.encode('utf8'))
                if r.hours23:
                        h.update(r.hours23.encode('utf8'))
                if r.hours23:
                        h.update(r.hours23.encode('utf8'))
                if r.hours24:
                        h.update(r.hours24.encode('utf8'))
                if r.hours25:
                        h.update(r.hours25.encode('utf8'))
                if r.hours26:
                        h.update(r.hours26.encode('utf8'))
                if r.hours27:
                        h.update(r.hours27.encode('utf8'))
                if r.hours28:
                        h.update(r.hours28.encode('utf8'))
                if r.hours29:
                        h.update(r.hours29.encode('utf8'))
                if r.hours30:
                        h.update(r.hours30.encode('utf8'))
                if r.hours31:
                        h.update(r.hours31.encode('utf8'))
    return h.hexdigest()
