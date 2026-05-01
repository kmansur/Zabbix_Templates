# Advanced ICMP Ping with Jitter

Zabbix 7.0 template for ICMP latency, packet loss, jitter, and RTT deviation.

## Files

- `Advanced ICMP Ping with Jitter.yaml` - Zabbix 7.0 template export.
- `advanced_icmp_ping.py` - external script used by the template.

## Requirements

- Zabbix server or proxy with external scripts enabled.
- Python 3.6 or newer.
- `fping` installed and executable by the Zabbix user.

## Installation

Copy the Python collector to the Zabbix external scripts directory:

```sh
cp advanced_icmp_ping.py /usr/lib/zabbix/externalscripts/
chmod +x /usr/lib/zabbix/externalscripts/advanced_icmp_ping.py
```

Install `fping` if needed:

```sh
apt install fping
```

On FreeBSD:

```sh
pkg install fping
```

Import `Advanced ICMP Ping with Jitter.yaml` in Zabbix 7.0 and link the
template to hosts that have a valid host interface or `{HOST.CONN}` value.

## Collector

The collector runs one `fping` batch:

```sh
fping -q -C <count> -p <interval_ms> -t <timeout_ms> <host>
```

It returns JSON with these fields:

- `xmt` - transmitted packets.
- `rcv` - received packets.
- `loss` - packet loss percentage.
- `min` - minimum RTT in milliseconds.
- `avg` - average RTT in milliseconds.
- `max` - maximum RTT in milliseconds.
- `jitter` - average absolute difference between consecutive received RTTs.
- `stddev` - population standard deviation of received RTTs.
- `error` - empty on success, error message on collector failure.
- `rtts` - received RTT sample list for troubleshooting.

## Default Macros

- `{$ADV_FPING_POOL_COUNT}` = `20`
- `{$ADV_FPING_INTERVAL_MS}` = `100`
- `{$ADV_FPING_TIMEOUT_MS}` = `1000`
- `{$ADV_ICMP_LOSS_WARN}` = `20`
- `{$ADV_ICMP_JITTER_WARN}` = `20`
- `{$ADV_ICMP_RESPONSE_TIME_WARN}` = `200`
- `{$ADV_ICMP_MAX_TIME_MULTIPLE}` = `30`
- `{$ADV_ICMP_STDDEV_WARN}` = `30`

The default collector settings send 20 probes spaced 100 ms apart, giving a
measurement window of about 2 seconds.

## Triggers

- High ICMP ping response time.
- High ICMP ping loss.
- High ICMP ping jitter.
- High ICMP ping time differences.
- ICMP collector error.
- High ICMP RTT standard deviation, disabled by default.
- Unavailable by ICMP ping.
- Total Unavailable by ICMP ping, disabled by default.

## Versioning

Template vendor:

```yaml
vendor:
  name: 'Net Tech'
  version: 1.0-1
```

Every functional template change should increment `vendor.version`.
