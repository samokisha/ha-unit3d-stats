"""Adds config flow for UNIT3D."""

from __future__ import annotations

import ipaddress
from typing import TYPE_CHECKING, Any

import voluptuous as vol
import yarl
from homeassistant import config_entries
from homeassistant.const import CONF_API_TOKEN, CONF_URL
from homeassistant.core import callback
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.util.network import (
    is_ip_address,
    is_link_local,
    is_loopback,
    is_private,
)
from slugify import slugify

from .api import (
    Unit3dApiClient,
    Unit3dApiClientAuthenticationError,
    Unit3dApiClientCommunicationError,
    Unit3dApiClientError,
    is_mock_enabled,
)
from .const import (
    CONF_ALLOW_INSECURE,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL_MINUTES,
    DOMAIN,
    LOGGER,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from homeassistant.config_entries import ConfigEntry

# Tailscale's CGNAT range (RFC 6598 shared address space). HA's is_private()/
# is_local() don't cover it, so it needs to be checked explicitly.
_TAILSCALE_CGNAT = ipaddress.ip_network("100.64.0.0/10")

_LOCAL_HOST_SUFFIXES = (".local", ".lan", ".internal", ".ts.net")


def _is_local_host(host: str) -> bool:
    """Return whether the host is on a local/trusted network (LAN, loopback, VPN)."""
    if is_ip_address(host):
        address = ipaddress.ip_address(host)
        return (
            is_private(address)
            or is_loopback(address)
            or is_link_local(address)
            or address in _TAILSCALE_CGNAT
        )
    host = host.lower()
    return "." not in host or host.endswith(_LOCAL_HOST_SUFFIXES)


def _account_slug(base_url: str, username: str) -> str:
    """Build the stable per-account unique ID from the host and username."""
    return slugify(f"{yarl.URL(base_url).host}-{username}")


class Unit3dFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for UNIT3D."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            parsed_url = yarl.URL(user_input[CONF_URL])
            if parsed_url.scheme not in ("http", "https") or parsed_url.host is None:
                _errors["base"] = "invalid_url"
            elif (
                parsed_url.scheme == "http"
                and not _is_local_host(parsed_url.host)
                and not user_input.get(CONF_ALLOW_INSECURE, False)
            ):
                _errors["base"] = "insecure_http"
            else:
                try:
                    user_data = await self._test_credentials(
                        base_url=user_input[CONF_URL],
                        api_token=user_input[CONF_API_TOKEN],
                    )
                except Unit3dApiClientAuthenticationError as exception:
                    LOGGER.warning(exception)
                    _errors["base"] = "auth"
                except Unit3dApiClientCommunicationError as exception:
                    LOGGER.error(exception)
                    _errors["base"] = "connection"
                except Unit3dApiClientError as exception:
                    LOGGER.exception(exception)
                    _errors["base"] = "unknown"
                else:
                    host = parsed_url.host
                    username = user_data["username"]
                    await self.async_set_unique_id(
                        unique_id=_account_slug(user_input[CONF_URL], username),
                    )
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=f"{username} ({host})",
                        data={
                            CONF_URL: user_input[CONF_URL],
                            CONF_API_TOKEN: user_input[CONF_API_TOKEN],
                        },
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_URL,
                        default=(user_input or {}).get(CONF_URL, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.URL,
                        ),
                    ),
                    vol.Required(CONF_API_TOKEN): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        ),
                    ),
                    vol.Optional(
                        CONF_ALLOW_INSECURE,
                        default=(user_input or {}).get(CONF_ALLOW_INSECURE, False),
                    ): selector.BooleanSelector(),
                },
            ),
            errors=_errors,
        )

    async def async_step_reauth(
        self,
        entry_data: Mapping[str, Any],  # noqa: ARG002 Unused function argument
    ) -> config_entries.ConfigFlowResult:
        """Perform reauth when the tracker rejects the stored API token."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Ask the user for a new API token and validate it."""
        _errors = {}
        reauth_entry = self._get_reauth_entry()
        if user_input is not None:
            try:
                user_data = await self._test_credentials(
                    base_url=reauth_entry.data[CONF_URL],
                    api_token=user_input[CONF_API_TOKEN],
                )
            except Unit3dApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except Unit3dApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except Unit3dApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                new_slug = _account_slug(
                    reauth_entry.data[CONF_URL],
                    user_data["username"],
                )
                if new_slug != reauth_entry.unique_id:
                    return self.async_abort(reason="wrong_account")
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data={
                        **reauth_entry.data,
                        CONF_API_TOKEN: user_input[CONF_API_TOKEN],
                    },
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_TOKEN): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )

    async def _test_credentials(self, base_url: str, api_token: str) -> dict[str, Any]:
        """Validate credentials and return the user's profile data."""
        client = Unit3dApiClient(
            base_url=base_url,
            api_token=api_token,
            session=async_create_clientsession(self.hass),
            use_mock=is_mock_enabled(),
        )
        return await client.async_get_user()

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,  # noqa: ARG004 Unused function argument: `config_entry`
    ) -> Unit3dOptionsFlowHandler:
        """Get the options flow for this handler."""
        return Unit3dOptionsFlowHandler()


class Unit3dOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow for UNIT3D."""

    async def async_step_init(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_UPDATE_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_UPDATE_INTERVAL,
                            DEFAULT_UPDATE_INTERVAL_MINUTES,
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=5,
                            mode=selector.NumberSelectorMode.BOX,
                            unit_of_measurement="min",
                        ),
                    ),
                },
            ),
        )
