########################################
#SCREENSHOTS WORK OF MODULE TABEL#
########################################
![Alt text](https://github.com/shurshilov/Tabel/blob/master/screenshots/edit.png "Optional title")
![Alt text](https://github.com/shurshilov/Tabel/blob/master/screenshots/view_form.png "Optional title")
![Alt text](https://github.com/shurshilov/Tabel/blob/master/screenshots/password_validation.png "Optional title")
![Alt text](https://github.com/shurshilov/Tabel/blob/master/screenshots/graph_example.png "Optional title")
![Alt text](https://github.com/shurshilov/Tabel/blob/master/screenshots/tree_view.png "Optional title")

====== INSTALL Debian Wheezy & Odoo на OpenVZ ======
  * 1. Download template from https://openvz.org/Download/template/precreated
  * 2. Install with proxmox (option ip-addr, id, name etc. Connection Bridge)
  (my setting of MY debian server, you will have other)
   /etc/network/interface  
   
''  auto lo
  iface lo inet loopback
  auto eth0
  iface eth0 inet static
    address  192.168.1.23
    netmask  255.255.255.0
    gateway  192.168.1.1
    broadcast  192.168.1.255
    network 192.168.1.0
    dns-nameservers 192.168.1.14
    dns-search kkokb.local''
 
  * 3.apt-get update
  * 4.apt-get insatall mc ( my editor )
  * 5.write to the end of file  /etc/bash.bashrc    "export LANG=ru_RU.utf8" (or your language locale)

  wget -O - https://nightly.odoo.com/odoo.key | apt-key add -
  echo "deb http://nightly.odoo.com/8.0/nightly/deb/ ./" >> /etc/apt/sources.list
  apt-get update && apt-get install odoo

----
====== SETTING Odoo ======
  * 1. Create database in odoo (name, your password etc.)
  * 2. Change timzone on your odoo server (if not identical)
  * 3. Administrator give Tehnic access
  * 4. Copy module Tabel from https://github.com/shurshilov/Tabel to /usr/lib/python2.7/dist-packages/openerp/addons/
  * 5. Update list of local module
  * 6. Install module Tabel

----
====== IMPORT SETTING SCRIPT TO POSTGRES FROM PARUS OR 1C ======
  * 1. copy file *load_parus.sh to /etc/cron.daily 
  * 2. change path in script to you path base of PARUS or 1C
  * 3. check you /etc/crontab  file you find string ("13 5 * * * root test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily ) ")
  * 4. change in Tabel/import/import.py  password, user, database name
  * 5. start this scrip from your CONTAINER (NOT A HOST!)

----
====== SETTING LDAP ======
  * 1. Install module ldap
  * 2. Add bind (Odoo ->Setting->Company->setting->LDAP)
EXAMPLE
adress LDAP server:192.168.1.14
LDAP binddn:cn=ldap dokuwiki,cn=users,dc=kkokb,dc=local
LDAP base:ou=Отдел информатизации,dc=kkokb,dc=local
Port server LDAP: 389
Password LDAP: your pass
Filter LDAP: sAMAccountName=%s
Template use: Demo User
Create User: yes
Sequence: 1
Use TLS: no
  * 3. FIX bug of ldap in file /usr/lib/python2.7/dist-packages/openerp/addons/auth_ldap/users_ldap.py
        try:
            conn = self.connect(conf)
            ldap_password = conf['ldap_password'].encode('utf-8') or ''
            conn.simple_bind_s(conf['ldap_binddn'].encode('utf-8') or '', ldap_password.encode('utf-8'))
            results = conn.search_st(conf['ldap_base'].encode('utf-8'), ldap.SCOPE_SUBTREE,
                                     filter, retrieve_attributes, timeout=60)
            conn.unbind()

----
====== Reports ======
  * 1. apt-get install python-setuptools
  * 2. Install aeroolib   python setup.py install from https://github.com/jamotion/aeroolib
  * 3. Install base_field_serialized from https://github.com/jamotion/base_field_serialized
  * 4. Install aeroo https://github.com/jamotion/aeroo
  * 5. apt-get install apt-get install openoffice.org python-genshi python-cairo python-openoffice python-lxml python-uno (install openoffice for pdf,doc)
  * 6. Создаем отчеты через графический интерфейс odoo->settings->aeroo reports

----
===== Import table in postgreSQL =====
== Для того чтобы импортировать таблицы из модуля Табель в График или наоборот или в другую систему надо выполнить 2 команды. ==
  * 1.Сделать бекап таблицы pg_dump -a -t tabel_password -f password openerp   (Здесь делается бекап таблицы паролей в файл password из БД openerp под пользователем postgres)
  * 2. Восстановить таблицу в другой базе или модуле psql -U postgres -d openerp -f password восстанавливает все таблицы из файла password. Для того чтобы перекинуть в другой модуль например из Табель в График, надо отредактировать файл изменить название таблицы например с tabel_password на graph_password)))