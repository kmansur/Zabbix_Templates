#!/bin/sh
# Script: dovecot_num_imap.sh
# Version: 2.0.0
# Purpose: Legacy-compatible IMAP session counter for Zabbix.
# Author: Karim Mansur / Net Tech

DOVEADM="${DOVECOT_DOVEADM:-/usr/local/bin/doveadm}"

"$DOVEADM" who -1 2>/dev/null | /usr/bin/awk '
BEGIN { imap = 0 }
function clean_token(value) {
    gsub(/^[^a-z0-9_]+/, "", value)
    gsub(/[^a-z0-9_]+$/, "", value)
    return value
}
{
    for (i = 2; i <= NF; i++) {
        token = clean_token(tolower($i))
        if (token == "imap") {
            imap++
            next
        }
    }
}
END { print imap }'
