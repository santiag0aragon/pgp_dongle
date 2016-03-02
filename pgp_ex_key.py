import gnupg

gpg = gnupg.GPG(gnupghome='/home/testgpguser/gpghome')
ascii_armored_public_keys = gpg.export_keys(key)
ascii_armored_private_keys = gpg.export_keys(key, True)
with open('mykeyfile.asc', 'w') as f:
    f.write(ascii_armored_public_keys)
    f.write(ascii_armored_private_keys)
