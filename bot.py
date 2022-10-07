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
                                                   f'Мокротиння слід максимально повно елімінувати з найдрібніших '
                                                   f'бронхіол та альвеол. З цією метою використовують спеціальні '
                                                   f'лікарські засоби, рідше – дихальну фізіотерапію '
                                                   f'(постуральний дренаж, техніки ефективного кашлю тощо). '
                                                   f'І не забуваємо зволожувати повітря у приміщенні!',
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
                                                   f'Муколітики (такі як амброксол та ацетилцистеїн)'
                                                   f' розріджують мокротиння, але на відміну від відхаркувальних '
                                                   f'засобів не збільшують його об’єм. Дія відхаркувальних засобів '
                                                   f'(зазвичай це препарати рослинного походження – трава термопсису,'
                                                   f' наприклад) заснована на збільшення секреції залоз '
                                                   f'(у т.ч. бронхіальних, залоз ШКТ, ЛОР-органів тощо). '
                                                   f'Тому їх не варто застосовувати при продуктивному кашлю, нежиті, '
                                                   f'захворюваннях ШКТ, гормональних порушеннях тощо. Крім того, '
                                                   f'у високій дозі ці препарати викликають блювоту.',
                           reply_markup=button.next())


@dp.callback_query_handler(text='nope', state=quest.q2)
async def question_2(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['points'] = data.get('points', 0) + 1
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Дійсно!\nМуколітики та відхаркувальні засоби (експекторанти) – це '
                                                   f'різні лікарські засоби. Справжні муколітики '
                                                   f'(амброксол, ацетилцистеїн) розріджують мокротиння, '
                                                   f'полегшуючи тим самим його відходження. '
                                                   f'Відхаркувальні ж засоби викликають збільшення об’єму слизу, '
                                                   f'при цьому зменшується в’язкість мокротиння, '
                                                   f'що стимулює кашльовий рефлекс.',
                           reply_markup=button.next())


# 2 ВОПРОС
# ******************************************************************************************************************
# 3 ВОПРОС


@dp.callback_query_handler(text='nxt', state=quest.q2)
async def question_3(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text="3 запитання з 10\n\n"
                                                   "Фармакологічні ефекти амброксолу не обмежуються виключно "
                                                   "його впливом на в’язкість мокротиння (муколітичною дією)",
                           reply_markup=button.yes_no())
    await quest.next()


@dp.callback_query_handler(text='yes_yes', state=quest.q3)
async def question_3(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['points'] = data.get('points', 0) + 1
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Це правда!\n'
                                                   f'Амброксол не лише розріджує мокротиння, '
                                                   f'виявляючи тим самим муколітичну дію, '
                                                   f'але й стимулює її виведення, '
                                                   f'відновлює санацію дихальних шляхів від інфікованного слизу, '
                                                   f'чинить протизапальну, імуномодулюючу та антиоксидантну дію. '
                                                   f'Особливо цікавою є виразна місцева знеболювальна дія амброксолу! '
                                                   f'Є навіть інноваційна форма з високим вмістом амброксолу, '
                                                   f'що ефективно усуває біль у горлі – «Респикс Спрей».',
                           reply_markup=button.next())


@dp.callback_query_handler(text='nope', state=quest.q3)
async def question_3(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Дуже навіть не обмежується!\n'
                                                   f'Фармакодинаміка амброксолу насправді досить обширна: '
                                                   f'окрім муколітичної дії йому притаманні ще властивості мукокінетика,'
                                                   f' протизапальні імунотропні, антиоксидантні властивості, '
                                                   f'а також – уявіть собі – місцевоанестезувальна дія! '
                                                   f'Саме ця дія найбільш виразно проявляється у «Респикс Спрею» – '
                                                   f'інноваційній лікарський формі амброксолу для місцевого лікування '
                                                   f'виразного болю в горлі. ',
                           reply_markup=button.next())


# 3 ВОПРОС
# ******************************************************************************************************************
# 4 ВОПРОС


@dp.callback_query_handler(text='nxt', state=quest.q3)
async def question_4(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text="4 запитання з 10\n\n"
                                                   "Амброксол не ефективніший за відомі місцеві анестетики,"
                                                   " зокрема, лідокаїн",
                           reply_markup=button.yes_no())
    await quest.next()


@dp.callback_query_handler(text='yes_yes', state=quest.q4)
async def question_4(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Уявіть собі, але ні!\n'
                                                   f'Лідокаїн у 39 разів поступається амброксолу у виразності '
                                                   f'знеболювальної дії – доведено науковими дослідженнями.',
                           reply_markup=button.next())


@dp.callback_query_handler(text='nope', state=quest.q4)
async def question_4(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['points'] = data.get('points', 0) + 1
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Дійсно!\n'
                                                   f'Дослідження підтверджують, що амброксол значно ефективніший '
                                                   f'місцевий анестетик, аніж лідокаїн. Крім того, '
                                                   f'місцева знеболювальна дія амброксолу, '
                                                   f'на відміну від лідокаїну чи бензокаїну, '
                                                   f'не супроводжується відчуттям оніміння та порушенням смаку – '
                                                   f'а все через вибірковий вплив на безмієлінові нервові волокна, '
                                                   f'що проводять больові імпульси!',
                           reply_markup=button.next())


# 4 ВОПРОС
# ******************************************************************************************************************
# 5 ВОПРОС


@dp.callback_query_handler(text='nxt', state=quest.q4)
async def question_5(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text="5 запитання з 10\n\n"
                                                   "Препарати амброксолу ефективні у запобіганні інфікуванню "
                                                   "SARS-nCoV-2",
                           reply_markup=button.yes_no())
    await quest.next()


@dp.callback_query_handler(text='yes_yes', state=quest.q5)
async def question_5(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['points'] = data.get('points', 0) + 1
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Правда!\n'
                                                   f'Амброксол доведено інгібує взаємодію між спайковим білком вірусу '
                                                   f'та зв’язувальним доменом рецептора АПФ-2, тим самим перешкоджаючи '
                                                   f'проникненню збудника до клітин респіраторного тракту людини. '
                                                   f'Аналогічний ефект, до речі, притаманний гліциризину, амонієва '
                                                   f'сіль якого разом із власне самим амброксолом входить до складу '
                                                   f'«Респикс Спрею».',
                           reply_markup=button.next())


@dp.callback_query_handler(text='nope', state=quest.q5)
async def question_5(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Дуже навіть здатні!\n'
                                                   f'Амброксол сам по собі здатний запобігати проникненню вірусу до '
                                                   f'клітин дихального тракту людини. Крім того, такий саме ефект '
                                                   f'встановлено і для гліциризину – допоміжного компоненту '
                                                   f'«Респикс Спрею».',
                           reply_markup=button.next())


# 5 ВОПРОС
# ******************************************************************************************************************
# 6 ВОПРОС


@dp.callback_query_handler(text='nxt', state=quest.q5)
async def question_6(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text="6 запитання з 10\n\n"
                                                   "Якщо амброксол і ацетилцистеїн мають муколітичний ефект, "
                                                   "використовувати їх одночасно недоцільно ",
                           reply_markup=button.yes_no())
    await quest.next()


@dp.callback_query_handler(text='yes_yes', state=quest.q6)
async def question_6(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Це не так.\n'
                                                   f'Амброксол і ацетилцистеїн мають різну фармакодинаміку на слиз: '
                                                   f'ацетилцистеїн (як прямий муколітик) швидко розріджує мокротиння, '
                                                   f'а амброксол (як мукокінетік) забезпечує його виведення '
                                                   f'впродовж півдоби. Тому їх спільне використання є цілком '
                                                   f'виправданим. Ось навіть лікарський засіб з такою комбінацією є – '
                                                   f'таблетки «Респикс».',
                           reply_markup=button.next())


@dp.callback_query_handler(text='nope', state=quest.q6)
async def question_6(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['points'] = data.get('points', 0) + 1
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Точно!\n'
                                                   f'Так, комбіноване застосування амброксолу і ацетилцистеїну є '
                                                   f'доцільним, адже ці муколітики впливають на різні компоненти '
                                                   f'мокротиння: ацетилцистеїн як прямий муколітик швидко зменшує '
                                                   f'в’язкість мокротиння (шляхом порушення структури дисульфідних '
                                                   f'зв’язків слизу), але залишає цю розріджену слиз в дихальних '
                                                   f'шляхах. Натомість амброксол стимулює рухливість війок '
                                                   f'миготливого епітелію, прискорюючи санацію дихальних шляхів '
                                                   f'від слизу. Саме така комбінація входить до складу таблеток '
                                                   f'«Респикс». Їх використання значно посилює ефективність '
                                                   f'лікування продуктивного кашлю.',
                           reply_markup=button.next())


# 6 ВОПРОС
# ******************************************************************************************************************
# 7 ВОПРОС


@dp.callback_query_handler(text='nxt', state=quest.q6)
async def question_7(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text="7 запитання з 10\n\n"
                                                   "Муколітики доцільно комбінувати з антигістамінними препаратами",
                           reply_markup=button.yes_no())
    await quest.next()


@dp.callback_query_handler(text='yes_yes', state=quest.q7)
async def question_7(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['points'] = data.get('points', 0) + 1
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Це правда!\n'
                                                   f'Такі комбінації є добре відомими – зокрема, '
                                                   f'амброксол разом з лоратадином входить до складу препарату '
                                                   f'«Респикс Л», що ефективно полегшує кашель, '
                                                   f'який супроводжується алергічним компонентом '
                                                   f'(його маркери – це закладеність носа, '
                                                   f'ринорея або бронхоспазмом – жорстке дихання при аускультації).',
                           reply_markup=button.next())


@dp.callback_query_handler(text='nope', state=quest.q7)
async def question_7(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Насправді доцільно!\n'
                                                   f'Комбінація муколітика амброксолу та блокатора Н1-гістамінових '
                                                   f'рецепторів лоратадину, що входить до складу препарату «Респикс Л», '
                                                   f'є ефективною у симптоматичному лікуванні захворювань дихальних '
                                                   f'шляхів з алергічним компонентом, що пов’язані з порушенням '
                                                   f'бронхіальної секреції та ослабленням просування слизу.',
                           reply_markup=button.next())


# 7 ВОПРОС
# ******************************************************************************************************************
# 8 ВОПРОС


@dp.callback_query_handler(text='nxt', state=quest.q7)
async def question_8(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text="8 запитання з 10\n\n"
                                                   "Курс лікування комбінованим препаратом амброксолу з лоратадином "
                                                   "повинен складати не більше 14 днів",
                           reply_markup=button.yes_no())
    await quest.next()


@dp.callback_query_handler(text='yes_yes', state=quest.q8)
async def question_8(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Не так.\n'
                                                   f'Як амброксол, так і лоратадин є не лише ефективними, '
                                                   f'але й безпечними препаратами, у тому числі при тривалому '
                                                   f'застосуванні. Той же «Респикс Л» не має обмежень щодо '
                                                   f'тривалості використання – все лімітується лише симптомами '
                                                   f'захворювання.',
                           reply_markup=button.next())


@dp.callback_query_handler(text='nope', state=quest.q8)
async def question_8(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['points'] = data.get('points', 0) + 1
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Правильно!\n'
                                                   f'«Респикс Л» можна використовувати без обмежень у тривалості, '
                                                   f'адже і амброксол, і лоратадин доведено безпечні при тривалому '
                                                   f'застосуванні.',
                           reply_markup=button.next())


# 8 ВОПРОС
# ******************************************************************************************************************
# 9 ВОПРОС


@dp.callback_query_handler(text='nxt', state=quest.q8)
async def question_9(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text="9 запитання з 10\n\n"
                                                   "Кашель може супроводжувати риносинусити",
                           reply_markup=button.yes_no())
    await quest.next()


@dp.callback_query_handler(text='yes_yes', state=quest.q9)
async def question_9(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['points'] = data.get('points', 0) + 1
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Це правда!\n'
                                                   f'А всьому виною синдром постназального затікання. '
                                                   f'Тому дуже важливо підходити до проблеми кашлю вдумливо '
                                                   f'та комплексно – обов’язково встановити його причину та обрати '
                                                   f'оптимальний варіант лікування. Для такого пацієнта найкращою '
                                                   f'рекомендацією буде використання «Респикс» таблеток разом з '
                                                   f'комплексом фітоекстрактів «Респикс Синус».',
                           reply_markup=button.next())


@dp.callback_query_handler(text='nope', state=quest.q9)
async def question_9(call: types.CallbackQuery):
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Насправді може!\n'
                                                   f'Найчастішою причиною кашлю у пацієнтів з гострим чи хронічним '
                                                   f'риносинуситом є спливання виділень по задній стінці глотки. '
                                                   f'У такому випадку разом з препаратами муколітиків '
                                                   f'(«Респикс» таблетки, «Респикс Л») доцільно порекомендувати '
                                                   f'комплекс рослинних екстрактів «Респикс Синус» у вигляді порошку '
                                                   f'для приготування зігріваючого напою.',
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
                                                   f'Відповідно до нового європейського узгоджувального документу '
                                                   f'з лікування риносинуситу і поліпозу носа EPOS 2020 фітотерапія '
                                                   f'має високий рівень доказовості – 1b. '
                                                   f'До рослин із доведеною ефективністю відносять, зокрема, і '
                                                   f'пеларгонію, що входить до складу «Респикс Синус».',
                           reply_markup=button.end())


@dp.callback_query_handler(text='nope', state=quest.q10)
async def question_10(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['points'] = data.get('points', 0) + 1
    await call.answer()
    await bot.send_message(call.from_user.id, text=f'Абсолютно правильно!\n'
                                                   f'Окремі фітопрепарати мають доведену ефективність із рівнем '
                                                   f'доказовості 1b – значний вплив на зменшення тривалості '
                                                   f'захворювання та його симптомів при відсутності серйозних '
                                                   f'побічних ефектів. EPOS 2020 рекомендує використовувати ту ж '
                                                   f'таки пеларгонію, що входить до складу «Респикс Синус», при '
                                                   f'гострому поствірусному риносинуситі.',
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
