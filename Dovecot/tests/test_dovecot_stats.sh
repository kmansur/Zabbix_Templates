#!/bin/sh
set -eu
PROJECT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT
FAKE_DOVEADM="$TMPDIR/doveadm"
cat > "$FAKE_DOVEADM" <<EOF
#!/bin/sh
if [ "\$1" = "who" ] && [ "\${2:-}" = "-1" ]; then
    cat "$PROJECT_DIR/tests/sample_doveadm_who_one_line.txt"
    exit 0
fi
exit 1
EOF
chmod 755 "$FAKE_DOVEADM"
RESULT="$(DOVECOT_DOVEADM="$FAKE_DOVEADM" "$PROJECT_DIR/dovecot_stats.sh")"
printf '%s
' "$RESULT" | grep '"status":1' >/dev/null
printf '%s
' "$RESULT" | grep '"imap":4' >/dev/null
printf '%s
' "$RESULT" | grep '"pop3":1' >/dev/null
printf '%s
' "$RESULT" | grep '"total":5' >/dev/null
IMAP_COUNT="$(DOVECOT_DOVEADM="$FAKE_DOVEADM" "$PROJECT_DIR/legacy/zabbix-5.0/dovecot_num_imap.sh")"
POP_COUNT="$(DOVECOT_DOVEADM="$FAKE_DOVEADM" "$PROJECT_DIR/legacy/zabbix-5.0/dovecot_num_pop.sh")"
[ "$IMAP_COUNT" = "4" ]
[ "$POP_COUNT" = "1" ]
echo "OK: dovecot_stats.sh parser test passed"
