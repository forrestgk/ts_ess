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

"""Implementation of ESS Instrument object."""

__all__ = ["EssInstrument"]

import asyncio
import logging
from typing import Any, Dict


class EssInstrument:
    """Instrument read-loop thread.

    Parameters
    ----------
    name : `str`
        Name of the Instrument instance.
    reader : `reader`
        Device read instance.
    callback_func : `func`
        Callback function to receive instrument output.

    Raises
    ------
    IndexError if attempted multiple use of instance name.
    IndexError if attempted multiple use of serial device instance.
    """

    def __init__(self, name: str, reader, callback_func, log=None):
        self._instances: Dict[str, "EssInstrument"] = {}
        self._devices: Dict[str, "EssInstrument"] = {}
        if log is None:
            self.log = logging.getLogger(type(self).__name__)
        else:
            self.log = log.getChild(type(self).__name__)
        if name not in self._instances:
            if reader.comport not in self._devices:
                try:
                    self._reader = reader
                except AttributeError:
                    self.log.debug(
                        f"EssInstrument:{name}: Failed to instantiate "
                        f"using reader object {reader.name!r}."
                    )
                self._enabled: bool = False
                self.name: str = name
                self._callback_func = callback_func
                self.telemetry_loop = None

                self._instances[name] = self
                self._devices[reader.comport] = self
                self.log.debug(
                    f"EssInstrument:{name}: First instantiation "
                    f"using reader object {reader.name!r}."
                )
            else:
                self.log.debug(
                    f"EssInstrument:{name}: Error: "
                    f"Attempted multiple use of reader serial device instance {reader.comport}."
                )
                raise IndexError(
                    f"EssInstrument:{name}: "
                    f"Attempted multiple use of reader serial device instance {reader.comport}."
                )
        else:
            self.log.debug(
                "EssInstrument: Error: "
                f"Attempted multiple instantiation of {name!r}."
            )
            raise IndexError(
                "EssInstrument: Error: "
                f"Attempted multiple instantiation of {name!r}."
            )

    async def _message(self, text: Any) -> None:
        # Print a message prefaced with the InstrumentThread object info.
        self.log.debug(f"EssInstrument:{self.name}: {text}")

    async def start(self):
        """Start the instrument read loop."""
        msg = f"Starting read loop for {self._reader.name!r} instrument."
        await self._message(msg)
        self._enabled = True
        self.telemetry_loop = asyncio.ensure_future(self._run())

    async def stop(self):
        """Terminate the instrument read loop."""
        msg = f"Stopping read loop for {self._reader.name!r} instrument."
        await self._message(msg)
        self.telemetry_loop.cancel()
        await self._reader.stop()
        self._enabled = False

    async def _run(self):
        """Run threaded instrument read loop.

        If enabled, loop and read the serial instrument and pass result to
        callback_func function.
        """
        msg = "Starting reader."
        await self._message(msg)
        await self._reader.start()
        while self._enabled:
            msg = "Reading data."
            await self._message(msg)
            await self._reader.read()
            await self._callback_func(self._reader.output)
