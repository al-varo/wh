from os.path import expanduser
from pyfiglet import Figlet

import os
import time
import urllib2
import socket
import locale
import pdfkit
import os.path

import psycopg2
import sqlite3

locale.setlocale(locale.LC_ALL, '')
SERVER = "192.168.88.251"
WEBPORT = 8069
TIMEOUT = 3
RETRY = 1

home=expanduser("~")+"/manzada/"

qry_get_jalur="SELECT lower(jalur) FROM sale_order_o WHERE date(date_order)=date('now','localtime') group by lower(jalur);"
qry_get_so="SELECT id, name, nama_toko, lower(jalur),user_id FROM sale_order_o WHERE date(date_order)=date('now','localtime') AND lower(jalur)=lower('{}') AND lower(nama_toko)!='pelanggan umum'"
qry_get_so_ids="SELECT id FROM sale_order_o WHERE date(date_order)=date('now','localtime') AND lower(jalur)=lower('{}')"
qry_get_so_line="SELECT name, product_uos_qty, satuan FROM sale_order_line_o WHERE order_id={} order by name"
qry_get_global="SELECT posisi, name, SUM(product_uos_qty), satuan FROM sale_order_line_o WHERE order_id IN ({}) GROUP BY name ORDER BY posisi"

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

def getData(qry):
    conn_sqlite=False
    record=""
    try:
        conn_sqlite = sqlite3.connect("{}offline.db".format(home))
        clite=conn_sqlite.cursor()
        #clite.row_factory = lambda cursor, row: row[0]
        clite.execute(qry)
        record=clite.fetchall()
    except (Exception, sqlite3.Error) as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        print("Exception class is: ", er.__class__)
        print('SQLite traceback: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))
        return record
    finally:
        if(conn_sqlite):
            clite.close()
            conn_sqlite.close()
            return record

def printAll():
    style1="""
        <html>
            <head>
                <style>
                    @font-face {
                        font-family: "Arial";
                    }
        """
    style2="""
        src: url("file:///home/boy/manzada/arial.ttf");
        """.format(home)
    style3="""
                @media print {
                    .page {
                         page-break-before: always;
                    }
                }
                #pos {
                    font-family: "Arial";
                    margin: 0;
                    margin-left: 30px !important;
                    margin-right: 20px !important;
                    border: none !important;
                    font-size: 16px !important;
                    width: 210mm !important;}
                #myTable {
                    font-family: Arial;
                    font-size:16px;
                    border-collapse: collapse;
                    width: 100%;}
                #myTable td, #myTable th {
                    border: 1px solid #ddd;
                    padding: 5px;}
                #myTable tr:nth-child(even){
                    background-color: #f2f2f2;}
                #myTable tr:hover {
                    background-color: #ddd;}
                #myTable th {
                    padding-top: 10px;
                    padding-bottom: 10px;
                    background-color: #4c6aaf;
                    color: white;}
            </style>
        </head>
        <body>
        """
    so_page="""
        <div style = "display:block; clear:both; page-break-after:always;">'
            <div id="pos">
                <table id="myTable">
                    <tr>
                        <td>
<pre>
{} {}     Jalur : {}    Sales : {}</pre>
                        </td>
                    </tr>
                    <tr>
                        <th>Nama Barang</th>
                        <th>Kuantitas</th>
                        <th>Satuan</th>
                    </tr>
                    {}
                </table>
            </div>
        </div>
        """
    intro_mark="""
        <div style = "display:block; clear:both; page-break-after:always;">'
            <div id="pos">
                <table id="myTable">
                  <tr>
                    <td colspan="4"><h2>Arsip Aktifitas Loading - CV. LAMBERTUS MANJADDA</h2></td> 
                  </tr>
                  <tr>
                    <td colspan="4"><h3>By boy@lambertus (Automated) Tgl : 12-11-2021</h3></td></tr>
                </table>
            </div>
        </div>
    """

    jalur_mark="""
        <div style = "display:block; clear:both; page-break-after:always;">'
            <div id="pos">
                <table id="myTable">
                  <tr>
                    <td colspan="4"><h2>Jalur : {}</h2></td> 
                  </tr>
                  {}
                </table>
            </div>
        </div>
    """
    global_mark="""
        <div style = "display:block; clear:both; page-break-after:always;">'
            <div id="pos">
                <table id="myTable">
                  <tr>
                    <td colspan="4"><h2>Global Item - Jalur : {}</h2></td>
                  </tr>
                  {}
                </table>
            </div>
        </div>
    """

    footer="""
       </body>"""
    html=""
    html_complete=""
    jalur=getData(qry_get_jalur)
    #print(', '.join(['"{}"'.format(value) for value in jalur]))
    #so_ids=getData(qry_get_so_ids.format(', '.join(['"{}"'.format(value) for value in jalur])))
    #print(str(so_ids))
    text_so=""
    text_so_line=""
    jalur_tmp=""
    jalur_page=""
    global_page=""
    sales=""
    #print(jalur)
    for row_jalur in jalur:
        print(row_jalur[0])
        sale_order_record=getData(qry_get_so.format(row_jalur[0]))
        #sale_order=', '.join(['"{}"'.format(value) for value in sale_order_record])
        for row_so in sale_order_record:
            user_id=row_so[4]
            if user_id==5:
                sales='Zul'
            if user_id==9:
                sales='Agus'
            if user_id==31:
                sales='Ahmad'
            if user_id==7:
                sales='Tedi'
            if user_id==44:
                sales='Agung'
            if user_id==25:
                sales='Yogi'
            if user_id==56:
                sales='Adi'
            if row_jalur[0] != jalur_tmp:
                sos=""
                posisi="None"
                so_sales=""
                sor=""
                sor_ids=""
                global_line=""
                sor=getData(qry_get_so.format(row_jalur[0]))
                sor_ids_r=getData(qry_get_so_ids.format(row_jalur[0]))
                for row in sor_ids_r:
                   sor_ids=sor_ids+str(row[0])+','
                print(sor_ids[:-1])
                for row in sor:
                   so_num=row[1]
                   so_toko=row[2]
                   if row[4]==5:
                       so_sales='Zul'
                   if row[4]==9:
                      so_sales='Agus'
                   if row[4]==31:
                      so_sales='Ahmad'
                   if row[4]==7:
                      so_sales='Tedi'
                   if row[4]==44:
                      so_sales='Agung'
                   if row[4]==25:
                      so_sales='Yogi'
                   if row[4]==56:
                      so_sales='Adi'
                   sos=sos+"<tr><td>{}</td><td>{}</td><td align='right'>{}</td></tr>".format(so_num,so_toko,so_sales)
                sol_global=getData(qry_get_global.format(sor_ids[:-1]))
                for row in sol_global:
                   if row[0]==1:
                      posisi="Atas"
                   if row[0]==2:
                      posisi="Bawah"
                   if row[0]==3:
                      posisi="Office"
                   nama_item=row[1]
                   kuantitas=row[2]
                   satuan=row[3]
                   global_line=global_line+"<tr><td>{}</td><td>{}</td><td>{}</td><td align='right'>{}</td></tr>".format(posisi,nama_item,kuantitas,satuan)
                jalur_page=jalur_mark.format(row_jalur[0],sos)
                global_page=global_mark.format(row_jalur[0],global_line)
                global_line=""
            else:
                jalur_page="" 
                global_page=""
            id_so=row_so[0]
            sale_order_line_record=getData(qry_get_so_line.format(id_so))
            no_so=row_so[1]
            toko_so=row_so[2]
            jalur_so=row_so[3]
            for row_so_line in sale_order_line_record:
                nama=row_so_line[0]
                qty=row_so_line[1]
                satuan=row_so_line[2]
                #text_so_line=text_so_line+"{}\t{}\t{}".format(nama,qty,satuan)+'\n'
                text_so_line=text_so_line+"<tr><td>{}</td><td>{}</td><td align='right'>{}</td></tr>".format(nama,qty,satuan)
            #text_so=text_so+jalur_page+str(id_so)+no_so+'\t'+toko_so+'\t'+jalur_so+'\n'+text_so_line+'\n'
            html=html+jalur_page+global_page+so_page.format(no_so,toko_so,jalur_so,sales,text_so_line)
            jalur_tmp=row_jalur[0]
            text_so_line=""
    html_complete=style1+style2+style3+intro_mark+html+footer
    fileout = open("/home/boy/manzada/html-table.htm", "w")
    fileout.writelines(html_complete)
    fileout.close()
    options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'dpi': '300',
            'custom-header' : [
                               ('Accept-Encoding', 'gzip')
                              ]
            }
    if(os.path.isfile("/home/boy/manzada/html-table.htm")):
        pdfkit.from_file("/home/boy/manzada/html-table.htm", "/home/boy/manzada/load.pdf", options=options)
        os.remove("/home/boy/manzada/html-table.htm")
    else:
        exit()
    print(html)
if __name__ == '__main__':
    printAll()
