import os
import gnupg
import socket
import struct
import re
from socket_utils import *

class PGP:
    def __init__(self, path, email=None, verbose=False, pass_phrase=None):
        self.DEF_SERVER = 'pgp.mit.edu'
        self.pgp = gnupg.GPG(gnupghome=path)
        self.verbose = verbose
        self.email = email
        #self.kid is only used after calling load_key
        # (self.kid, self.fingerprint) = load_key(self.email)
        self.fingerprint = self.load_key(self.email)
        if self.fingerprint is None:
            print 'No key pair found this email. Generating new key_pair...'
            self.gen_key_pair(pass_phrase, self.email)
        os.chmod(path, 0x1C0)

    '''
    returns the last match in the list_keys() dict
    '''
    def load_key(self, email, private=True):
        kdict = self.pgp.list_keys(private)
        kid = None
        fp = None
        for k in kdict:
            if email in str(k['uids'][0]):
                # kid = str(k['keyid'][0])
                fp = str(k['fingerprint'])
        # return (kid, fp)
        return fp

    def gen_key_pair(self, pass_phrase, email=None):
        if email != None:
            self.email = email
        input_data = self.pgp.gen_key_input(name_email=self.email, passphrase=pass_phrase)
        key = self.pgp.gen_key(input_data)
        self.fingerprint = key.fingerprint
        return key

    def export_kp_to_file(self, key_fingerprint, file_name):
        ascii_armored_public_keys = self.pgp.export_keys(key_fingerprint)
        ascii_armored_private_keys = self.pgp.export_keys(key_fingerprint, True)
        with open('%s.asc' % file_name, 'w') as f:
            f.write(ascii_armored_public_keys)
            f.write(ascii_armored_private_keys)

    def import_kp_from_file(self, file_name):
        key_data = open(file_name).read()
        import_result = self.pgp.import_keys(key_data)
        print 'Found %d keys with ids:\n' % import_result.count
        for id in import_result.fingerprints:
            print id
        return import_result

    '''
        recipients: list of fingerprints or one fingerprint
    '''
    def encrypt_sign_str(self, plain_text, recipients,
                    sign_key_id=None, sign_passphase=None,
                    alwaystrust=False):
        enc = self.pgp.encrypt(plain_text, recipients,
                                    sign=sign_key_id,
                                    passphrase=sign_passphase,
                                    always_trust=alwaystrust)
        if enc.ok is True:
            return str(enc)
        else:
            return enc.stderr
    '''
        file: should be open in rb mode i.e., file = open('filename.txt','rb')
    '''
    def encrypt_sign_file(self, file, output_file_name,
                     recipients, sign_key_id=None,
                     sign_passphase=None, alwaystrust=False):
        enc =  self.pgp.encrypt_file(file, recipients,
                                         sign=sign_key_id,
                                         passphrase=sign_passphase,
                                         output=output_file_name,
                                         always_trust=alwaystrust)
        if enc.ok is True:
            return str(enc)
        else:
            return enc.stderr

    def decrypt_str(self, encrypted_string, pass_phrase):
        dec = self.pgp.decrypt(encrypted_string,
                                    passphrase=pass_phrase)
        if dec.ok is True:
            return dec.data
        else:
            return dec.stderr

    def decrypt_file(self, file, output_file_name,
                     pass_phrase):
        dec =  self.pgp.decrypt_file(file, passphrase=pass_phrase,
                                         output=output_file_name)
        if dec.ok is True:
            return dec.data
        else:
            return dec.stderr

    def local_search(self, email):
        kdict = self.pgp.list_keys(False)
        kid = None
        fp = None
        for k in kdict:
            if email in str(k['uids'][0]):
                fp = str(k['fingerprint'])
                print 'Pub key found locally !'
        return fp

    def search_key(self, email, key_server=None):
        kid = self.local_search(email)
        if kid is None:
            if key_server is None:
                # key_server = 'hkps.pool.sks-keyservers.net'
                key_server = self.get_default_server()
            key =  self.pgp.search_keys(email, key_server)
            if len(key) > 0:
                for k in key:
                    # print k['uids'][0]
                    import_result = []
                    if email in str(k['uids'][0]):
                        print 'Imporing pub for %s' % str(k['uids'][0])
                        kid = k['keyid']
                        self.pgp.recv_keys(self.DEF_SERVER, kid)
        return kid

    def get_default_server(self):
        return self.DEF_SERVER

    def send_key(self, kid, server=None):
        if server is None:
            server = get_default_server()
        return gpg.send_keys(server, kid)

    def email2fp(self, email):
        kdict = self.pgp.list_keys()
        for k in kdict:
            if email in str(k['uids'][0]):
                return str(k['fingerprint'])

    def delete_key_fp(self, fp):
        dsk = self.pgp.delete_keys(fp, True)
        dpk = self.pgp.delete_keys(fp)
        return '%s %s' % (str(dsk), str(dpk))

    def delete_key(self, email):
        fp = self.email2fp(email)
        return self.delete_key_fp(fp)

    def get_priv_keys(self):
        kdict = self.pgp.list_keys(True)
        priv_key_fps= []
        for k in kdict:
            priv_key_fps.append(k['fingerprint'])
        return priv_key_fps

    def get_pub_keys(self):
        kdict = self.pgp.list_keys()
        pub_key_fps= []
        for k in kdict:
            pub_key_fps.append(k['fingerprint'])
        return pub_key_fps

    def reset_database(self):
        print 'DELETING all pub/priv keys'
        priv_key_fps = self.get_priv_keys()
        for k in priv_key_fps:
            self.delete_key_fp(k)

    def run_server(self, server_ip, server_port, max_connections=5):

        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind((server_ip, server_port))
        serversocket.listen(max_connections) # become a server socket, maximum 5 connections

        while True:
            connection, address = serversocket.accept()
            buf = recv_one_message(connection)
            if buf['mode'] == 0:
                if len(buf['data']) > 0:
                    print buf['data']
                    recipient_email = re.findall(r'(?<=mailto:)[^@]+@[^@]+\.[^@]+(?="\s)', buf['data'])[0]
                    print 'Searchin for pub of %s ...' % recipient_email
                    recipient_fp = self.search_key(recipient_email)
                    print 'Encrypting using pub of %s ...' % recipient_email
                    enc = self.encrypt_sign_str(buf['data'], recipient_fp, alwaystrust=True)
                    print enc
                    send_one_resp(connection, str(enc))

            elif buf['mode'] == 1:
                if len(buf['data']) > 0:
                    print buf['data']
                    print 'Decrypting using priv of %s ...' % self.email
                    enc = self.decrypt_str(buf['data'], 'secreto')
                    print enc
                    send_one_resp(connection, str(enc))
        # serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # serversocket.bind((, ))
        # serversocket.listen(1) # become a server socket, maximum 5 connections

        # while True:
        #     connection, address = serversocket.accept()
        #     buf = connection.recv(64)
        #     if len(buf) > 0:
        #         encrypt_sign_file
    # def send_emai(self,)
    # def send_one_message(self, sock, data):
    #     length = len(data)
    #     sock.sendall(struct.pack('!I', length))
    #     sock.sendall(data)
    # def recv_one_message(self, sock):
    #     lengthbuf = self.recvall(sock, 4)
    #     length, = struct.unpack('!I', lengthbuf)
    #     return self.recvall(sock, length)

    # def recvall(self, sock, count):
    #     buf = b''
    #     while count:
    #         newbuf = sock.recv(count)
    #         if not newbuf: return None
    #         buf += newbuf
    #         count -= len(newbuf)
    #     return buf


    # def delete_current_key(self):

if  __name__ == '__main__':
    server_ip = '193.168.8.2'
    server_ip = 'localhost'
    server_port = 8089

    import pgp_wrapper as g
    p = g.PGP('keys',
          'santiago9101@me.com',
          verbose=True,
          pass_phrase='secreto')

    p.run_server(server_ip, server_port)
