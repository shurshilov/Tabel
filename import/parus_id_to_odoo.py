#!/usr/bin/env python 
# -*- coding: UTF-8 -*-
charDict = {
	'1': 1,
	'2': 2,
	'0': 0, 
	'3': 3, 
	'4': 4, 
	'5': 5, 
	'6': 6, 
	'7': 7, 
	'8': 8, 
	'9': 9, 
	'A': 10, 
	'B': 11, 
	'C': 12, 
	'D': 13, 
	'E': 14, 
	'F': 15, 
	'G': 16, 
	'H': 17, 
	'I': 18, 
	'J': 19, 
	'K': 20, 
	'L': 21, 
	'M': 22, 
	'N': 23, 
	'O': 24, 
	'P': 25, 
	'Q': 26, 
	'R': 27, 
	'S': 28, 
	'T': 29, 
	'U': 30, 
	'V': 31, 
	'W': 32, 
	'X': 33, 
	'Y': 34, 
	'Z': 35, 
	'a': 36, 
	'b': 37, 
	'c': 38, 
	'd': 39, 
	'e': 40, 
	'f': 41, 
	'g': 42, 
	'h': 43, 
	'i': 44, 
	'j' :45, 
	'k': 46, 
	'l': 47, 
	'm': 48, 
	'n': 49, 
	'o': 50, 
	'p': 51, 
	'q': 52, 
	'r': 53, 
	's': 54, 
	't': 55, 
	'u': 56, 
	'v': 57, 
	'w': 58, 
	'x': 59, 
	'y': 60, 
	'z': 61, 
	u'\u0430': 62, 
	u'\u0431': 63, 
	u'\u0432': 64, 
	u'\u0433': 65, 
	u'\u0434': 66, 
	u'\u0435': 67, 
	u'\u0451': 68, 
	u'\u0436': 69, 
	u'\u0437': 70, 
	u'\u0438': 71, 
	u'\u0439': 72, 
	u'\u043a': 73, 
	u'\u043b': 74, 
	u'\u043c': 75, 
	u'\u043d': 76, 
	u'\u043e': 77, 
	u'\u043f': 78, 
	u'\u0440': 79, 
	u'\u0441': 80, 
	u'\u0442': 81, 
	u'\u0443': 82, 
	u'\u0444': 83, 
	u'\u0445': 84, 
	u'\u0446': 85, 
	u'\u0447': 86, 
	u'\u0448': 87, 
	u'\u0449': 88, 
	u'\u044a': 89, 
	u'\u044b': 90, 
	u'\u044c': 91, 
	u'\u044d': 92, 
	u'\u044e': 93, 
	u'\u044f': 94, 
	u'\u0410': 95, 
	u'\u0411': 96, 
	u'\u0412': 97, 
	u'\u0413': 98, 
	u'\u0414': 99, 
	u'\u0415': 100, 
	u'\u0401': 101, 
	u'\u0416': 102, 
	u'\u0417': 103, 
	u'\u0418': 104, 
	u'\u0419': 105, 
	u'\u041a': 106, 
	u'\u041b': 107, 
	u'\u041c': 108, 
	u'\u041d': 109, 
	u'\u041e': 110, 
	u'\u041f': 111, 
	u'\u0420': 112, 
	u'\u0421': 113, 
	u'\u0422': 114, 
	u'\u0423': 115, 
	u'\u0424': 116, 
	u'\u0425': 117, 
	u'\u0426': 118, 
	u'\u0427': 119, 
	u'\u0428': 120, 
	u'\u0429': 121, 
	u'\u042a': 122, 
	u'\u042b': 123, 
	u'\u042c': 124, 
	u'\u042d': 125, 
	u'\u042e': 126, 
	u'\u042f': 127
}
 


def recalcChar(char):
	global charDict
        return charDict[char]
#def returnValue (value):
#	a ="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZабвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
#	return a.find(value)

def parusIndexToOdoo (value):
	summ=0
	j=0
	for i in value[::-1]:
		summ+=recalcChar(i)*128**j
		j+=1
	return summ
#print parusIndexToOdoo ("ЯЯЯЯ".decode('utf8'))