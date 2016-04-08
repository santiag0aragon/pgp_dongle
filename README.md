# pgp_dongle
This project aim to build the basics of a plug and play service to encrypt/decrypt/sign/manage personal and 3rd party keys/ running on a external device.

based on python-gnupg and pyzmail

Usage

sudo python pgp_wrapper.py --server-ip localhost --server-port 8089 --email oikos.labs@gmail.com --passphrase secreto

config file
[email-credentials]
username: oikos.labs@gmail.com
password: ******
imap_server: imap.gmail.com
imap_port: 993
smtp_local_add: 127.0.0.1
smtp_local_port: 587
smtp_remote: smtp.gmail.com:587



Referenes
http://www.saltycrane.com/blog/2011/10/python-gnupg-gpg-example/
