#!/bin/sh
/usr/local/bin/doveadm who | /usr/bin/awk '/imap/ {imap++} /pop/{pop++} /imap|pop/ {total++} END {print "imap,pop,total\n"imap","pop","total}'
