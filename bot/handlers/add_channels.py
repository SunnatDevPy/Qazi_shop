from aiogram import Router, Bot, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.buttuns.inline import confirm_channels, show_channels
from bot.detail import channel_detail
from bot.state.states import ForwardState, AddChannelState
from db import Channel

channels_router = Router()

''' ============       Get ID handler      =============='''


@channels_router.message(ForwardState.chat_id)
async def get_id(message: Message, state: FSMContext):
    chat_id = ''
    username = ''
    type = 'private'
    if message.forward_from:
        chat_id = message.forward_from.id
        username = message.forward_from.username
        type = 'Bot' if message.forward_from.is_bot == True else 'User'
    if message.forward_from_chat:
        chat_id = message.forward_from_chat.id
        username = message.forward_from_chat.username
        type = message.forward_from_chat.type
    text = f'''
Forward {type}
chat_id: <code>{chat_id}</code>
Username: <code>@{username}</code>
    '''
    await message.answer(text=text, parse_mode='html')
    await state.clear()


'''============     CHANAL add handler   ===================='''


@channels_router.callback_query(F.data.startswith('channel_'))
async def clear_channel(call: CallbackQuery, bot: Bot, state: FSMContext):
    data = call.data.split('_')
    await call.answer()
    if data[1] == 'add':
        await state.set_state(AddChannelState.chat_id)
        await call.message.answer('Chat id ni kiriting')
    if data[1] == 'clear':
        await Channel.delete(int(data[-1]))
        await call.answer(f'Kanal o\'chdi {data[-1]}', show_alert=True)
        await call.message.edit_text('Kanallar ro\'yxati',
                                     reply_markup=await show_channels(bot=bot))


@channels_router.message(AddChannelState.chat_id)
async def add_channel(message: Message, bot: Bot, state: FSMContext):
    chat = []
    try:
        chat = await bot.get_chat(message.text)
    except:
        await message.answer(f"Bu kanalga meni admin qling")
    if chat:
        await state.set_state(AddChannelState.confirm)
        await state.update_data(info_chat=chat)
        text = channel_detail(chat)
        await message.answer(text, parse_mode="HTML",
                             reply_markup=confirm_channels(chat.title, chat.username))
    else:
        await message.answer('Chat id notog\'ri')


@channels_router.callback_query(F.data.endswith('_add_channel'), AddChannelState.confirm)
async def confirm_channelss(call: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = call.data.split('_')
    if data[0] == 'confirm':
        data = await state.get_data()
        channel = data['info_chat']
        try:
            # link = await bot.create_chat_invite_link(channel.id)
            await Channel.create(id=int(channel.id), url=channel.invite_link, title=channel.title)
        except TelegramBadRequest as e:
            await call.message.answer('Kanalda yo\'qmanku')
        await call.message.delete()
        await call.message.answer(f'Yangi {channel.type} qo\'shildi')
        await state.clear()
    elif data[0] == 'cancel':
        await call.message.delete()
        await call.message.answer('Protsess toxtatildi')
        await state.clear()
