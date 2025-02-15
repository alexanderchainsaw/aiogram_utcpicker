# aiogram_utcpicker
```
pip install aiogram-utcpicker
```

UTC selection tool for aiogram3 telegram bots

![img.png](img.png)
# Use case
The tool is designed to allow users interactively select valid timezones (listed at https://timezonedb.com/time-zones).

To enforce valid timezone selection, the tool has some restrictions:
 - Hours: Values only in the range of 0 to 14 (inclusively) are allowed.
 - Minutes: Can only be 0, 30 or 45.


Even with the restrictions listed above, it's still possible to select a timezone that is not listed at https://timezonedb.com/time-zones.

If that happens, an error message will be displayed ( as a  notification envoked by `callback.answer()` )

# Demo
```python
import logging
import asyncio
import sys
import aiogram.client.default
from aiogram_utcpicker import UtcPickerCallback, start_utc_picker, process_utc_picker
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery

dp = Dispatcher()

YOUR_API_TOKEN = ''


@dp.message(Command('utc_picker'))
async def cmd_utc_picker(message: Message):
    await message.answer(
        'Utc picker demo:\nTry changing the values and submitting\n'
        'Only the valid timezones will be accepted, otherwise an error notification will be displayed',
        reply_markup=await start_utc_picker()
    )


@dp.callback_query(UtcPickerCallback.filter())
async def process_utc_picker_selection(callback: CallbackQuery, callback_data: CallbackData):
    canceled, selected, utc_difference = await process_utc_picker(callback, callback_data)

    if canceled:
        await callback.message.answer('You have canceled utc picker selection')
    elif selected:
        await callback.message.answer(f'Selected value in minutes: {utc_difference}')


async def main():
    bot = Bot(YOUR_API_TOKEN, default=aiogram.client.default.DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
```

# Localization

By default, all captions are in english. 

To customize text captions, pass a `dict` with your translations to the `start_utc_picker()` function

It should have the following structure:
```python
{ # do NOT alter this column    # change values in this column to whatever language you need
  'cancel_button':              'Cancel', 
  'confirm_button':             'Confirm',
  'display_value':              'Time according to selected: ',
  'err_msg_invalid':            'Not a valid timezone'
}
```
