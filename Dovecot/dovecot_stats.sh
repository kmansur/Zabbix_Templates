#!/bin/sh
# Script: dovecot_stats.sh
# Version: 2.0.0
# Purpose: Collect Dovecot session counters for Zabbix as JSON.
# Author: Karim Mansur / Net Tech
# Notes:
# - Uses "doveadm who -1" so each connection is returned on a separate line.
# - Returns valid JSON even when collection fails.

DOVEADM="${DOVECOT_DOVEADM:-/usr/local/bin/doveadm}"

print_error() {
    printf '{"status":0,"imap":0,"pop3":0,"total":0,"error":"%s"}\n' "$1"
}

if [ ! -x "$DOVEADM" ]; then
    print_error "doveadm_not_executable"
    exit 0
fi

WHO_OUTPUT="$("$DOVEADM" who -1 2>/dev/null)"
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
function clean_token(value) {
    gsub(/^[^a-z0-9_]+/, "", value)
    gsub(/[^a-z0-9_]+$/, "", value)
    return value
}
{
    # Skip the first field because it is normally the username.
    for (i = 2; i <= NF; i++) {
        token = clean_token(tolower($i))
        if (token == "imap") {
            imap++
            next
        }
        if (token == "pop3" || token == "pop") {
            pop3++
            next
        }
    }
}
END {
    total = imap + pop3
    printf "{\"status\":1,\"imap\":%d,\"pop3\":%d,\"total\":%d,\"error\":\"\"}\n", imap, pop3, total
}'
