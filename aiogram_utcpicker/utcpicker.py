from datetime import datetime, timedelta
from aiogram.types import CallbackQuery
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from enum import Enum

LOC_ENG = {'cancel_button': 'Cancel', 'confirm_button': 'Confirm',

           'display_value': 'Time according to selected: ',

           'err_msg_invalid': 'Not a valid timezone'}
UTC_MINUTE_VALUES = [0, 30, 45]
UTC_HOUR_VALUES = [x for x in range(15)]
VALID_TIMEZONES = ('UTC +00:00',
                   'UTC -00:00',
                   'UTC +01:00',
                   'UTC +02:00',
                   'UTC +03:00',
                   'UTC +03:30',
                   'UTC +04:00',
                   'UTC +04:30',
                   'UTC +05:00',
                   'UTC +05:30',
                   'UTC +05:45',
                   'UTC +06:00',
                   'UTC +06:30',
                   'UTC +07:00',
                   'UTC +08:00',
                   'UTC +08:45',
                   'UTC +09:00',
                   'UTC +09:30',
                   'UTC +10:00',
                   'UTC +10:30',
                   'UTC +11:00',
                   'UTC +12:00',
                   'UTC +13:00',
                   'UTC +13:45',
                   'UTC +14:00',
                   'UTC -01:00',
                   'UTC -02:00',
                   'UTC -02:30',
                   'UTC -03:00',
                   'UTC -04:00',
                   'UTC -05:00',
                   'UTC -06:00',
                   'UTC -07:00',
                   'UTC -08:00',
                   'UTC -09:00',
                   'UTC -09:30',
                   'UTC -10:00',
                   'UTC -11:00')


class UtcPickerActions(str, Enum):
    ignore = 'IGNORE'
    increase_hour = 'INCREASE_HOUR'
    decrease_hour = 'DECREASE_HOUR'
    increase_minute = 'INCREASE_MINUTE'
    decrease_minute = 'DECREASE_MINUTE'
    change_sign = 'CHANGE_SIGN'
    cancel_selection = 'CANCEL_SELECTION'
    confirm_utc = 'CONFIRM_UTC'


class UtcPickerCallback(CallbackData, prefix='utc_picker'):
    action: str = ''
    hour: int = 0
    minute: int = 0
    sign: str = '+'


async def get_current_value(data: UtcPickerCallback):
    return (datetime.utcnow() + timedelta(hours=int(data.sign + str(data.hour)),
                                          minutes=int(data.sign + str(data.minute)))).strftime('%H:%M')


async def convert_to_minutes(data: tuple) -> int | None:
    if not data:
        return
    multiplier = 1
    if data[0] == '-':
        multiplier = -1
    return (data[1] * 60 + data[2]) * multiplier


async def validate_timezone(data: tuple) -> bool:
    if f"UTC {data[0]}{data[1]:02d}:{data[2]:02d}" not in VALID_TIMEZONES:
        return False
    return True


async def process_utc_picker(callback: CallbackQuery, data: UtcPickerCallback, loc_dict: dict = None):

    if not loc_dict:
        loc_dict = LOC_ENG

    canceled, selected, utc_difference = False, False, None
    match data.action:
        case UtcPickerActions.ignore:
            await callback.answer()
        case UtcPickerActions.change_sign:
            data.sign = '+' if data.sign == '-' else '-'
            await callback.message.edit_reply_markup(reply_markup=await start_utc_picker(data))
        case UtcPickerActions.increase_hour | UtcPickerActions.decrease_hour:
            data.hour = (UTC_HOUR_VALUES * 2)[UTC_HOUR_VALUES.index(data.hour) + {
                UtcPickerActions.increase_hour: 1, UtcPickerActions.decrease_hour: -1,
            }[data.action]]
            await callback.message.edit_reply_markup(reply_markup=await start_utc_picker(data))
        case UtcPickerActions.increase_minute | UtcPickerActions.decrease_minute:
            data.minute = (UTC_MINUTE_VALUES * 2)[UTC_MINUTE_VALUES.index(data.minute) + {
                UtcPickerActions.increase_minute: 1, UtcPickerActions.decrease_minute: -1,
            }[data.action]]
            await callback.message.edit_reply_markup(reply_markup=await start_utc_picker(data))
        case UtcPickerActions.cancel_selection:
            await callback.message.delete()
            canceled = True
        case UtcPickerActions.confirm_utc:
            utc_difference = data.sign, int(data.hour), int(data.minute)
            if await validate_timezone(utc_difference):
                selected = True
            else:
                await callback.answer(loc_dict['err_msg_invalid'])
    return canceled, selected, await convert_to_minutes(utc_difference)


async def start_utc_picker(data: UtcPickerCallback = UtcPickerCallback(),
                           loc_dict: dict = None) -> InlineKeyboardMarkup:
    if not loc_dict:
        loc_dict = LOC_ENG

    keyboard = [[], [], [], [], []]

    keyboard[0] = [
        InlineKeyboardButton(
            text=f"{loc_dict['display_value']} {await get_current_value(data)}",
            callback_data=UtcPickerCallback(
                action=UtcPickerActions.ignore,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        )
    ]

    keyboard[1] = [
        InlineKeyboardButton(
            text='↑',
            callback_data=UtcPickerCallback(
                action=UtcPickerActions.change_sign,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
        InlineKeyboardButton(
            text='↑',
            callback_data=UtcPickerCallback(
                action=UtcPickerActions.increase_hour,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
        InlineKeyboardButton(
            text=' ',
            callback_data=UtcPickerCallback(
                action=UtcPickerActions.ignore,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
        InlineKeyboardButton(
            text='↑',
            callback_data=UtcPickerCallback(
                action=UtcPickerActions.increase_minute,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
    ]

    keyboard[2] = [
        InlineKeyboardButton(
            text=data.sign,
            callback_data=UtcPickerCallback(
                action=UtcPickerActions.change_sign,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
        InlineKeyboardButton(
            text=f"{data.hour:02d}",
            callback_data=UtcPickerCallback(
                action=UtcPickerActions.ignore,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
        InlineKeyboardButton(
            text=':',
            callback_data=UtcPickerCallback(
                action=UtcPickerActions.ignore,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
        InlineKeyboardButton(
            text=f"{data.minute:02d}",
            callback_data=UtcPickerCallback(
                action=UtcPickerActions.ignore,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
    ]

    keyboard[3] = [
        InlineKeyboardButton(
            text='↓',
            callback_data=UtcPickerCallback(
                action=UtcPickerActions.change_sign,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
        InlineKeyboardButton(
            text='↓',
            callback_data=UtcPickerCallback(
                action=UtcPickerActions.decrease_hour,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
        InlineKeyboardButton(
            text=' ',
            callback_data=UtcPickerCallback(
                action=UtcPickerActions.ignore,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
        InlineKeyboardButton(
            text='↓',
            callback_data=UtcPickerCallback(
                action=UtcPickerActions.decrease_minute,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
    ]

    keyboard[4] = [
        InlineKeyboardButton(
            text=loc_dict['cancel_button'],
            callback_data=UtcPickerCallback(

                action=UtcPickerActions.cancel_selection,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()

        ),
        InlineKeyboardButton(
            text=loc_dict['confirm_button'],
            callback_data=UtcPickerCallback(

                action=UtcPickerActions.confirm_utc,
                hour=data.hour,
                minute=data.minute,
                sign=data.sign
            ).pack()
        ),
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
