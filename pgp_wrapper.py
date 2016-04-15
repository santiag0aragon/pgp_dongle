import os
import gnupg
import socket
import struct
import re
import sys
import getpass

from socket_utils import *

# For the generation of the key you may want to run
# sudo rngd -r /dev/urandom
# to generate randomnes
class PGP:
    def __init__(self, path, email=None, verbose=False, pass_phrase=None):
        self.DEF_SERVER = 'pgp.mit.edu'
        self.pgp = gnupg.GPG(gnupghome=path)
        self.pgp.verbose = verbose
        self.email = email
        #self.kid is only used after calling load_key
        # (self.kid, self.fingerprint) = load_key(self.email)
        self.fingerprint = self.load_key(self.email)
        if self.fingerprint is None:
            if  pass_phrase is not None:
                print 'No key pair found this email. Generating new key_pair...'
                self.gen_key_pair(pass_phrase, self.email)
                self.key_not_uploaded = True
            elif pass_phrase is None:
                print 'To generate the key a passphrase is needed'
                sys.exit(1)

        else:
            self.key_not_uploaded = False
            # self.send_key(self.fingerprint)
        # os.chmod(path, 0x1C0)

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
        if sign_passphase is None or sign_key_id is None:
            enc = self.pgp.encrypt(plain_text, recipients,
                                    always_trust=alwaystrust)
        else:
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
        print dec.trust_text
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

    def sign_str(self, message, pass_phrase):
        return self.pgp.sign(message, keyid=self.fingerprint, passphrase=pass_phrase)

    def vrf_str(self, sign):
        return self.pgp.verify(sign).valid

    def local_search(self, email):
        kdict = self.pgp.list_keys(False)
        kid = None
        fp = None
        for k in kdict:
            if email in str(k['uids'][0]):
                fp = str(k['fingerprint'])
                print 'Pub key found locally !'
        return fp

    # def search_key(self, email, connection, key_server=None):
    #     kid = self.local_search(email)
    #     if kid is None:
    #         if key_server is None:
    #             # key_server = 'hkps.pool.sks-keyservers.net'
    #             key_server = self.get_default_server()
    #         key =  self.pgp.search_keys(email, key_server)
    #         if len(key) > 0:
    #             for k in key:
    #                 # print k['uids'][0]
    #                 if email in str(k['uids'][0]):
    #                     print 'Imporing pub for %s' % str(k['uids'][0])
    #                     kid = k['keyid']
    #                     self.pgp.recv_keys(self.DEF_SERVER, kid)
    #     return kid

    def get_default_server(self):
        return self.DEF_SERVER

    # def send_key(self, kid, server=None):
    #     if server is None:
    #         server = self.get_default_server()
    #     return self.pgp.send_keys(server, kid)

    def email2fp(self, email):
        kdict = self.pgp.list_keys()
        for k in kdict:
            if email in str(k['uids'][0]):
                print k['uids'][0]
                return str(k['fingerprint'])

    def delete_key_fp(self, fp):
        dsk = self.pgp.delete_keys(fp, True)
        dpk = self.pgp.delete_keys(fp)
        return 'Deleted %s %s' % (str(dsk), str(dpk))

    def delete_key(self, email):
        fp = self.email2fp(email)
        return self.delete_key_fp(fp)

    def delete_key_pub(self, email):
        fp = self.email2fp(email)
        if fp is None:
            print 'No key to delete for %s' % email
        else:
            dpk = self.pgp.delete_keys(fp)
        return 'Deleted %s' % dpk

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
        connection, address = serversocket.accept()
        while True:
            print 'Waiting for incomming requests...'
            buf = recv_one_message(connection)
            mode = buf['mode']
            data = buf['data']
            if len(data) > 0:
                if mode == 0:
                    print 'Processing encryption request...'
                    # print data
                    buf = recv_one_message(connection)
                    recipient_email = buf['data']
                    # recipient_email = re.findall(r'(?<=To:)*[^@]+@[^@]+\.[^@]+(?=>)', data)[0]
                    print 'Searchin for pub of %s ...' % recipient_email
                    recipient_fp = self.local_search(recipient_email)
                    buf = recv_one_message(connection)
                    key_data = buf['data']
                    if recipient_fp is None:
                        print 'Key downloaded. Importing locally.'
                        self.pgp.import_keys(key_data)
                        recipient_fp = self.local_search(recipient_email)

                    if recipient_fp is not None:
                        print 'Encrypting using pub of %s ...' % recipient_email
                        # Signature is not currently supported
                        # phrase = getpass.getpass('Passphrase:')
                        # enc = self.encrypt_sign_str(data, recipient_fp, sign_key_id=self.fingerprint, sign_passphase=phrase, alwaystrust=True)
                        enc = self.encrypt_sign_str(data, recipient_fp, alwaystrust=True)
                        print enc
                        send_one_resp(connection, str(enc))
                    else:
                        print 'Pub not found for %s' % recipient_email
                        send_one_resp(connection, 'Key not found')

                elif mode == 1:
                    print data
                    print 'Decrypting using priv of %s ...' % self.email
                    phrase = getpass.getpass('Passphrase:')
                    enc = self.decrypt_str(data, phrase)
                    print enc
                    send_one_resp(connection, str(enc))

                elif mode == 3:
                    print data
                    # VERIFY SIGN
                    # print 'Verifing message signature using key with fingerprint %s ...' % data.fingerprint
                    vrf = self.vrf_str(data)
                    send_one_resp(connection, str(vrf))

                elif mode == 4:
                    print data
                    #  SIGN
                    print 'Signing message using priv of %s ...' % self.email
                    phrase = getpass.getpass('Passphrase:')
                    sgn = self.sign_str(data, phrase)
                    send_one_resp(connection, str(sgn))

                elif mode == 6:
                    if self.key_not_uploaded:
                        key_data = self.pgp.export_keys(self.fingerprint)
                        send_one_upload_key(connection, key_data)
                        print 'Sending pub to client to be uploaded'
                    else:
                        send_one_upload_key(connection, 'Uploaded')


if  __name__ == '__main__':
    import sys
    import pgp_wrapper as g
    import argparse

    parser = argparse.ArgumentParser(description='DonPGP!')

    parser.add_argument('--server-ip', help='IP to run DonPGP', required=True)
    parser.add_argument('--server-port', help='port to run DonPGP', required=True)
    parser.add_argument('--email', help='Email to generate key pair', required=True)
    parser.add_argument('--passphrase', help='Secret to unlock private key. Only needed to generate a new key_pair.', default=None, required=False)
    parser.add_argument('--verbose', help='Secret to unlock private key. Only needed to generate a new key_pair.', action='store_true')


    args = parser.parse_args()
    print args
    p = g.PGP('keys',
          args.email,
          verbose=args.verbose,
          pass_phrase=args.passphrase)
    p.run_server(args.server_ip, int(args.server_port))
