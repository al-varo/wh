
from os.path import expanduser
from pyfiglet import Figlet

import os
import time
import urllib2
import socket
import locale

import psycopg2
import sqlite3

locale.setlocale(locale.LC_ALL, '')
SERVER = "192.168.88.251"
WEBPORT = 8069
TIMEOUT = 3
RETRY = 1 

home=expanduser("~")+"/manzada/"
"""
SERVER="0.0.0.0"
try:
   SERVER="192.168.88.251"
   data = urllib2.urlopen("http://manzada.store/manzada-offline/srv.txt") 
   if(data):
        for srv in data:
            SERVER=srv
except Exception as e:
    #print(e)
    SERVER="192.168.88.251"
finally:
    print "Terhubung dengan ramdan@"+SERVER
"""

qry_sale_order="SELECT id,client_order_ref,date_order,partner_id,state,user_id,name,(SELECT name FROM res_partner where id=so.partner_id) as nama_toko, (SELECT coalesce(max(function), 'Belum di input') FROM res_partner where id=so.partner_id) as jalur,amount_total::TEXT FROM sale_order so WHERE state='progress' AND date_order > CURRENT_DATE - INTERVAL '3' day;"
qry_sale_order_line="""
SELECT id,product_uos_qty::TEXT,((price_unit*product_uos_qty)-(discount/100))::TEXT as netto,name,state::TEXT,order_partner_id,order_id,write_date::TEXT,product_id,salesman_id,order_line_id,(SELECT p_induk FROM product_template WHERE id=(SELECT product_tmpl_id FROM product_product WHERE id=sol.product_id)) AS posisi,(select name from product_uom where id=sol.product_uom) as satuan FROM sale_order_line sol 
WHERE order_id IN (SELECT id FROM sale_order WHERE date_order > CURRENT_DATE - INTERVAL '3' day 
AND state='progress') AND state='confirmed';
"""
qry_simpan_sale_order_o="INSERT INTO sale_order_o (id,client_order_ref,date_order,partner_id,state,user_id,name,nama_toko,jalur,amount_total) VALUES \
                                          (?,?,?,?,?,?,?,?,?,?)"
qry_simpan_sale_order_line_o="INSERT INTO sale_order_line_o (id,product_uos_qty,netto,name,state,order_partner_id,order_id,write_date,product_id,salesman_id,order_line_id,posisi,satuan) VALUES \
                                          (?,?,?,?,?,?,?,?,?,?,?,?,?)"

def tcpCheck(ip, port, timeout):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((ip, int(port)))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except:
        return False
    finally:
        s.close()

def check_SERVER(ip, port, timeout, retry):
    ipup = False
    for i in range(retry):
        if tcpCheck(ip, port, timeout):
            ipup = True
            break
        else:
            print("Tidak terhubung...")
            time.sleep(timeout)
    return ipup

def tarikData(qry):
    conn_serv=False
    record=False
    try:
        conn_serv=psycopg2.connect(user="offline",
	    		  password="ra#asia",
			  host=SERVER,
			  port="5432",
			  database="manzada")
        cursor=conn_serv.cursor()
        cursor.execute(qry)
        record=cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        print(error)
        return False
    finally:
        if(conn_serv):
            cursor.close()
            conn_serv.close()
            return record

def buatData():
    conn_sqlite=False
    try:
        conn_sqlite = sqlite3.connect("{}offline.db".format(home))
        clite=conn_sqlite.cursor()
        clite.execute("DROP TABLE IF EXISTS sale_order_o")
        clite.execute("DROP TABLE IF EXISTS sale_order_line_o")
        clite.execute("CREATE TABLE IF NOT EXISTS sale_order_o (\
                      id integer PRIMARY KEY, \
                      client_order_ref text, \
                      date_order date, \
                      partner_id integer, \
                      state text, \
                      user_id integer, \
                      name text, \
                      nama_toko text, \
                      jalur text, \
                      amount_total integer, \
                      cetak integer default 0)")
        clite.execute("CREATE TABLE IF NOT EXISTS sale_order_line_o (\
                      id integer PRIMARY KEY, \
                      product_uos_qty integer, \
                      netto integer, \
                      name text, \
                      state text, \
                      order_partner_id integer, \
                      order_id integer, \
                      write_date text, \
                      product_id integer, \
                      salesman_id integer, \
                      order_line_id integer, \
                      posisi integer, \
                      satuan text)")
        clite.execute("CREATE TABLE IF NOT EXISTS status_print (\
                      order_name text, \
                      printed integer default 0)")
        conn_sqlite.commit()
    except (Exception, sqlite3.Error) as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))
        return False
    finally:
        if(conn_sqlite):
            clite.close()
            conn_sqlite.close()
            return True

def simpanData(qry, record):
    conn_sqlite=False
    try:
        conn_sqlite = sqlite3.connect("{}offline.db".format(home))
        clite=conn_sqlite.cursor()
        clite.executemany(qry, record)
        conn_sqlite.commit()
    except (Exception, sqlite3.Error) as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))
        return False
    finally:
        if(conn_sqlite):
            clite.close()
            conn_sqlite.close()
            return True

def checkData(qry):
    conn_sqlite=False
    try:
        record=0
        conn_sqlite = sqlite3.connect("{}offline.db".format(home))
        clite=conn_sqlite.cursor()
        clite.execute(qry)
        record=clite.fetchone()
    except (Exception, sqlite3.Error) as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))
        return 0
    finally:
        if(conn_sqlite):
            clite.close()
            conn_sqlite.close()
            return record[0]

if __name__ == '__main__':
    tipe=""
    status_select=True
    status_simpan=True
    f = Figlet(font='isometric2')
    print f.renderText('BOY')+"boy@lambertus"
    print("Menghubungi ramdan@{}...".format(SERVER))
    if check_SERVER(SERVER, WEBPORT, TIMEOUT, RETRY):
        print("Gagal menghubungi ramdan, SERVER offline.")
    else:
        print("Terhubung dengan ramdan.")
    print("")
    print("Memulai sinkronisasi data dari SERVER...")
    record_sale_order=tarikData(qry_sale_order)
    if(record_sale_order):
        print("Tarik S.O\t\t[OK]")
    else:
        status_select=False
        print("Tarik S.O\t\t[Gagal]")
    record_sale_order_line=tarikData(qry_sale_order_line)
    if(record_sale_order_line):
        print("Tarik Baris S.O\t\t[OK]")
    else:
        status_select=False
        print("Tarik Baris S.O\t\t[Gagal]")
    print("")
    if(status_select):
       print("Menyimpan data pada HDD lokal...")
       if(buatData()):
           print("Membuat Table\t\t[OK]")
       else:
           status_simpan=False
       record_old_so=checkData("select COUNT(*) from sale_order_o;")
       record_old_so_line=checkData("select COUNT(*) from sale_order_line_o;")
       if(simpanData(qry_simpan_sale_order_o, record_sale_order)):
           updated_so=0
           record_new_so=checkData("SELECT COUNT(*) FROM sale_order_o;")
           total_so=checkData("SELECT SUM(amount_total) FROM sale_order_o;")
           updated_so=record_new_so-record_old_so
           print("Simpan S.O\t\t[OK]\tUpdated[{}] Nilai Total: {}".format(updated_so,locale.format('%d', total_so, 1)))
       else:
           status_simpan=False
           print("Simpan S.O\t\t[Gagal]")
       if(simpanData(qry_simpan_sale_order_line_o, record_sale_order_line)):
           updated_so_line=0
           record_new_so_line=checkData("SELECT COUNT(*) FROM sale_order_line_o;")
           total_so_line=checkData("SELECT SUM(netto) FROM sale_order_line_o;")
           updated_so_line=record_new_so_line-record_old_so_line
           print("Simpan Baris S.O\t[OK]\tUpdated[{}] Nilai Total: {}".format(updated_so_line, locale.format('%d', total_so_line, 1)))
       else:
           status_simpan=False
           print("Simpan Baris S.O\t[Gagal]")
       if(status_simpan):
           print("")
           if total_so==total_so_line:
              print("Selamat!. Seluruh data berhasil disimpan dengan integrity 100%.")
           else:
              print("Nilai S.O dan Baris S.O berbeda, sangat disarankan untuk tarik data ulang")
       else:
           print("")
           print("Ada beberapa kegagalan disaat menyimpan data.")
           print("Disarankan untuk mengulangi menarik data")
    else:
       print("Ada kegagalan ketika menarik data dari SERVER")
       print("Kemungkinan bisa disebabkan oleh:")
       print("1. Jaringan internet Anda bermasalah")
       print("2. Anda tidak memiliki hak akses ke SERVER")
       print("3. SERVER Offline")
    print("")
