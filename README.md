# pgp_dongle
This project aim to build the basics of a plug and play service to encrypt/decrypt/sign/manage personal and 3rd party keys/ running on a external device.

# Requirements

+ Unix computer
+ BeagleBoard Black (BBB) or  Any linux-based computer with USB-host capabilities
+ GnuPGP. The open source library for pgp
+ Git
+ Python 2.7
+ PIP for Python

# Installation
In the BBB:

    + git clone https://github.com/santiag0aragon/pgp_dongle
    + cd pgp_dongle
    + pip install -r requirements.txt


# Usage
'''
sudo python pgp_wrapper.py --server-ip localhost --server-port 8089 --email your_email@your_domain.com --passphrase secreto
'''

In config file:

    [email-credentials]
    username: your_email@your_domain.com
    password: ******
    imap_server: imap.your_domain.com
    imap_port: 993
    smtp_local_add: 127.0.0.1
    smtp_local_port: 587
    smtp_remote: smtp.your_domain.com:587
'''


