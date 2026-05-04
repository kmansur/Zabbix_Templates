#!/bin/sh

DOVEADM="${DOVECOT_DOVEADM:-/usr/local/bin/doveadm}"

print_error() {
    printf '{"status":0,"imap":0,"pop3":0,"total":0,"error":"%s"}\n' "$1"
}

if [ ! -x "$DOVEADM" ]; then
    print_error "doveadm_not_executable"
    exit 0
fi

WHO_OUTPUT="$("$DOVEADM" who 2>/dev/null)"
WHO_STATUS=$?

if [ "$WHO_STATUS" -ne 0 ]; then
    print_error "doveadm_who_failed"
    exit 0
fi

printf '%s\n' "$WHO_OUTPUT" | /usr/bin/awk '
BEGIN {
    imap = 0
    pop3 = 0
}
{
    line = tolower($0)
    if (line ~ /(^|[^a-z0-9_])imap([^a-z0-9_]|$)/) {
        imap++
    }
    if (line ~ /(^|[^a-z0-9_])pop3?([^a-z0-9_]|$)/) {
        pop3++
    }
}
END {
    total = imap + pop3
    printf "{\"status\":1,\"imap\":%d,\"pop3\":%d,\"total\":%d,\"error\":\"\"}\n", imap, pop3, total
}'
