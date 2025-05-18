from custom_components.vaillantcloud import SystemCoordinator
from custom_components.vaillantcloud.number import SystemManualCoolingDays
from myVaillant.api import MyVaillantAPI
from myVaillant.tests.generate_test_data import DATA_DIR
from myVaillant.tests.utils import load_test_data


async def test_manual_cooling_days(
    vaillantcloud_aioresponses,
    mocked_api: MyVaillantAPI,
    system_coordinator_mock: SystemCoordinator,
):
    test_data = load_test_data(DATA_DIR / "ventilation")
    with vaillantcloud_aioresponses(test_data) as _:
        system_coordinator_mock.data = (
            await system_coordinator_mock._async_update_data()
        )
        assert system_coordinator_mock.data[0].is_cooling_allowed is True
        manual_cooling = SystemManualCoolingDays(0, system_coordinator_mock)
        assert manual_cooling.native_value == 0
        await mocked_api.aiohttp_session.close()
