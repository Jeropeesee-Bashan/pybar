from __future__ import annotations
from typing import Any, Dict, List, Tuple
from sdbus import (
    DbusDeprecatedFlag,
    DbusInterfaceCommonAsync,
    DbusNoReplyFlag,
    DbusPropertyConstFlag,
    DbusPropertyEmitsChangeFlag,
    DbusPropertyEmitsInvalidationFlag,
    DbusPropertyExplicitFlag,
    DbusUnprivilegedFlag,
    dbus_method_async,
    dbus_property_async,
    dbus_signal_async,
)


UPOWER = "org.freedesktop.UPower"
UPOWER_OBJECT = "/org/freedesktop/UPower"


class UPower(
    DbusInterfaceCommonAsync,
    interface_name="org.freedesktop.UPower",
):
    @dbus_method_async(
        result_signature="ao",
    )
    async def enumerate_devices(
        self,
    ) -> List[str]:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="o",
    )
    async def get_display_device(
        self,
    ) -> str:
        raise NotImplementedError

    @dbus_method_async(
        result_signature="s",
    )
    async def get_critical_action(
        self,
    ) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def daemon_version(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
    )
    def on_battery(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
    )
    def lid_is_closed(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
    )
    def lid_is_present(self) -> bool:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="o",
    )
    def device_added(self) -> str:
        raise NotImplementedError

    @dbus_signal_async(
        signal_signature="o",
    )
    def device_removed(self) -> str:
        raise NotImplementedError


class UPowerDevice(
    DbusInterfaceCommonAsync,
    interface_name="org.freedesktop.UPower.Device",
):
    @dbus_method_async(
    )
    async def refresh(
        self,
    ) -> None:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="suu",
        result_signature="a(udu)",
    )
    async def get_history(
        self,
        type: str,
        timespan: int,
        resolution: int,
    ) -> List[Tuple[int, float, int]]:
        raise NotImplementedError

    @dbus_method_async(
        input_signature="s",
        result_signature="a(dd)",
    )
    async def get_statistics(
        self,
        type: str,
    ) -> List[Tuple[float, float]]:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def native_path(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def vendor(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def model(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def serial(self) -> str:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="t",
    )
    def update_time(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
    )
    def type(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
    )
    def power_supply(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
    )
    def has_history(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
    )
    def has_statistics(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
    )
    def online(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="d",
    )
    def energy(self) -> float:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="d",
    )
    def energy_empty(self) -> float:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="d",
    )
    def energy_full(self) -> float:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="d",
    )
    def energy_full_design(self) -> float:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="d",
    )
    def energy_rate(self) -> float:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="d",
    )
    def voltage(self) -> float:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="i",
    )
    def charge_cycles(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="d",
    )
    def luminosity(self) -> float:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="x",
    )
    def time_to_empty(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="x",
    )
    def time_to_full(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="d",
    )
    def percentage(self) -> float:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="d",
    )
    def temperature(self) -> float:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
    )
    def is_present(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
    )
    def state(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="b",
    )
    def is_rechargeable(self) -> bool:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="d",
    )
    def capacity(self) -> float:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
    )
    def technology(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
    )
    def warning_level(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="u",
    )
    def battery_level(self) -> int:
        raise NotImplementedError

    @dbus_property_async(
        property_signature="s",
    )
    def icon_name(self) -> str:
        raise NotImplementedError
