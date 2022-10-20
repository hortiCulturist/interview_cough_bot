import os
from sqlite3 import IntegrityError

import aiogram
from aiogram import Bot
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils import executor

import button
import config
import db

storage = MemoryStorage()
bot = Bot(token=config.TOKEN)
dp = Dispatcher(bot, storage=storage)


async def on_startup(_):
    print('Bot activated')
    db.start_db()


class quest(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()
    q6 = State()
    q7 = State()
    q8 = State()
    q9 = State()
    q10 = State()


class MassSend(StatesGroup):
    sendd = State()


@dp.message_handler(commands='start')
async def strt(message: types.Message):
    try:
        db.db_add(message.from_user.id, message.from_user.first_name, message.from_user.username)
    except IntegrityError:
        pass
    await bot.send_message(message.from_user.id, text="Ласкаво просимо!\n"
                                                      "Цей бот допоможе вам зрозуміти наскільки ви обізнані "
                                                      "у темі кашлю та його лікуванні, пройдіть опитування та "
                                                      "дізнаєтеся свій рівень знань у цій темі\n",
                           reply_markup=button.interview())

@dp.message_handler(commands="users")
async def usrs(message: types.Message):
    await bot.send_message(message.from_user.id, text=f"Пользователей в базе данных: {len(db.all_user())}")

@dp.message_handler(commands='send', state=None)
async def snd(message: types.Message):


    if message.from_user.id not in config.ADMIN_ID:
        await bot.send_message(message.from_user.id, text="В ДОСТУПІ ВІДМОВЛЕНО!")
    else:
        await bot.send_message(message.from_user.id, text=f"Напишите и отправьте сообщение для "
                                                          f"рассылки оно будет отправлено {len(db.all_user())} "
                                                          f"пользователям", reply_markup=button.cancel())
        await MassSend.sendd.set()

@dp.message_handler(text='ОТМЕНА',state=MassSend.sendd)
async def cncl(message: types.Message, state: FSMContext):
    await state.finish()
    await bot.send_message(message.from_user.id, 'Рассылка отменена', reply_markup=ReplyKeyboardRemove())

@dp.message_handler(content_types=aiogram.types.ContentType.ANY,
                    state=MassSend.sendd)
async def send(message: types.Message, state: FSMContext):
    good, bad = 0, 0
    await state.finish()
    errors_list = []
    for i in db.all_user():
        try:
            await bot.send_message(i[0], message.text)
            good += 1
        except Exception as e:
            bad += 1
            errors_list.append(e)
    await bot.send_message(message.from_user.id, 'Рассылка завершена успешно\n'
                                                 f'Доставлено: {good}\n'
                                                 f'Не доставлено: {bad}\n'
                                                 f'Ошибки {set(errors_list)}')


# ******************************************************************************************************************
# 1 ВОПРОС

@dp.callback_query_handler(text='start_again', state=None)
@dp.message_handler(text_startswith='Почати опитування', state=None)
async def question_1(message: types.Message):
    #    await db.start_num_db()
    #    await db.add_pnt(message.from_user.id)
    await quest.q1.set()
    await bot.send_message(message.from_user.id, 'Дайте відповідь на 10 питань та дізнайтеся наскільки ви '
                                                 'обізнані у темі кашлю та його лікуванні 🤔',
                           reply_markup=ReplyKeyboardRemove())
    await bot.send_message(message.from_user.id, text="1 запитання з 10\n\n"
                                                      "Продуктивний кашель не потребує лікування",
                           reply_markup=button.yes_no())


@dp.callback_query_handler(text='yes_yes', state=quest.q1)
async def question_1(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Ще й як потребує!\n'
                                                   f'Важливо максимально повно елімінувати мокротиння з нижніх '
                                                   f'дихальних шляхів. Найчастіше з цією метою використовують '
                                                   f'лікарські засоби.',
                           reply_markup=button.next())


@dp.callback_query_handler(text='nope', state=quest.q1)
async def question_1(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['points'] = data.get('points', 0) + 1
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Абсолютно вірно!\n'
                                                   f'Мокротиння слід максимально повно елімінувати з '
                                                   f'дихальних шляхів і тут доцільно використовувати '
                                                   f'муколітики. І не забуваємо зволожувати повітря у '
                                                   f'приміщенні!',
                           reply_markup=button.next())
    await call.answer()


# 1 ВОПРОС
# ******************************************************************************************************************
# 2 ВОПРОС


@dp.callback_query_handler(text='nxt', state=quest.q1)
async def question_2(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text=f"2 запитання з 10\n\n"
                                                   f"Муколітична та відхаркувальна дія – це одне й те саме",
                           reply_markup=button.yes_no())
    await quest.next()


@dp.callback_query_handler(text='yes_yes', state=quest.q2)
async def question_2(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Зовсім не так!\n'
                                                   f'Муколітики (такі як амброксол та ацетилцистеїн) '
                                                   f'розріджують мокротиння, але на відміну від відхаркувальних '
                                                   f'засобів не збільшують його об’єм.',
                           reply_markup=button.next())


@dp.callback_query_handler(text='nope', state=quest.q2)
async def question_2(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['points'] = data.get('points', 0) + 1
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Дійсно!\n'
                                                   f'Справжні муколітики (амброксол, ацетилцистеїн) '
                                                   f'розріджують мокротиння, a відхаркувальні засоби '
                                                   f'зменшують в’язкість слизу за рахунок збільшення її об’єму.',
                           reply_markup=button.next())


# 2 ВОПРОС
# ******************************************************************************************************************
# 3 ВОПРОС


@dp.callback_query_handler(text='nxt', state=quest.q2)
async def question_3(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text="3 запитання з 10\n\n"
                                                   "Фармакологічні ефекти амброксолу не обмежуються муколітичною дією.",
                           reply_markup=button.yes_no())
    await quest.next()


@dp.callback_query_handler(text='yes_yes', state=quest.q3)
async def question_3(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['points'] = data.get('points', 0) + 1
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Це правда!\n'
                                                   f'Додатково має місцеву знеболювальну, '
                                                   f'протизапальну та імуномодулюючу дію. '
                                                   f'Є навіть амброксол у формі орального спрею, '
                                                   f'який впродовж 3 діб долає симптоми фарингіту '
                                                   f'у дорослих – «Респикс Спрей».',
                           reply_markup=button.next())


@dp.callback_query_handler(text='nope', state=quest.q3)
async def question_3(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Дуже навіть не обмежується!\n'
                                                   f'Його фармакодинаміка обширна: '
                                                   f'окрім впливу на мокротиння йому притаманні '
                                                   f'ще місцевоанестезувальна, протизапальна та '
                                                   f'імунотропна дія. ',
                           reply_markup=button.next())


# 3 ВОПРОС
# ******************************************************************************************************************
# 4 ВОПРОС


@dp.callback_query_handler(text='nxt', state=quest.q3)
async def question_4(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text="4 запитання з 10\n\n"
                                                   "Симптоми гострого фарингіту минають "
                                                   "приблизно за тиждень лікування. ",
                           reply_markup=button.yes_no())
    await quest.next()


@dp.callback_query_handler(text='yes_yes', state=quest.q4)
async def question_4(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Уявіть собі, але ні!\n'
                                                   f'Достатньо всього 3 днів використання «Респикс Спрею», '
                                                   f'щоб повністю позбавитись симптомів гострого фарингіту!',
                           reply_markup=button.next())


@dp.callback_query_handler(text='nope', state=quest.q4)
async def question_4(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['points'] = data.get('points', 0) + 1
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Дійсно!\n'
                                                   f'«Респикс Спрей» ефективно усуває симптоми гострого '
                                                   f'неускладненого фарингіту менше ніж за 3 дні – доведено '
                                                   f'науковими дослідженнями!',
                           reply_markup=button.next())


# 4 ВОПРОС
# ******************************************************************************************************************
# 5 ВОПРОС


@dp.callback_query_handler(text='nxt', state=quest.q4)
async def question_5(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text="5 запитання з 10\n\n"
                                                   "Амброксол та гліцирризин здатні забезпечити "
                                                   "захист клітин дихальних шляхів від інфікування SARS-nCoV-2",
                           reply_markup=button.yes_no())
    await quest.next()


@dp.callback_query_handler(text='yes_yes', state=quest.q5)
async def question_5(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['points'] = data.get('points', 0) + 1
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Правда!\n'
                                                   f'Ці компоненти здатні перешкоджати проникненню SARS-nCoV-2 '
                                                   f'до клітин респіраторного тракту. '
                                                   f'Важливо при цьому, що «Респикс Спрей» '
                                                   f'створює високі концентрації цих речовин '
                                                   f'на слизовій оболонці горла – «вхідних воротах» '
                                                   f'для коронавірусу.',
                           reply_markup=button.next())


@dp.callback_query_handler(text='nope', state=quest.q5)
async def question_5(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Дуже навіть здатний!\n'
                                                   f'Амброксол сам по собі здатний запобігати проникненню '
                                                   f'вірусу до клітин дихального тракту людини. '
                                                   f'Крім того, такий саме ефект встановлено і для '
                                                   f'гліциризину – одного зі складових «Респикс Спрею».',
                           reply_markup=button.next())


# 5 ВОПРОС
# ******************************************************************************************************************
# 6 ВОПРОС


@dp.callback_query_handler(text='nxt', state=quest.q5)
async def question_6(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text="6 запитання з 10\n\n"
                                                   "Якщо амброксол і ацетилцистеїн мають муколітичний ефект, "
                                                   "то їх спільне використання недоцільно",
                           reply_markup=button.yes_no())
    await quest.next()


@dp.callback_query_handler(text='yes_yes', state=quest.q6)
async def question_6(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Це не так.\n'
                                                   f'Їх спільне використання цілком виправдано, '
                                                   f'адже  ацетилцистеїн протягом 30 хв розріджує мокротиння, '
                                                   f'а амброксол забезпечує тривале його виведення. '
                                                   f'Ось навіть така комбінація є – таблетки «Респикс».',
                           reply_markup=button.next())


@dp.callback_query_handler(text='nope', state=quest.q6)
async def question_6(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['points'] = data.get('points', 0) + 1
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Точно!\n'
                                                   f'Ацетилцистеїн швидко зменшує в’язкість мокротиння, '
                                                   f'а амброксол стимулює його виведення. '
                                                   f'Тому таблетки «Респикс» значно зменшує скарги на '
                                                   f'кашель та мокротиння.',
                           reply_markup=button.next())


# 6 ВОПРОС
# ******************************************************************************************************************
# 7 ВОПРОС


@dp.callback_query_handler(text='nxt', state=quest.q6)
async def question_7(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text="7 запитання з 10\n\n"
                                                   "Амброксол доцільно рекомендувати разом з антибіотиками",
                           reply_markup=button.yes_no())
    await quest.next()


@dp.callback_query_handler(text='yes_yes', state=quest.q7)
async def question_7(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['points'] = data.get('points', 0) + 1
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Це правда!\n'
                                                   f'Амброксол збільшує ефективність антибіотика шляхом '
                                                   f'збільшення його концентрації в легенях та мокротинні. '
                                                   f'Разом з лоратадином амброксол входить до складу '
                                                   f'таблеток «Респикс Л» - ідеального доповнення до '
                                                   f'антибіотикотерапії – підвищує її ефективність і '
                                                   f'прикриває можливу алергію на антибіотик.',
                           reply_markup=button.next())


@dp.callback_query_handler(text='nope', state=quest.q7)
async def question_7(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Насправді доцільно!\n'
                                                   f'Комбінація амброксолу та лоратадину, '
                                                   f'що входить до складу препарату «Респикс Л», '
                                                   f'є особливо ефективною у збільшенні ефективності '
                                                   f'антибіотикотерапії хвороб органів дихання та '
                                                   f'запобіганні можливої алергії на антибіотик.',
                           reply_markup=button.next())


# 7 ВОПРОС
# ******************************************************************************************************************
# 8 ВОПРОС


@dp.callback_query_handler(text='nxt', state=quest.q7)
async def question_8(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text="8 запитання з 10\n\n"
                                                   "Муколітик чи антигістамінний препарат можна застосовувати "
                                                   "не більше 14 днів.",
                           reply_markup=button.yes_no())
    await quest.next()


@dp.callback_query_handler(text='yes_yes', state=quest.q8)
async def question_8(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Не так.\n'
                                                   f'Наприклад амброксол і лоратадин є не лише ефективними, '
                                                   f'але й безпечними препаратами, у тому числі при тривалому '
                                                   f'застосуванні. Той же «Респикс Л» не має обмежень щодо '
                                                   f'тривалості використання – все лімітується лише '
                                                   f'симптомами захворювання.',
                           reply_markup=button.next())


@dp.callback_query_handler(text='nope', state=quest.q8)
async def question_8(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['points'] = data.get('points', 0) + 1
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Правильно!\n'
                                                   f'Адже «Респикс Л» можна використовувати без обмежень '
                                                   f'у тривалості, адже і амброксол, і лоратадин доведено '
                                                   f'безпечні при тривалому застосуванні.',
                           reply_markup=button.next())


# 8 ВОПРОС
# ******************************************************************************************************************
# 9 ВОПРОС


@dp.callback_query_handler(text='nxt', state=quest.q8)
async def question_9(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text="9 запитання з 10\n\n"
                                                   "Назальні деконгестанти відновлюють носове дихання та допомагають "
                                                   "позбавитись від слизу",
                           reply_markup=button.yes_no())
    await quest.next()


@dp.callback_query_handler(text='yes_yes', state=quest.q9)
async def question_9(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Насправді не завжди.\n'
                                                   f'Наприклад, при риносинуситі густий, інфікований слиз '
                                                   f'накопичується також в синусах, а ці засоби не '
                                                   f'полегшують його виведення. Для санації синусів '
                                                   f'сучасні гайдлайни рекомендують застосовувати '
                                                   f'фітоекстракти - такі, які входять до складу «Респикс Синус».',
                           reply_markup=button.next())


@dp.callback_query_handler(text='nope', state=quest.q9)
async def question_9(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['points'] = data.get('points', 0) + 1
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Це правда!\n'
                                                   f'Адже накопичення слизу відбувається і в порожнині носа, '
                                                   f'і в синусах, а деконгестанти мало впливають на '
                                                   f'його виведення. В таких випадках допомагають '
                                                   f'фітоекстракти. Саме такі, які містяться в '
                                                   f'«Респикс Синус». ',
                           reply_markup=button.next())


# 9 ВОПРОС
# ******************************************************************************************************************
# 10 ВОПРОС


@dp.callback_query_handler(text='nxt', state=quest.q9)
async def question_10(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text="10 запитання з 10\n\n"
                                                   "Фітопрепарати не мають доказової ефективності при риносинуситах",
                           reply_markup=button.yes_no())
    await quest.next()


@dp.callback_query_handler(text='yes_yes', state=quest.q10)
async def question_10(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Ще й як мають!\n'
                                                   f'Відповідно EPOS 2020 пеларгонія, '
                                                   f'що входить до складу «Респикс Синус», '
                                                   f'має високий рівень доказовості – 1b. ',
                           reply_markup=button.end())


@dp.callback_query_handler(text='nope', state=quest.q10)
async def question_10(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['points'] = data.get('points', 0) + 1
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Абсолютно правильно!\n'
                                                   f'EPOS 2020 рекомендує використовувати ту ж '
                                                   f'таки пеларгонію, що входить до складу «Респикс Синус», '
                                                   f'при поствірусному риносинуситі (рівень доказовості 1b).',
                           reply_markup=button.end())


# 10 ВОПРОС
# ******************************************************************************************************************
# КОНЕЦ. ИТОГИ


@dp.callback_query_handler(text='endd', state=quest.q10)
async def back_end(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    async with state.proxy() as data:
        counter = data.get('points')
    db.update_point(call.from_user.id, counter)
    if counter == 0 or counter <= 4:
        await bot.send_photo(call.from_user.id,
                             photo=open(os.path.join(config.path_photo, 'COVER_PULMO_1.png'), 'rb'),
                             caption=f"{config.minimum}\n\n"
                                     f"Ваші бали: {counter}\n",
                             reply_markup=button.axxe(counter, config.minimum))
    elif counter >= 5 and counter <= 7:
        await bot.send_photo(call.from_user.id,
                             photo=open(os.path.join(config.path_photo, 'COVER_PULMO_2.png'), 'rb'),
                             caption=f"{config.medium}\n\n"
                                     f"Ваші бали: {counter}\n",
                             reply_markup=button.axxe(counter, config.medium))
    else:
        await bot.send_photo(call.from_user.id,
                             photo=open(os.path.join(config.path_photo, 'COVER_PULMO_3.png'), 'rb'),
                             caption=f"{config.maximum}\n\n"
                                     f"Ваші бали: {counter}\n",
                             reply_markup=button.axxe(counter, config.maximum))
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
