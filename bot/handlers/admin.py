from aiogram import Bot, F, Router, html
from aiogram.enums import ChatMemberStatus
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.buttuns.inline import send_text, confirm_inl, link, admins, show_channels, make_channels
from bot.state.states import SendTextState, AddAdmin, ForwardState
from db import User
from db import Channel

admin_router = Router()


async def mandatory_channel(user_id, bot: Bot):
    form_kb = []
    channels = await Channel.get_all()
    for channel_id in channels:
        member = await bot.get_chat_member(channel_id.id, user_id)
        if member.status == ChatMemberStatus.LEFT:
            form_kb.append(channel_id.id)
    if form_kb:
        return form_kb
    else:
        return


@admin_router.callback_query(F.data.startswith('settings_'))
async def leagues_handler(call: CallbackQuery, bot: Bot, state: FSMContext):
    data = call.data.split('_')[-1]
    await call.answer()
    if data == 'static':
        users = await User.get_all()
        await call.message.answer(html.bold(f'Admin\nUserlar soni: {len(users)}'), parse_mode='HTML')
    elif data == 'send':
        await call.message.answer(html.bold("Xabarni qaysi usulda jo'natmoqchisiz❓"), parse_mode='HTML',
                                  reply_markup=send_text())
    elif data == 'admins':
        await call.message.delete()
        await call.message.answer(html.bold("Adminlar ro'yxati"), parse_mode='HTML', reply_markup=await admins())
    elif data == 'get-id':
        await state.set_state(ForwardState.chat_id)
        await call.message.answer(text='Forward qilib message tashlang')
    elif data == 'subscribe':
        await call.message.edit_text('Kanallar ro\'yxati',
                                     reply_markup=await show_channels(bot=bot))


@admin_router.callback_query(F.data.startswith('admins_'))
async def delete_admins(call: CallbackQuery, state: FSMContext):
    data = call.data.split('_')
    await call.answer()
    if data[1] == 'add':
        await call.message.delete()
        await state.set_state(AddAdmin.user_id)
        await call.message.answer(html.bold("User idni kiriting"), parse_mode='HTML')
    if data[1] == 'delete':
        try:
            await User.update(id_=int(data[-1]), admin=False)
            await call.message.edit_text(html.bold("Adminlar ro'yxati"), parse_mode='HTML', reply_markup=await admins())
        except:
            await call.message.answer('Xatolik yuz berdi')


@admin_router.message(AddAdmin.user_id)
async def add_admin(call: Message, state: FSMContext):
    user = await User.get(int(call.text))
    print(user)
    if user:
        text = html.bold(f'''
#Admin qo'shildi
chat_id: <code>{user.id}</code>
Username: <code>@{user.username}</code>
            ''')
        await User.update(id_=user.id, admin=True)
        await call.answer(text, parse_mode='HTML')
        await call.answer(html.bold("Adminlar ro'yxati"), parse_mode='HTML', reply_markup=await admins())
    else:
        await call.answer(html.bold("Bunaqa id li user yo'q, bo'tga /start bergan bo'lish kerak"), parse_mode='HTML')


@admin_router.callback_query(F.data.startswith('send_'))
async def leagues_handler(call: CallbackQuery, state: FSMContext):
    data = call.data.split('_')[-1]
    await call.answer()
    await state.set_state(SendTextState.text)
    if data == 'text':
        await call.message.answer('Text xabarni kiriting')
    if data == 'video':
        await call.message.answer("Rasm yoki videoni kiriting")


@admin_router.message(SendTextState.text)
async def leagues_handler(msg: Message, state: FSMContext):
    if msg.photo:
        await state.set_state(SendTextState.video)
        await state.update_data(photo=msg.photo[-1].file_id)
        await msg.answer('Text xabarni kiriting')
    elif msg.video:
        await state.set_state(SendTextState.video)
        await state.update_data(video=msg.video.file_id)
        await msg.answer('Text xabarni kiriting')
    elif msg.text:
        await state.set_state(SendTextState.link)
        await state.update_data(text=msg.text)
        await msg.answer("Link jo'nating")


@admin_router.message(SendTextState.video)
async def leagues_handler(msg: Message, state: FSMContext):
    await state.update_data(text=msg.text)
    await state.set_state(SendTextState.link)
    await msg.answer("Link jo'nating")


@admin_router.message(SendTextState.link)
async def leagues_handler(msg: Message, state: FSMContext):
    await state.update_data(link=msg.text)
    data = await state.get_data()
    if len(data) == 2:
        await msg.answer(data['text'] + f'\n\n{data["link"]}', reply_markup=confirm_inl())
    else:
        if data.get('photo'):
            await msg.answer_photo(data['photo'], data['text'] + f'\n\n{data["link"]}', parse_mode='HTML',
                                   reply_markup=confirm_inl())
        else:
            await msg.answer_video(video=data['video'], caption=data['text'] + f'\n\n{data["link"]}', parse_mode='HTML',
                                   reply_markup=confirm_inl())


@admin_router.callback_query(F.data.endswith("_network"))
async def leagues_handler(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = call.data.split('_')
    res = await state.get_data()
    print(res)
    await call.answer()
    users: list[User] = await User.get_all()
    if data[0] == 'confirm':
        send = 0
        block = 0
        if len(res) == 2:
            for i in users:
                try:
                    await bot.send_message(i.id, res['text'], parse_mode='HTML', reply_markup=link(res['link']))
                    send += 1
                except:
                    block += 1
        else:
            if res.get('photo'):
                for i in users:
                    try:
                        await bot.send_photo(chat_id=i.id, photo=res['photo'], caption=res['text'], parse_mode='HTML',
                                             reply_markup=link(res['link']))
                        send += 1
                    except:
                        block += 1
            elif res.get('video'):
                for i in users:
                    try:
                        await bot.send_video(chat_id=i.id, video=res['video'], caption=res['text'], parse_mode='HTML',
                                             reply_markup=link(res['link']))
                        send += 1
                    except:
                        block += 1
        await call.message.answer(f'Yuborildi: {send}\nBlockda: {block}')

    elif data[0] == 'cancel':
        await call.message.delete()
        await call.message.answer("Protsess to'xtatildi")
    await state.clear()
