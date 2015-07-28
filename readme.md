########################################
#INSTALL Debian Wheezy & Odoo на OpenVZ#
########################################
![Alt text](https://github.com/shurshilov/Tabel/blob/master/screenshots/edit.png "Optional title")
1. Download template from https://openvz.org/Download/template/precreated
2. Install with proxmox (option ip-addr, id, name etc. Connection Bridge)
(my setting of MY debian server, you will have other)
/etc/network/interface  
"

auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
    address  192.168.1.23
    netmask  255.255.255.0
    gateway  192.168.1.1
    broadcast  192.168.1.255
    network 192.168.1.0
    dns-nameservers 192.168.1.14
    dns-search kkokb.local
"
3. apt-get update
4. apt-get insatall mc ( my editor )
5. write to the end of file  /etc/bash.bashrc    "export LANG=ru_RU.utf8" (or your language locale)
6. wget -O - https://nightly.odoo.com/odoo.key | apt-key add -
echo "deb http://nightly.odoo.com/8.0/nightly/deb/ ./" >> /etc/apt/sources.list
apt-get update && apt-get install odoo

########################################
#SETTING Odoo#
########################################
7. Create database in odoo (name, your password etc.)
8. Change timzone on your odoo server (if not identical)
9. Administrator give Tehnic access
10. Copy module Tabel from https://github.com/shurshilov/Tabel to /usr/lib/python2.7/dist-packages/openerp/addons/
11. Update list of local module
12. Install module Tabel
#IMPORT SETTING SCRIPT TO POSTGRES FROM PARUS OR 1C
13. copy file *load_parus.sh to /etc/cron.daily 
14. change path in script to you path base of PARUS or 1C
15. check you /etc/crontab  file you find string ("13 5 * * * root test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily ) ")
16. change in Tabel/import/import.py  password, user, database name
17. start this scrip from your CONTAINER (NOT A HOST!)
#SETTING LDAP
18. Install module ldap
19. Add bind (Odoo ->Setting->Company->setting->LDAP)
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
20. FIX bug of ldap in file /usr/lib/python2.7/dist-packages/openerp/addons/auth_ldap/users_ldap.py
        try:
            conn = self.connect(conf)
            ldap_password = conf['ldap_password'].encode('utf-8') or ''
            conn.simple_bind_s(conf['ldap_binddn'].encode('utf-8') or '', ldap_password.encode('utf-8'))
            results = conn.search_st(conf['ldap_base'].encode('utf-8'), ldap.SCOPE_SUBTREE,
                                     filter, retrieve_attributes, timeout=60)
            conn.unbind()
#reports
21. apt-get install python-setuptools
22. Install aeroolib   python setup.py install from https://github.com/jamotion/aeroolib
23. Install base_field_serialized from https://github.com/jamotion/base_field_serialized
24. Install aeroo https://github.com/jamotion/aeroo
25. apt-get install apt-get install openoffice.org python-genshi python-cairo python-openoffice python-lxml python-uno (install openoffice for pdf,doc)
26. touch /etc/init.d/office
27. write to office
#!/bin/sh
/usr/bin/soffice --nologo --nofirststartwizard --headless --norestore --invisible "--accept=socket,host=localhost,port=8100,tcpNoDelay=1;urp;" &
28. chmod +x /etc/init.d/office
29. update-rc.d office defaults
30. /etc/init.d/office
31. check netstat -tnlp
32. Install report_aeroo_ooo https://github.com/jamotion/report_aeroo_ooo
33. Create reports odoo->settings->aeroo reports
EXAMPLE
name: myreport
model: tabel.tabel
Template Mime-type: ODF Text Document (.odt)
Output Mime-type:Microsoft Word 97/2000/XP (.doc) 
Template source:File
Template path:/usr/lib/python2.7/dist-packages/openerp/addons/Tabel/tabel.odt


OC