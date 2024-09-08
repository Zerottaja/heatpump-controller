import aiohttp
import asyncio
import pymelcloud
import secrets

async def __update_melcloud(state_request):

    async with aiohttp.ClientSession() as session:
        # call the login method with the session
        token = await pymelcloud.login(secrets.user_email, secrets.user_password, session=session)

        # lookup the device
        devices = await pymelcloud.get_devices(token, session=session)
        device = devices[pymelcloud.DEVICE_TYPE_ATA][0]

        # perform logic on the device
        await device.update()

        print("MELCloud login ok, setting {}-heatpump state to {}.".format(device.name, state_request))
        await device.set({"power": state_request, "target_temperature": 23,
                          "operation_mode": "heat", "fan_speed": "3", })
        await session.close()


def set_heatpump_state(state_request):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(__update_melcloud(state_request))


