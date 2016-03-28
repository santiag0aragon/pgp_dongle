import os
import gnupg


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
    def load_key(self, email):
        kdict = self.pgp.list_keys(True)
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

    def search_key(self, key_fp, key_server=None):
        if key_server is None:
            # key_server = 'hkps.pool.sks-keyservers.net'
            key_server = self.get_default_server()
        return self.pgp.search_keys(key_fp, key_server)

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


    # def send_emai(self,)

    # def delete_current_key(self):

# if  __name__ == '__main__':
    # import pgp_wrapper as g
    # p = g.PGP('keys', 'a@b.com', verbose=True, pass_phrase='secreto')

    # #key = p.gen_key_pair('a@b.com','secreto')
    # enc = p.encrypt_str('secret','a@b.com','a@b.com','secreto')
    # dec = p.decrypt_str(str(enc),'secreto')
    # p.search_key('santiago9101@gmail.com')

    # enc = p.encrypt_str('secret','santiago9101@gmail.com','a@b.com','secreto')

    #  a = p.pgp.recv_keys('pgp.mit.edu','84748DAF70BAF47AA8690B46B95E1EDB6956044F')

    # path = './testgpguser/gpghome'
    # gpg_instance = gnupg.GPG(gnupghome=path)

    # import_kp_from_file(gpg_instance, 'mykeyfile.asc')
    # unencrypted_string = 'un secreto'
    # encrypted_data = gpg_instance.encrypt(unencrypted_string, 'testgpguser@mydomain.com')
    # encrypted_string = str(encrypted_data)

    # print 'ok: ', encrypted_data.ok
    # print 'status: ', encrypted_data.status
    # print 'stderr: ', encrypted_data.stderr
    # print 'unencrypted_string: ', unencrypted_string
    # print 'encrypted_string: ', encrypted_string
    # decrypted_data = gpg_instance.decrypt(encrypted_string)
    # print 'ok: ', decrypted_data.ok
    # print 'status: ', decrypted_data.status
    # print 'stderr: ', decrypted_data.stderr
    # print 'decrypted string: ', decrypted_data.data
