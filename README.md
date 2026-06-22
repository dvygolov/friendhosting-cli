```
                          friendhosting-cli
    _            __     __  _ _             __          __  _
   | |           \ \   / / | | |            \ \        / / | |
   | |__  _   _   \ \_/ /__| | | _____      _\ \  /\  / /__| |__
   | '_ \| | | |   \   / _ \ | |/ _ \ \ /\ / /\ \/  \/ / _ \ '_ \
   | |_) | |_| |    | |  __/ | | (_) \ V  V /  \  /\  /  __/ |_) |
   |_.__/ \__, |    |_|\___|_|_|\___/ \_/\_/    \/  \/ \___|_.__/
           __/ |
          |___/             https://yellowweb.top

If you like this script, PLEASE DONATE!
```

[Support this project](https://yellowweb.top/donate)


# Friendhosting CLI

Agent-friendly command-line interface for the public Friendhosting API.

The CLI only uses the documented HTTP gateway at `https://my.friendhosting.net/apih.php`.
It does not automate the web panel and does not implement private VPS controls such as
start, stop, shutdown, reset, rescue, VNC, backups, tickets, or payments.

## Install

```powershell
python -m pip install -e .
```

## Credentials

The CLI checks credentials in this order:

1. `FRIENDHOSTING_LOGIN` and `FRIENDHOSTING_API_KEY`
2. Project-local `./.friendhosting/config.json`

Create a local config:

```powershell
friendhosting auth setup
```

For automation, avoid interactive prompts:

```powershell
friendhosting auth setup --login "my-login" --api-key "my-api-key"
```

The project-local config stores the API key in plaintext. Keep `.friendhosting/` out of git.

## Usage

```powershell
friendhosting auth status
friendhosting balance
friendhosting tariffs --type vds
friendhosting orders
friendhosting orders --order-id 12345
friendhosting restart --order-id 12345 --yes
```

Every command prints JSON by default.

## Tests

```powershell
python -m pytest
```
