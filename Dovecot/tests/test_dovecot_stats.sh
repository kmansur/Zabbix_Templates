#!/bin/sh
set -eu

PROJECT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
TMPDIR_TEST="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_TEST"' EXIT HUP INT TERM

FAKE_DOVEADM="$TMPDIR_TEST/doveadm"
FAKE_DOVECOT="$TMPDIR_TEST/dovecot"
FIXTURE="$TMPDIR_TEST/who.txt"

cat > "$FAKE_DOVEADM" <<'EOF'
#!/bin/sh
case "${DOVECOT_TEST_CASE:-fixture}" in
    fail)
        exit 1
        ;;
    empty)
        exit 0
        ;;
    fixture)
        cat "${DOVECOT_TEST_FIXTURE:?}"
        exit 0
        ;;
    *)
        exit 2
        ;;
esac
EOF

cat > "$FAKE_DOVECOT" <<'EOF'
#!/bin/sh
[ "${1:-}" = "--version" ] || exit 1
printf '2.4.5 (test build)\n'
EOF

chmod 755 "$FAKE_DOVEADM" "$FAKE_DOVECOT"

assert_contains() {
    value="$1"
    expected="$2"
    label="$3"

    printf '%s\n' "$value" | grep -F "$expected" >/dev/null || {
        printf 'FAIL: %s\nExpected: %s\nActual:   %s\n' "$label" "$expected" "$value" >&2
        exit 1
    }
}

# 1. Existing regression fixture: preserve the original connection counts.
RESULT="$(
    DOVECOT_DOVEADM="$FAKE_DOVEADM" \
    DOVECOT_TEST_CASE=fixture \
    DOVECOT_TEST_FIXTURE="$PROJECT_DIR/tests/sample_doveadm_who_one_line.txt" \
    /bin/sh "$PROJECT_DIR/scripts/dovecot_stats.sh" stats
)"

assert_contains "$RESULT" '"status":1' "collector status"
assert_contains "$RESULT" '"imap":4' "IMAP count"
assert_contains "$RESULT" '"pop3":1' "POP3 count"
assert_contains "$RESULT" '"total":5' "total count"
assert_contains "$RESULT" '"users":2' "unique user count"
assert_contains "$RESULT" '"max_user_connections":4' "maximum connections per user"

# 2. Empty output is valid and must not be reported as collector failure.
RESULT="$(
    DOVECOT_DOVEADM="$FAKE_DOVEADM" \
    DOVECOT_TEST_CASE=empty \
    /bin/sh "$PROJECT_DIR/scripts/dovecot_stats.sh" stats
)"

assert_contains "$RESULT" '"status":1' "empty output status"
assert_contains "$RESULT" '"total":0' "empty output total"
assert_contains "$RESULT" '"users":0' "empty output users"

# 3. Ignore non-IMAP/POP3 services and do not count the header as a user.
cat > "$FIXTURE" <<'EOF'
username service pid ip
alpha@example.net imap 100 192.0.2.10
alpha@example.net imap 101 192.0.2.10
beta@example.net pop3 102 192.0.2.11
gamma@example.net sieve 103 192.0.2.12
EOF

RESULT="$(
    DOVECOT_DOVEADM="$FAKE_DOVEADM" \
    DOVECOT_TEST_CASE=fixture \
    DOVECOT_TEST_FIXTURE="$FIXTURE" \
    /bin/sh "$PROJECT_DIR/scripts/dovecot_stats.sh" stats
)"

assert_contains "$RESULT" '"imap":2' "mixed IMAP count"
assert_contains "$RESULT" '"pop3":1' "mixed POP3 count"
assert_contains "$RESULT" '"total":3' "mixed total count"
assert_contains "$RESULT" '"users":2' "mixed unique user count"
assert_contains "$RESULT" '"max_user_connections":2' "mixed maximum connections per user"

# 4. Failed doveadm execution must still return valid JSON and status 0.
RESULT="$(
    DOVECOT_DOVEADM="$FAKE_DOVEADM" \
    DOVECOT_TEST_CASE=fail \
    PATH="$TMPDIR_TEST" \
    /bin/sh "$PROJECT_DIR/scripts/dovecot_stats.sh" stats
)"

assert_contains "$RESULT" '"status":0' "failure status"
assert_contains "$RESULT" '"error":"doveadm_who_failed"' "failure reason"

# 5. Version modes.
VERSION="$(DOVECOT_BINARY="$FAKE_DOVECOT" /bin/sh "$PROJECT_DIR/scripts/dovecot_stats.sh" version)"
[ "$VERSION" = "2.4.5" ] || {
    printf 'FAIL: Dovecot version. Actual: %s\n' "$VERSION" >&2
    exit 1
}

COLLECTOR_VERSION="$(/bin/sh "$PROJECT_DIR/scripts/dovecot_stats.sh" collector-version)"
[ "$COLLECTOR_VERSION" = "3.0.0" ] || {
    printf 'FAIL: collector version. Actual: %s\n' "$COLLECTOR_VERSION" >&2
    exit 1
}

echo "OK: Dovecot collector tests passed"
