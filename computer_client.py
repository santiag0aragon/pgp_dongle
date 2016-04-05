#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import paramiko
import socket
from socket_utils import *

class PCClient():

    def __init__(self, localhost=False):
        self.username = 'root'
        if not localhost:
            self.server = '193.168.8.2'
        else:
            self.server = 'localhost'
        self.port = 8089
        self.password = ''
        self.remotepath = '/root/home/email/to_encrypt/'

    def send_file(self, file):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        f_path = file
        ssh.connect(self.server, username=self.username, password=self.password)
        sftp = ssh.open_sftp()
        sftp.put(f_path, '%s%s' % (self.remotepath, f_path))
        sftp.close()
        ssh.close()

    def send_data(self, data):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        f_path = 'my-unencrypted.txt'
        open(f_path, 'w').write(data)
        ssh.connect(self.server, username=self.username, password=self.password)
        sftp = ssh.open_sftp()
        sftp.put(f_path, '%s%s' % (self.remotepath, f_path))
        sftp.close()
        ssh.close()
        os.remove(f_path)

    def send(self, data, mode, email= None):
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.connect((self.server, self.port))
        if mode is 'ENC':
            send_one_enc(clientsocket, data)
            send_one_enc(clientsocket, email)

        elif mode is 'DEC':
            send_one_dec(clientsocket, data)

        elif mode is 'VFY':
            send_one_vrf(clientsocket, data)

        elif mode is 'SGN':
            send_one_sgn(clientsocket, data)

        while True:
            buf = recv_one_message(clientsocket)
            if buf['mode'] == 2 and len(buf['data']) > 0:
                if len(buf['data']) > 0:
                    print "Received response:\n" + str(buf['data'])
                    return str(buf['data'])

    def send_ciphertext(self, data):
        return self.send(data, 'DEC')

    def send_plaintext(self, data, email):
        return self.send(data, 'ENC', email=email)

    def send_verify(self, data):
        return self.send(data, 'VFY')

    def send_sign(self, data):
        return self.send(data, 'SGN')

if  __name__ == '__main__':
    pc = PCClient(True)

    email = '''
    <html><head><meta http-equiv=3D"Content-Type" content=3D"text/html =
    charset=3Dutf-8"></head><body style=3D"word-wrap: break-word; =
    -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;" =
    class=3D"">They told me that they are almost done (10 min) and I need 20 =
    to the university.<div class=3D"">Is there any other option, i.e., go to =
    Delf next week</div><div class=3D""><br class=3D""></div><div =
    class=3D"">Best&nbsp;<br class=3D""><div><blockquote type=3D"cite" =
    class=3D""><div class=3D"">El 18/03/2016, a las 3:55 p.m., Christian =
    Doerr &lt;<a href=3D"mailto:santiago9101@me.com" =
    class=3D"">santiago9101@gmail.com</a>&gt; escribi=C3=B3:</div><br =
    class=3D"Apple-interchange-newline"><div class=3D""><span =
    style=3D"font-family: Helvetica; font-size: 12px; font-style: normal; =
    font-variant: normal; font-weight: normal; letter-spacing: normal; =
    orphans: auto; text-align: start; text-indent: 0px; text-transform: =
    none; white-space: normal; widows: auto; word-spacing: 0px; =
    -webkit-text-stroke-width: 0px; float: none; display: inline =
    !important;" class=3D"">n their room, be nice to them and ask them to =
    adopt you.</span><br style=3D"font-family: Helvetica; font-size: 12px; =
    font-style: normal; font-variant: normal; font-weight: normal; =
    letter-spacing: normal; orphans: auto; text-align: start; text-indent: =
    0px; text-transform: none; white-space: normal; widows: auto; =
    word-spacing: 0px; -webkit-text-stroke-width: 0px;" =
    class=3D""></div></blockquote></div><br class=3D""></div></body></html>=
    '''
    sign = '''Content-Transfer-Encoding: 7bit
Content-Type: text/plain;
    charset=us-ascii

asdasdasdasdadsadasdasd
-----BEGIN PGP SIGNATURE-----
Comment: GPGTools - https://gpgtools.org

iQIcBAEBCgAGBQJXA7f8AAoJELleHttpVgRP9xkP/1tb4wFKfBraYmByzONdjTfO
tog2eksLg0BPfehyoBx0apJT2WPXRGlqcMINIY3CMa6tXCQAfb+XqtOIkk2kuvPw
JJeiFSAYgv7VQJ64B04wj9aL4Vl7RoMYWE83SYftnLrpN8jQAf68BhI+sjfojIk1
kCmm0YT0Z75etJXhsssfTQJv3sbLwWRoZdVyvB0pe1McElW9sThijtAGyLR9rFBT
o5yi8nEjx9ifwsmTenb6GJ3v3KZFxeM5r8vOGCYkd2p7aBBoTnUYindb/TKaNrsf
HvJy2Dx8v3+bmDcAortp+MeL7rjPzdsfpNq5oWMn3RpFjuORt5Af62rRbmMKlfVp
/HYVz3df+coa53sxc2fuJsWIB4VGZYq7qTTqFqIpZT0VYoU1OQwbSU9V+O5L67/+
mjoy9IFHUUW/QHppMbbp8kH5HKUJOCW3vvwA3JisdjLTuUyJdbrRo5oQ+OkKXjsn
bCMPePYDTofPlwg8UAA6LA2OX5WrCR8hXw0RUOy4Vea5ViLUzSgQfZ6CH0cQgmv5
qEVGJxacdZZqvpBOZmSduhLxrHwY1k0kwmKA/JK66bLrxugR45XtdXWYJv7I2Wb8
lyhCAPGWncO/fyDbh2leirXuAHOqNuwVdOcPcNAkDQJl6VxWyGdJcCgXcjIrIai1
o3LFhv1e8jgEFVoNvM8E
=8Po5
-----END PGP SIGNATURE-----'''
    print '############################## ENC ##############################'
    # enc = pc.send_plaintext(a, 'santiago9101@me.com')
    print '############################## DEC ##############################'
    # dec = pc.send_ciphertext(to_dec)
    print '############################## SGN ##############################'
    # sgn = pc.send_sign(email)
    print '############################## VFY ##############################'
    # vrf = pc.send_verify(sign)
    print '##################################################################'
