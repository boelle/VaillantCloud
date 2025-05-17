from unittest.mock import Mock

import pytest
from homeassistant.helpers.entity_registry import DATA_REGISTRY, EntityRegistry
from homeassistant.loader import DATA_COMPONENTS, DATA_INTEGRATIONS

from custom_components.VaillantCloud import SystemCoordinator
from myVaillant.api import MyVaillantAPI
from myVaillant.models import System
from myVaillant.tests.generate_test_data import DATA_DIR
from myVaillant.tests.utils import list_test_data, load_test_data

from custom_components.VaillantCloud.binary_sensor import (
    CircuitIsCoolingAllowed,
    ControlError,
    ControlOnline,
    SystemControlEntity,
    async_setup_entry,
    ZoneIsManualCoolingActive,
)
from custom_components.VaillantCloud.utils import CircuitEntity
from custom_components.VaillantCloud.const import DOMAIN
from tests.utils import get_config_entry


@pytest.mark.parametrize("test_data", list_test_data())
async def test_async_setup_binary_sensors(
    hass,
    myvaillant_aioresponses,
    mocked_api: MyVaillantAPI,
    system_coordinator_mock,
    test_data,
):
    hass.data[DATA_COMPONENTS] = {}
    hass.data[DATA_INTEGRATIONS] = {}
    hass.data[DATA_REGISTRY] = EntityRegistry(hass)
    with myvaillant_aioresponses(test_data) as _:
        config_entry = get_config_entry()
        system_coordinator_mock.data = (
            await system_coordinator_mock._async_update_data()
        )
        hass.data[DOMAIN] = {
            config_entry.entry_id: {"system_coordinator": system_coordinator_mock}
        }
        mock = Mock(return_value=None)
        await async_setup_entry(hass, config_entry, mock)
        mock.assert_called_once()
        assert len(mock.call_args.args[0]) > 0

        await mocked_api.aiohttp_session.close()


@pytest.mark.parametrize("test_data", list_test_data())
async def test_system_binary_sensors(
    myvaillant_aioresponses, mocked_api: MyVaillantAPI, system_coordinator_mock, test_data
):
    with myvaillant_aioresponses(test_data) as _:
        system_coordinator_mock.data = (
            await system_coordinator_mock._async_update_data()
        )
        system = SystemControlEntity(0, system_coordinator_mock)
        assert isinstance(system.device_info, dict)

        circuit = CircuitEntity(0, 0, system_coordinator_mock)
        assert isinstance(circuit.device_info, dict)
        assert isinstance(circuit.system, System)

        assert isinstance(ControlError(0, system_coordinator_mock).is_on, bool)
        assert isinstance(ControlError(0, system_coordinator_mock).name, str)
        assert ControlOnline(0, system_coordinator_mock).is_on is True
        assert isinstance(ControlOnline(0, system_coordinator_mock).name, str)
        # TODO: May  moved to zones, see no_cooling.yaml
        # assert isinstance(
        #    CircuitIsCoolingAllowed(0, 0, system_coordinator_mock).is_on, bool
        # )
        assert isinstance(
            CircuitIsCoolingAllowed(0, 0, system_coordinator_mock).name, str
        )
        await mocked_api.aiohttp_session.close()


async def test_control_error(
    myvaillant_aioresponses,
    mocked_api: MyVaillantAPI,
    system_coordinator_mock: SystemCoordinator,
):
    test_data = load_test_data(DATA_DIR / "ambisense2.yaml")
    with myvaillant_aioresponses(test_data) as _:
        system_coordinator_mock.data = (
            await system_coordinator_mock._async_update_data()
        )
        control_error = ControlError(0, system_coordinator_mock)
        assert control_error.is_on
        await mocked_api.aiohttp_session.close()


async def test_is_manual_cooling_active(
    myvaillant_aioresponses,
    mocked_api: MyVaillantAPI,
    system_coordinator_mock: SystemCoordinator,
):
    test_data = load_test_data(DATA_DIR / "ventilation")
    with myvaillant_aioresponses(test_data) as _:
        system_coordinator_mock.data = (
            await system_coordinator_mock._async_update_data()
        )
        manual_cooling = ZoneIsManualCoolingActive(0, 0, system_coordinator_mock)
        assert not manual_cooling.is_on
        await mocked_api.aiohttp_session.close()
