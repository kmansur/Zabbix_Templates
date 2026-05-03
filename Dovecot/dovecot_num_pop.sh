#!/bin/sh
/usr/local/bin/doveadm who | /usr/bin/grep pop | /usr/bin/wc -l | /usr/bin/awk '{print $1}'
