from unittest.mock import AsyncMock
import pytest

from src.aiogram_utcpicker import start_utc_picker, UtcPickerCallback, process_utc_picker
from src.aiogram_utcpicker.utcpicker import VALID_TIMEZONES
from aiogram.types import InlineKeyboardMarkup


@pytest.mark.asyncio
async def test_init():
    assert await start_utc_picker()


@pytest.mark.asyncio
async def test_start_utc_picker():
    result = await start_utc_picker()

    assert isinstance(result, InlineKeyboardMarkup)


test_sets = [
    (UtcPickerCallback(**{'action': 'IGNORE', 'hour': 0, 'minute': 0, 'sign': '+'}), (False, False, None)),
    (UtcPickerCallback(**{'action': 'CONFIRM_UTC', 'hour': 0, 'minute': 30, 'sign': '+'}), (False, False, 30)),
    (UtcPickerCallback(**{'action': 'CONFIRM_UTC', 'hour': 0, 'minute': 45, 'sign': '+'}), (False, False, 45)),
    (UtcPickerCallback(**{'action': 'CANCEL_SELECTION', 'hour': 0, 'minute': 0, 'sign': '+'}), (True, False, None)),
]

for utc_value in VALID_TIMEZONES:

    _, value = utc_value.split()
    signed_hour, minute = value.split(':')
    sign, hour = signed_hour[0], signed_hour[1:]

    multiplier = 1
    if sign == '-':
        multiplier = -1

    test_sets.append(
        (UtcPickerCallback(**{'action': 'CONFIRM_UTC', 'hour': int(hour), 'minute': int(minute), 'sign': sign}),
         (False, True, (int(hour) * 60 + int(minute)) * multiplier))
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("callback_data, expected", test_sets)
async def test_process_selection(callback_data, expected):
    query = AsyncMock()
    result = await process_utc_picker(query, callback_data)
    assert result == expected
