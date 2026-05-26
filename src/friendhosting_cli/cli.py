from __future__ import annotations

from typing import Annotated

import typer

from .client import FriendhostingAPIError, FriendhostingClient
from .config import DEFAULT_API_URL, MissingCredentialsError, credential_status, load_credentials, write_config
from .output import error, print_json, success

app = typer.Typer(help="Agent-friendly CLI for the public Friendhosting API.", no_args_is_help=True)
auth_app = typer.Typer(help="Credential setup and status commands.", no_args_is_help=True)
app.add_typer(auth_app, name="auth")

ServiceType = Annotated[str, typer.Option("--type", help="Tariff plan type: hosting, vds, or dedicated.")]
OrderId = Annotated[str, typer.Option("--order-id", help="Friendhosting order ID.")]
YesFlag = Annotated[bool, typer.Option("--yes", help="Confirm a mutating or billable operation.")]


def _client() -> FriendhostingClient:
    return FriendhostingClient(load_credentials())


def _run_api(command: str, **params: object) -> None:
    try:
        data = _client().request(command, **params)
        print_json(success(command, data))
    except MissingCredentialsError as exc:
        print_json(error(command, str(exc), error_code="MISSING_CREDENTIALS"))
        raise typer.Exit(2) from exc
    except FriendhostingAPIError as exc:
        print_json(error(command, exc.error_msg or "Friendhosting API error.", error_code=exc.error_code, data=exc.data))
        raise typer.Exit(1) from exc


def _require_yes(command: str, yes: bool) -> None:
    if yes:
        return
    print_json(error(command, f"`{command}` requires --yes because it can change or bill a service.", error_code="CONFIRMATION_REQUIRED"))
    raise typer.Exit(2)


@auth_app.command("setup")
def auth_setup(
    login: Annotated[str | None, typer.Option("--login", help="Friendhosting login.")] = None,
    api_key: Annotated[str | None, typer.Option("--api-key", help="Friendhosting API key. Prefer interactive input when typing manually.")] = None,
    api_url: Annotated[str, typer.Option("--api-url", help="Friendhosting API endpoint.")] = DEFAULT_API_URL,
) -> None:
    """Interactively save credentials to ./.friendhosting/config.json."""
    if login is None:
        login = typer.prompt("Friendhosting login")
    if api_key is None:
        api_key = typer.prompt("Friendhosting API key", hide_input=True)
    path = write_config(login=login, api_key=api_key, api_url=api_url)
    print_json(
        success(
            "auth setup",
            {
                "config_path": str(path),
                "login": login,
                "api_url": api_url,
                "warning": "API key is stored in plaintext. Keep .friendhosting/ out of git.",
            },
        )
    )


@auth_app.command("status")
def auth_status() -> None:
    """Show which credential source is active without printing secrets."""
    print_json(success("auth status", credential_status()))


@app.command()
def balance() -> None:
    """Get the user's balance."""
    _run_api("getBalance")


@app.command()
def tariffs(service_type: ServiceType = "hosting") -> None:
    """Get tariff plans for a service type."""
    _run_api("getTarifs", vid=service_type)


@app.command()
def orders(order_id: Annotated[str | None, typer.Option("--order-id", help="Optional Friendhosting order ID.")] = None) -> None:
    """Get all orders, or a single order if --order-id is provided."""
    _run_api("getOrders", orderid=order_id)


@app.command()
def create(
    service_type: ServiceType,
    tariff_id: Annotated[str, typer.Option("--tariff-id", help="Tariff plan ID.")],
    period: Annotated[str, typer.Option("--period", help="Order period in months.")],
    domain: Annotated[str | None, typer.Option("--domain", help="Domain name for the order.")] = None,
    addons: Annotated[str | None, typer.Option("--addons", help="Comma-separated addon IDs.")] = None,
    yes: YesFlag = False,
) -> None:
    """Create a new order."""
    command = "createOrder"
    _require_yes(command, yes)
    _run_api(command, vid=service_type, tarifid=tariff_id, period=period, domain=domain, addons=addons)


@app.command()
def renew(order_id: OrderId, period: Annotated[str, typer.Option("--period", help="Renewal period in months.")], yes: YesFlag = False) -> None:
    """Renew an order."""
    command = "renewOrder"
    _require_yes(command, yes)
    _run_api(command, orderid=order_id, period=period)


@app.command()
def suspend(order_id: OrderId, yes: YesFlag = False) -> None:
    """Suspend an order."""
    command = "suspendOrder"
    _require_yes(command, yes)
    _run_api(command, orderid=order_id)


@app.command()
def unsuspend(order_id: OrderId, yes: YesFlag = False) -> None:
    """Start a suspended order."""
    command = "unSuspendOrder"
    _require_yes(command, yes)
    _run_api(command, orderid=order_id)


@app.command()
def restart(order_id: OrderId, yes: YesFlag = False) -> None:
    """Restart an order where the API supports it."""
    command = "restartOrder"
    _require_yes(command, yes)
    _run_api(command, orderid=order_id)


@app.command()
def reinstall(order_id: OrderId, yes: YesFlag = False) -> None:
    """Reinstall an order where the API supports it."""
    command = "reinstallOrder"
    _require_yes(command, yes)
    _run_api(command, orderid=order_id)
