# portcheck-cli

A small, dependency-free command-line tool that checks whether a single
`host:port` is currently accepting TCP connections.

## Why

"Is the service actually listening?" is a question that comes up
constantly while debugging — a container that didn't bind its port, a
firewall rule that's blocking traffic, a typo in a config. `portcheck-cli`
answers it in one command with a clear exit code, so it drops straight
into a shell script or CI step.

**This checks one host:port at a time by design — not a network scanner.**
There is no range scanning, no sweeping multiple hosts, and no plan to add
either; use a dedicated network scanner if that's what you need.

## Install

```bash
pip install .
```

This installs a `portcheck-cli` command on your PATH.

## Usage

```bash
portcheck-cli example.com:443
```

```
example.com:443 is open
```

```bash
portcheck-cli localhost:9999
```

```
localhost:9999 refused the connection
```

Adjust the timeout for slow links:

```bash
portcheck-cli example.com:443 --timeout 5
```

### Options

| Flag         | Description                                     |
|--------------|--------------------------------------------------|
| `--timeout`  | Connection timeout in seconds (default: `2`)     |

### Exit codes

- `0` — the port is open
- `1` — the port is closed or refused the connection
- `2` — the host couldn't be resolved, or another error occurred

## Development

```bash
pip install -e .
python -m unittest discover -s tests -v
```

## License

All rights reserved. This code is public for viewing and reference only —
no license is granted to use, copy, modify, or redistribute it. See
[LICENSE](LICENSE) for details.
