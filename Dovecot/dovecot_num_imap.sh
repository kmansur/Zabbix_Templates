#!/bin/sh

DOVEADM="${DOVECOT_DOVEADM:-/usr/local/bin/doveadm}"

"$DOVEADM" who 2>/dev/null | /usr/bin/awk '
BEGIN { imap = 0 }
{
    line = tolower($0)
    if (line ~ /(^|[^a-z0-9_])imap([^a-z0-9_]|$)/) {
        imap++
    }
}
END { print imap }'
