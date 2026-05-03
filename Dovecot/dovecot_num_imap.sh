#!/bin/sh
/usr/local/bin/doveadm who | /usr/bin/grep imap | /usr/bin/wc -l | /usr/bin/awk '{print $1}'
