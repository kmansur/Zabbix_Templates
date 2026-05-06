#!/bin/sh
# Script: dovecot_num_pop.sh
# Version: 2.0.0
# Purpose: Legacy-compatible POP3 session counter for Zabbix.
# Author: Karim Mansur / Net Tech

DOVEADM="${DOVECOT_DOVEADM:-/usr/local/bin/doveadm}"

"$DOVEADM" who -1 2>/dev/null | /usr/bin/awk '
BEGIN { pop3 = 0 }
function clean_token(value) {
    gsub(/^[^a-z0-9_]+/, "", value)
    gsub(/[^a-z0-9_]+$/, "", value)
    return value
}
{
    for (i = 2; i <= NF; i++) {
        token = clean_token(tolower($i))
        if (token == "pop3" || token == "pop") {
            pop3++
            next
        }
    }
}
END { print pop3 }'
