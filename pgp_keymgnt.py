import os
import gnupg
from pprint import pprint

path = './testgpguser/gpghome'
# KEY GEN
print '###########################################'
os.system('rm -rf %s'% s)
gpg = gnupg.GPG(gnupghome=path)
input_data = gpg.gen_key_input(
    name_email='testgpguser@mydomain.com',
    passphrase='my passphrase')
key = gpg.gen_key(input_data)
print key

# # KEY EXPORT
# print '###########################################'
# gpg = gnupg.GPG(gnupghome=path)
# ascii_armored_public_keys = gpg.export_keys(key)
# ascii_armored_private_keys = gpg.export_keys(key, True)
# with open('mykeyfile.asc', 'w') as f:
#     f.write(ascii_armored_public_keys)
#     f.write(ascii_armored_private_keys)
# # KEY IMPORT
# print '###########################################'
# gpg = gnupg.GPG(gnupghome=path)
# key_data = open('mykeyfile.asc').read()
# import_result = gpg.import_keys(key_data)
# pprint(import_result.results)
# STRING ENC
print '###########################################'
gpg = gnupg.GPG(gnupghome=path)
unencrypted_string = 'Who are you? How did you get in my house?'
encrypted_data = gpg.encrypt(unencrypted_string, 'testgpguser@mydomain.com')
encrypted_string = str(encrypted_data)
print 'ok: ', encrypted_data.ok
print 'status: ', encrypted_data.status
print 'stderr: ', encrypted_data.stderr
print 'unencrypted_string: ', unencrypted_string
print 'encrypted_string: ', encrypted_string
# STRING DEC
print '###########################################'
gpg = gnupg.GPG(gnupghome=path)
unencrypted_string = 'Who are you? How did you get in my house?'
encrypted_data = gpg.encrypt(unencrypted_string, 'testgpguser@mydomain.com')
encrypted_string = str(encrypted_data)
decrypted_data = gpg.decrypt(encrypted_string, passphrase='my passphrase')

print 'ok: ', decrypted_data.ok
print 'status: ', decrypted_data.status
print 'stderr: ', decrypted_data.stderr
print 'decrypted string: ', decrypted_data.data
# FILE ENC
print '###########################################'
gpg = gnupg.GPG(gnupghome=path)
open('my-unencrypted.txt', 'w').write('You need to Google Venn diagram.')
with open('my-unencrypted.txt', 'rb') as f:
    status = gpg.encrypt_file(
        f, recipients=['testgpguser@mydomain.com'],
        output='my-encrypted.txt.gpg')

print 'ok: ', status.ok
print 'status: ', status.status
print 'stderr: ', status.stderr
# FILE DEC
print '###########################################'
gpg = gnupg.GPG(gnupghome=path)
with open('my-encrypted.txt.gpg', 'rb') as f:
    status = gpg.decrypt_file(f, passphrase='my passphrase', output='my-decrypted.txt')

print 'ok: ', status.ok
print 'status: ', status.status
print 'stderr: ', status.stderr
