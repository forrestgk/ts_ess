# This file is part of ts_ess.
#
# Developed for the Vera C. Rubin Observatory Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

import logging
import unittest

from lsst.ts.ess.sel_temperature_reader import SelTemperature, DELIMITER
from lsst.ts.ess.mock.mock_temperature_sensor import (
    MockTemperatureSensor,
    MIN_TEMP,
    MAX_TEMP,
)

logging.basicConfig(
    format="%(asctime)s:%(levelname)s:%(name)s:%(message)s", level=logging.INFO,
)


class SelTemperatureReaderTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_sel_temperature_reader(self):
        logging.info("test_ess_instrument_object")

        # Reset SelTemperature
        SelTemperature._instances = {}
        SelTemperature._devices = {}

        num_channels = 4
        device = MockTemperatureSensor("MockSensor", num_channels)
        sel_temperature = SelTemperature("MockSensor", device, num_channels)
        sel_temperature.read()
        data = sel_temperature.output
        self.assertEqual(num_channels + 2, len(data))
        for i in range(0, 4):
            data_item = data[i + 2]
            self.assertTrue(MIN_TEMP <= float(data_item) <= MAX_TEMP)

    async def test_old_sel_temperature_reader(self):
        logging.info("test_ess_instrument_object")

        # Reset SelTemperature
        SelTemperature._instances = {}
        SelTemperature._devices = {}

        num_channels = 4
        count_offset = 1
        device = MockTemperatureSensor("MockSensor", num_channels, count_offset)
        sel_temperature = SelTemperature("MockSensor", device, num_channels)
        sel_temperature.read()
        data = sel_temperature.output
        self.assertEqual(num_channels + 2, len(data))
        for i in range(0, 4):
            data_item = data[i + 2]
            self.assertTrue(MIN_TEMP <= float(data_item) <= MAX_TEMP)