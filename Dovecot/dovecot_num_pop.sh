#!/bin/sh

DOVEADM="${DOVECOT_DOVEADM:-/usr/local/bin/doveadm}"

"$DOVEADM" who 2>/dev/null | /usr/bin/awk '
BEGIN { pop3 = 0 }
{
    line = tolower($0)
    if (line ~ /(^|[^a-z0-9_])pop3?([^a-z0-9_]|$)/) {
        pop3++
    }
}
END { print pop3 }'
