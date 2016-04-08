#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import paramiko
import socket
from socket_utils import *
import gnupg


class PCClient():

    def __init__(self, server='193.168.8.2', port=8089):
        self.DEF_SERVER = 'pgp.mit.edu'
        self.server = server
        self.port = port
        self.pgp = gnupg.GPG(gnupghome='./.gpg')
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientsocket.connect((self.server, self.port))
        # self.password = ''
        # self.remotepath = '/root/home/email/to_encrypt/'
        # self.username = 'root'
        # if not localhost:
        #     self.server = server
        # else:

    # def send_file(self, file):
    #     ssh = paramiko.SSHClient()
    #     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #     f_path = file
    #     ssh.connect(self.server, username=self.username, password=self.password)
    #     sftp = ssh.open_sftp()
    #     sftp.put(f_path, '%s%s' % (self.remotepath, f_path))
    #     sftp.close()
    #     ssh.close()

    # def send_data(self, data):
    #     ssh = paramiko.SSHClient()
    #     ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #     f_path = 'my-unencrypted.txt'
    #     open(f_path, 'w').write(data)
    #     ssh.connect(self.server, username=self.username, password=self.password)
    #     sftp = ssh.open_sftp()
    #     sftp.put(f_path, '%s%s' % (self.remotepath, f_path))
    #     sftp.close()
    #     ssh.close()
    #     os.remove(f_path)

    def send(self, data, mode, email= None):
        # clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # clientsocket.connect((self.server, self.port))
        if mode is 'ENC':
            send_one_enc(self.clientsocket, data)
            print 'Sending email to PGP device...'
            send_one_enc(self.clientsocket, email)
            key = self.search_key(email)
            send_one_enc(self.clientsocket, key)
            print 'Sending pub to PGP device...'

        elif mode is 'DEC':
            send_one_dec(self.clientsocket, data)

        elif mode is 'VFY':
            send_one_vrf(self.clientsocket, data)

        elif mode is 'SGN':
            send_one_sgn(self.clientsocket, data)

        done = False
        while not done:
            buf = recv_one_message(self.clientsocket)
            print buf
            if buf['mode'] == 2 and len(buf['data']) > 0:
                if len(buf['data']) > 0:
                    print "Received response:\n" + str(buf['data'])
                    data =  str(buf['data'])
                    done = True
        print data
        return data

    def search_key(self, email, key_server=None):
        if key_server is None:
        #     # key_server = 'hkps.pool.sks-keyservers.net'
            key_server = self.DEF_SERVER
        print 'Searching key for %s in %s' % (email, key_server)
        key = self.pgp.search_keys(email, key_server)
        key_data = None
        if len(key) > 0:
            for k in key:
                import_result = []
                # print k['uids'][0]
                if email in str(k['uids'][0]):
                    print 'Imporing pub for %s' % str(k['uids'][0])
                    kid = k['keyid']
                    import_result = self.pgp.recv_keys( self.DEF_SERVER, kid)
                    key_data = self.pgp.export_keys(kid)
        return key_data

    def recv_key_to_upload(self, key_server=None):
        if key_server is None:
        #     # key_server = 'hkps.pool.sks-keyservers.net'
            key_server = self.DEF_SERVER
        send_one_upload_key(self.clientsocket, ':D')
        buf = recv_one_message(self.clientsocket)
        key_data = buf['data']
        if key_data != 'Uploaded':
            kid = self.pgp.import_keys(key_data).results[0]['fingerprint']
            print 'Sending pub to %s' % key_server
            self.pgp.send_keys(key_server, kid)

    def send_ciphertext(self, data):
        return self.send(data, 'DEC')

    def send_plaintext(self, data, email):
        return self.send(data, 'ENC', email=email)

    def send_verify(self, data):
        return self.send(data, 'VFY')

    def send_sign(self, data):
        return self.send(data, 'SGN')

# if  __name__ == '__main__':
    # pc = PCClient('localhost')
    # print pc.search_key('santiago9101@gmail')
#     email = '''
#     <html><head><meta http-equiv=3D"Content-Type" content=3D"text/html =
#     charset=3Dutf-8"></head><body style=3D"word-wrap: break-word; =
#     -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" =
#     class=3D"">They told me that they are almost done (10 min) and I need 20 =
#     to the university.<div class=3D"">Is there any other option, i.e., go to =
#     Delf next week</div><div class=3D""><br class=3D""></div><div =
#     class=3D"">Best&nbsp;<br class=3D""><div><blockquote type=3D"cite" =
#     class=3D""><div class=3D"">El 18/03/2016, a las 3:55 p.m., Christian =
#     Doerr &lt;<a href=3D"mailto:santiago9101@me.com" =
#     class=3D"">santiago9101@gmail.com</a>&gt; escribi=C3=B3:</div><br =
#     class=3D"Apple-interchange-newline"><div class=3D""><span =
#     style=3D"font-family: Helvetica; font-size: 12px; font-style: normal; =
#     font-variant: normal; font-weight: normal; letter-spacing: normal; =
#     orphans: auto; text-align: start; text-indent: 0px; text-transform: =
#     none; white-space: normal; widows: auto; word-spacing: 0px; =
#     -webkit-text-stroke-width: 0px; float: none; display: inline =
#     !important;" class=3D"">n their room, be nice to them and ask them to =
#     adopt you.</span><br style=3D"font-family: Helvetica; font-size: 12px; =
#     font-style: normal; font-variant: normal; font-weight: normal; =
#     letter-spacing: normal; orphans: auto; text-align: start; text-indent: =
#     0px; text-transform: none; white-space: normal; widows: auto; =
#     word-spacing: 0px; -webkit-text-stroke-width: 0px;" =
#     class=3D""></div></blockquote></div><br class=3D""></div></body></html>=
#     '''
#     sign = '''Content-Transfer-Encoding: 7bit
# Content-Type: text/plain;
#     charset=us-ascii

# asdasdasdasdadsadasdasd
# -----BEGIN PGP SIGNATURE-----
# Comment: GPGTools - https://gpgtools.org

# iQIcBAEBCgAGBQJXA7f8AAoJELleHttpVgRP9xkP/1tb4wFKfBraYmByzONdjTfO
# tog2eksLg0BPfehyoBx0apJT2WPXRGlqcMINIY3CMa6tXCQAfb+XqtOIkk2kuvPw
# JJeiFSAYgv7VQJ64B04wj9aL4Vl7RoMYWE83SYftnLrpN8jQAf68BhI+sjfojIk1
# kCmm0YT0Z75etJXhsssfTQJv3sbLwWRoZdVyvB0pe1McElW9sThijtAGyLR9rFBT
# o5yi8nEjx9ifwsmTenb6GJ3v3KZFxeM5r8vOGCYkd2p7aBBoTnUYindb/TKaNrsf
# HvJy2Dx8v3+bmDcAortp+MeL7rjPzdsfpNq5oWMn3RpFjuORt5Af62rRbmMKlfVp
# /HYVz3df+coa53sxc2fuJsWIB4VGZYq7qTTqFqIpZT0VYoU1OQwbSU9V+O5L67/+
# mjoy9IFHUUW/QHppMbbp8kH5HKUJOCW3vvwA3JisdjLTuUyJdbrRo5oQ+OkKXjsn
# bCMPePYDTofPlwg8UAA6LA2OX5WrCR8hXw0RUOy4Vea5ViLUzSgQfZ6CH0cQgmv5
# qEVGJxacdZZqvpBOZmSduhLxrHwY1k0kwmKA/JK66bLrxugR45XtdXWYJv7I2Wb8
# lyhCAPGWncO/fyDbh2leirXuAHOqNuwVdOcPcNAkDQJl6VxWyGdJcCgXcjIrIai1
# o3LFhv1e8jgEFVoNvM8E
# =8Po5
# -----END PGP SIGNATURE-----'''
    # print '############################## ENC ##############################'
    # # enc = pc.send_plaintext(a, 'santiago9101@me.com')
    # print '############################## DEC ##############################'
    # # dec = pc.send_ciphertext(to_dec)
    # print '############################## SGN ##############################'
    # # sgn = pc.send_sign(email)
    # print '############################## VFY ##############################'
    # # vrf = pc.send_verify(sign)
    # print '##################################################################'
