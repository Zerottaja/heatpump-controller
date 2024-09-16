'''This module calls Mitsubishi MELCloud via the pymelcloud module to set heatpump state.'''
from os import path
import configparser
import asyncio
import aiohttp
import pymelcloud
import light_logging

_dir_path = path.dirname(path.abspath(__file__))
_conf = configparser.ConfigParser()
_conf.read(path.join(_dir_path, '..', 'config.ini'))


async def __update_melcloud(state_request):
    '''Open MELCloud session, set device parameters.'''
    async with aiohttp.ClientSession() as session:
        # call the login method with the session
        token = await pymelcloud.login(_conf['Credentials']['melcloudemail'], \
                                       _conf['Credentials']['melcloudpassword'], \
                                       session=session)

        # lookup the device
        devices = await pymelcloud.get_devices(token, session=session)
        # TODO: allow ATW devices, allow multiple devices?
        device = devices[pymelcloud.DEVICE_TYPE_ATA][0]

        # perform logic on the device
        await device.update()

        light_logging.log(f'MELCloud login ok, setting {device.name}-heatpump state to {state_request}.')
        await device.set({'power': state_request, \
                          'target_temperature': int(_conf['Heatpump']['targettemperature']), \
                          'operation_mode': _conf['Heatpump']['operationmode'], \
                          'fan_speed': _conf['Heatpump']['fanspeed'], \
                          'vane_horizontal': _conf['Heatpump']['vanehorizontal'], \
                          'vane_vertical': _conf['Heatpump']['vanevertical']})
        await session.close()


def set_heatpump_state(state_request):
    '''Call async cloud session function with predetermined heating control state.'''
    loop = asyncio.get_event_loop()
    loop.run_until_complete(__update_melcloud(state_request))


if __name__ == '__main__':
    set_heatpump_state(True)
