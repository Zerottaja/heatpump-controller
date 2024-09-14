import aiohttp
import asyncio
import pymelcloud
import configparser

conf = configparser.ConfigParser()
conf.read('config.ini')

async def __update_melcloud(state_request):

    async with aiohttp.ClientSession() as session:
        # call the login method with the session
        token = await pymelcloud.login(conf['Credentials']['melcloudemail'], \
                                       conf['Credentials']['melcloudpassword'], \
                                       session=session)

        # lookup the device
        devices = await pymelcloud.get_devices(token, session=session)
        device = devices[pymelcloud.DEVICE_TYPE_ATA][0]

        # perform logic on the device
        await device.update()

        print("MELCloud login ok, setting {}-heatpump state to {}." \
              .format(device.name, state_request))
        await device.set({"power": state_request, \
                          "target_temperature": int(conf['Heatpump']['targettemperature']), \
                          "operation_mode": conf['Heatpump']['operationmode'], \
                          "fan_speed": conf['Heatpump']['fanspeed'], \
                          "vane_horizontal": conf['Heatpump']['vanehorizontal'], \
                          "vane_vertical": conf['Heatpump']['vanevertical']})
        await session.close()


def set_heatpump_state(state_request):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(__update_melcloud(state_request))


