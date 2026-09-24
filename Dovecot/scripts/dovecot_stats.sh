#!/bin/sh
# Script: dovecot_stats.sh
# Version: 3.0.0
# Purpose: Collect Dovecot session metrics for Zabbix as JSON.
# Author: Karim Mansur / Net Tech
#
# Security model:
# - This script MUST run as the unprivileged Zabbix agent user.
# - It first tries "doveadm who -1" without privilege escalation.
# - If access to the Dovecot anvil socket is denied, only the exact
#   "doveadm who -1" command is retried through sudo -n.
# - Never grant sudo permission for this script itself.
#
# Compatibility:
# - FreeBSD: /usr/local/bin/doveadm and /usr/local/sbin/dovecot
# - Linux:   /usr/bin/doveadm and /usr/sbin/dovecot
# - DOVECOT_DOVEADM and DOVECOT_BINARY are supported for testing or
#   non-standard installations. Sudoers must still explicitly allow the
#   resolved doveadm path and exact "who -1" arguments.

set -u

VERSION="3.0.0"

print_error() {
    printf '{"status":0,"imap":0,"pop3":0,"total":0,"users":0,"max_user_connections":0,"error":"%s"}\n' "$1"
}

find_executable() {
    override="$1"
    shift

    if [ -n "$override" ]; then
        [ -x "$override" ] && {
            printf '%s\n' "$override"
            return 0
        }
        return 1
    fi

    for candidate in "$@"; do
        if [ -x "$candidate" ]; then
            printf '%s\n' "$candidate"
            return 0
        fi
    done

    return 1
}

find_sudo() {
    for candidate in /usr/local/bin/sudo /usr/bin/sudo; do
        if [ -x "$candidate" ]; then
            printf '%s\n' "$candidate"
            return 0
        fi
    done

    return 1
}

get_doveadm() {
    find_executable "${DOVECOT_DOVEADM:-}" /usr/local/bin/doveadm /usr/bin/doveadm
}

get_dovecot() {
    find_executable "${DOVECOT_BINARY:-}" /usr/local/sbin/dovecot /usr/sbin/dovecot
}

print_version() {
    DOVECOT="$(get_dovecot)" || {
        printf 'dovecot_not_executable\n' >&2
        return 1
    }

    "$DOVECOT" --version 2>/dev/null | /usr/bin/awk 'NR == 1 { print $1; exit }'
}

collect_stats() {
    DOVEADM="$(get_doveadm)" || {
        print_error "doveadm_not_executable"
        return 0
    }

    WHO_OUTPUT=""

    # Least privilege: prefer direct access when the Zabbix user is already
    # allowed to query the Dovecot anvil socket.
    if WHO_OUTPUT="$("$DOVEADM" who -1 2>/dev/null)"; then
        :
    else
        SUDO="$(find_sudo)" || {
            print_error "doveadm_who_failed"
            return 0
        }

        if ! WHO_OUTPUT="$("$SUDO" -n "$DOVEADM" who -1 2>/dev/null)"; then
            print_error "doveadm_who_failed"
            return 0
        fi
    fi

    printf '%s\n' "$WHO_OUTPUT" | /usr/bin/awk '
    BEGIN {
        imap = 0
        pop3 = 0
        users = 0
        max_user_connections = 0
    }

    function clean_token(value) {
        gsub(/^[^a-z0-9_]+/, "", value)
        gsub(/[^a-z0-9_]+$/, "", value)
        return value
    }

    {
        # "doveadm who -1" normally prints a header such as:
        # username proto pid ip
        # or:
        # username service pid ip
        if (tolower($1) == "username") {
            next
        }

        protocol = ""

        # Skip the first field because it is normally the username.
        for (i = 2; i <= NF; i++) {
            token = clean_token(tolower($i))

            if (token == "imap") {
                protocol = "imap"
                break
            }

            if (token == "pop3" || token == "pop") {
                protocol = "pop3"
                break
            }
        }

        # Ignore non-mail-access services such as sieve. The users metric is
        # intentionally scoped to IMAP/POP3 so it remains comparable to total.
        if (protocol == "") {
            next
        }

        if (protocol == "imap") {
            imap++
        } else {
            pop3++
        }

        username = $1

        if (!(username in seen_user)) {
            seen_user[username] = 1
            users++
        }

        per_user[username]++

        if (per_user[username] > max_user_connections) {
            max_user_connections = per_user[username]
        }
    }

    END {
        total = imap + pop3

        printf "{\"status\":1,\"imap\":%d,\"pop3\":%d,\"total\":%d,\"users\":%d,\"max_user_connections\":%d,\"error\":\"\"}\n", \
            imap, pop3, total, users, max_user_connections
    }'
}

case "${1:-stats}" in
    stats)
        collect_stats
        ;;
    version)
        print_version
        ;;
    collector-version)
        printf '%s\n' "$VERSION"
        ;;
    *)
        printf 'Usage: %s [stats|version|collector-version]\n' "$0" >&2
        exit 2
        ;;
esac
