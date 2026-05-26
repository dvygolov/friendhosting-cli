---
name: friendhosting
description: Operate Friendhosting through the public Friendhosting CLI/API. Use when Codex needs to inspect Friendhosting balance, tariff plans, or orders, or explicitly create, renew, suspend, unsuspend, restart, or reinstall a Friendhosting service from an agent workflow.
---

# Friendhosting

Use the `friendhosting` CLI as the only execution backend. Do not automate the web panel, scrape private endpoints, or invent unsupported VPS controls.

## Capability Boundary

Supported public API operations:

- `balance`
- `tariffs --type hosting|vds|dedicated`
- `orders [--order-id ID]`
- `create --type ... --tariff-id ... --period ... [--domain ...] [--addons ...] --yes`
- `renew --order-id ... --period ... --yes`
- `suspend --order-id ... --yes`
- `unsuspend --order-id ... --yes`
- `restart --order-id ... --yes`
- `reinstall --order-id ... --yes`

Do not claim support for start, stop, shutdown, reset, rescue, VNC, IP listing, backups, tickets, payments, or monitoring unless a later CLI version adds documented support.

## Credential Workflow

Use credentials in this order:

1. If `FRIENDHOSTING_LOGIN` and `FRIENDHOSTING_API_KEY` are already present, run the CLI directly.
2. If `./.friendhosting/config.json` exists in the project where the command is run, let the CLI read it.
3. If the user has configured KeePassXC variables such as `KPXC_CLI`, `KPXC_DB`, and a Friendhosting entry path, retrieve only the login/API key needed for the command and pass them as environment variables.
4. If no credentials are available, tell the user to run `friendhosting auth setup`.

Never print or log full API keys. Treat `./.friendhosting/config.json` as plaintext local secret storage.

For noninteractive setup, use `friendhosting auth setup --login ... --api-key ...` only when the user has explicitly supplied the secret in the current task or approved storing it locally.

## Command Rules

- Prefer read-only commands when the user asks to inspect or check state.
- Add `--yes` only when the user explicitly asked for a mutating or billable operation.
- Keep CLI output as JSON and summarize the relevant fields for the user.
- If the CLI returns `ok: false`, report `errorCode` and `errorMsg` without retrying destructive commands.
- Use `FRIENDHOSTING_API_URL` only when the user explicitly needs a non-default endpoint.

## Examples

Read-only:

```powershell
friendhosting balance
friendhosting tariffs --type vds
friendhosting orders
friendhosting orders --order-id 12345
```

Mutating, only after explicit user intent:

```powershell
friendhosting restart --order-id 12345 --yes
friendhosting renew --order-id 12345 --period 1 --yes
```
