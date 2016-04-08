import smtpd
import asyncore
import sys
import smtplib
import pyzmail as par
from computer_client import PCClient
import email.mime.application
import email.mime.multipart
import email.mime.text
import email.encoders
import getpass, imaplib, sys, email
# import secure_smtpd as ss
# import logging
# from secure_smtpd import LOG_NAME


class CustomSMTPServer(smtpd.SMTPServer):

    def __init__(self, username, password, imap_server, imap_port, *args, **kwargs):
        smtpd.SMTPServer.__init__(self, *args, **kwargs)
        # super(CustomSMTPServer, self).__init__(*args, **kwargs)
        self.username = username
        self.password = password
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.pc_client = PCClient(server=self._localaddr[0])
        self.sync()
    # def __init__(self, *args, **kwds ):
        # self.pc_client = PCClient('127.0.0.1')
        # super(CustomSMTPServer, self).__init__(*args, **kwds)

    # def get_body(self, data):
    #     parts = par.parse.get_mail_parts(data)
    #     # msg = dict()

    #     # for d in data.split('\n'):
    #     #     fields = d.split(':')
    #     #     if len(fields) > 1:
    #     #         msg[fields[0]] = fields[1]
    #     #     else:
    #     #         msg['body'] = fields[0]
    #     return msg

    def sync(self):
        self.pc_client.recv_key_to_upload()

    def pgp_mime(self, encrypted_content):

        enc = email.mime.application.MIMEApplication(
                _data=str(encrypted_content),
                _subtype='octet-stream; name="encrypted.asc"',
                _encoder=email.encoders.encode_7or8bit)
        enc['Content-Description'] = 'OpenPGP encrypted message'
        enc.set_charset('us-ascii')

        control = email.mime.application.MIMEApplication(
                _data='Version: 1\n',
                _subtype='pgp-encrypted',
                _encoder=email.encoders.encode_7or8bit)
        control.set_charset('us-ascii')

        encmsg = email.mime.multipart.MIMEMultipart(
                'encrypted',
                protocol='application/pgp-encrypted')
        encmsg.attach(control)
        encmsg.attach(enc)
        encmsg['Content-Disposition'] = 'inline'

        return encmsg

    def process_message(self, peer, mailfrom, rcpttos, data):

        # print 'Receiving message from:', peer
        # print 'Message addressed from:', mailfrom
        # print 'Message addressed to  :', rcpttos
        # print 'Message length        :', len(data)
        # print 'Message\n##\n', data
        # print sys.stderr.write()


        # Forwarding to
        print 'Forwarding to servername %s ' % (self._remoteaddr)
        server = smtplib.SMTP(self._remoteaddr)
        try:
            author = mailfrom
            to_email = rcpttos
            enc = self.pc_client.send_plaintext(data, to_email[0])
            if enc != 'Key not found':
                enc_msg =  self.pgp_mime(enc)
                server.set_debuglevel(True)
                print enc_msg
                # identify ourselves, prompting server for supported features
                server.ehlo()
                # If we can encrypt this session, do it
                # server.login(username, password)
                # print dir(server)
                if server.has_extn('STARTTLS'):
                    server.starttls()
                    server.ehlo() # re-identify ourselves over TLS connection

                server.login(self.username, self.password)
                server.sendmail(author, [to_email], enc_msg.as_string())
            else:
                print 'Pub of %s not found in servers.' % to_email[0]
        except:
            server.quit()
            print 'Quiting server. Error'

    def imap_reciever(self):
        conn = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
        # user = 'oikos.labs@gmail.com'
        # pas = 'vhysnegoxaygaifq

        def get_body(data):
            parts = par.parse.get_mail_parts(data)
            # print parts
            # print parts[1].get_payload().decode(parts[1].charset)
            body = ''
            for part in parts:
                if part.filename:
                    ext = part.filename.split('.')[1]

                if part.type.strip() == 'application/octet-stream' and ext == 'asc':
                    body = part.get_payload().decode(part.charset)
            return body

        try:
            (retcode, capabilities) = conn.login(self.username, self.password)
        except:
            print sys.exc_info()[1]
            sys.exit(1)

        conn.select(readonly=0) # Select inbox or default namespace
        (retcode, messages) = conn.search(None, '(UNSEEN)')
        if retcode == 'OK' and messages[0].split(' ') != ['']:
            for num in messages[0].split(' '):
                new_email = raw_input("New encrypted email. Do you want to decrypt? [Yes/no]")
                if new_email == 'Yes':
                    print 'Processing :', num
                    typ, data = conn.fetch(num, '(RFC822)')
                    msg = email.message_from_string(data[0][1])
                    typ, data = conn.store(num, 'FLAGS', '(\Seen)')
                    print typ, data
                    if retcode == 'OK':
                        print '\n',30*'/'
                        to_dec = get_body(msg)
                        print to_dec
                        dec = self.pc_client.send_ciphertext(to_dec)
                        print dec
                elif new_email == 'No':
                    print 'Skipping email'
        conn.close()
        conn.logout()

if  __name__ == '__main__':
    username = 'oikos.labs@gmail.com'
    password = 'vhysnegoxaygaifq'
    server = CustomSMTPServer(username=username,
                              password=password,
                              imap_server='imap.gmail.com',
                              imap_port=993,
                              localaddr=('127.0.0.1', 587),
                              remoteaddr='smtp.gmail.com:587')
    print 'Server running'



    while True:
        asyncore.loop(timeout=1, count=5)
        server.imap_reciever()


# server = smtpd.DebuggingServer(('127.0.0.1', 1025), 'smtp.gmail.com:587')
# server = CustomProxyServer(('127.0.0.1', 587), 'smtp.gmail.com:587')
# server = ss.proxy_server.ProxyServer(('127.0.0.1', 587),('smtp.gmail.com',587) ,credential_validator=None, debug = True)

# logger = logging.getLogger( LOG_NAME )
# logger.setLevel(logging.INFO)
# print server.run()
