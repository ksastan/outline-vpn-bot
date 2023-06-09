from outline_vpn.outline_vpn import OutlineVPN
from functools import wraps
from aiogram import Bot, Dispatcher, executor, types
import logging
import logs.log_config
from config import API_TOKEN, OUTLINE_API_URL, LOGGING_LEVEL, AUTHORIZED_IDS

# Setup the access with the API URL (Use the one provided to you after the server setup)
client = OutlineVPN(api_url=OUTLINE_API_URL)
# logs init
logs.log_config.log_setup(LOGGING_LEVEL)


def show_keys():
    keys_list = ""
    for key in client.get_keys():
        keys_list += f"{key.key_id} {key.name if key.name else 'Noname'} " \
                     f"{int(key.used_bytes / (1024 ** 2)) if key.used_bytes else 0}MB\n"
    logging.info('show vpn keys successfully')
    return keys_list


def get_keys():
    keys_list = {}
    for key in client.get_keys():
        keys_list[key.key_id] = {'name': key.name,
                                 'access_url': key.access_url,
                                 'used_bytes': key.used_bytes,
                                 'data_limit': key.data_limit}
    logging.info('get vpn keys successfully')
    return keys_list


def create_key(name, traffic_limit):
    """
    :param traffic_limit: limit in Gb
    :param name: key name
    :return: connection URL string
    """
    try:
        new_key = client.create_key()
        client.rename_key(new_key.key_id, name)
        client.add_data_limit(new_key.key_id, traffic_limit)
        logging.info(f"create new key {name} successfully")
        return new_key.access_url
    except Exception as e:
        logging.exception(f"create_key {name} error {e}")


def permission_check(func):
    """
    Decorator to check telegram user permissions
    """

    @wraps(func)
    async def wrapped(message: types.Message):
        # permission check code goes here
        user_id = message.from_user.id
        # For example, we only allow users with user_id 123 and 456 to run the command
        if str(user_id) not in AUTHORIZED_IDS:
            logging.error(f"user id {user_id} don't have permissions - {func.__name__}")
            await message.answer(f"You do not have permission to run this command.\nYour user_id={user_id}")
            return
        # if permission check pass, run the original function
        await func(message)

    return wrapped


# telegram bot section
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)  # look for updates


@dp.message_handler(commands=['start', 'help'])
@permission_check
async def send_welcome(message: types.Message):
    await message.reply("*Create new VPN key:* /newkey <keyname> <limit in GB>\n"
                        "*List existed keys:* /showkeys\n"
                        "*Delete key:* /delkey <keyid>\n"
                        "*Get key access url:* /getkey <keyid>\n"
                        "*Change data limit:* /changelimit <keyid> <limit in GB>", parse_mode="Markdown")


@dp.message_handler(commands=['newkey'])
@permission_check
async def newkey(message: types.Message):
    name_exists = False
    try:
        command = message.text.split()
        key_name = command[1]
        traffic_limit = 1000 ** 3 * int(command[2]) if len(command) == 3 else 1000 ** 3 * 50  # default 50Gb
        keys = get_keys()
        for key in keys.values():
            if key['name'] == key_name:
                name_exists = True
        if not name_exists:
            key_access_url = create_key(name=key_name, traffic_limit=traffic_limit)
            await message.answer(f"Access URL for new key:\n`{key_access_url}`", parse_mode="Markdown")
        else:
            logging.error(f"key {key_name} already exists")
            await message.answer(f"Key with name {key_name} already exists")
    except IndexError:
        logging.error("no specified key name - newkey")
        await message.answer(f"There is no key name. Specify key name: `/newkey <keyname> <limitGB>`",
                             parse_mode="Markdown")


@dp.message_handler(commands=['showkeys'])
@permission_check
async def showkeys(message: types.Message):
    await message.answer(f"*ID Name  Traffic*:\n{show_keys()}", parse_mode="Markdown")


@dp.message_handler(commands=['delkey'])
@permission_check
async def delkey(message: types.Message):
    try:
        vpn_keys = get_keys()
        key_id = message.text.split()[1]
        logging.debug(f"key_id={key_id} keys={vpn_keys.keys()} - delkey")
        if key_id in vpn_keys.keys():
            client.delete_key(int(key_id))
            logging.info(f"delete key id={key_id} successfully")
            await message.answer(f"Key with id {key_id} was deleted")
        else:
            logging.info(f"key with id {key_id} not existed")
            await message.answer(f"Key with id {key_id} not existed")
    except IndexError:
        logging.error("no specified key id - delkey")
        await message.answer("There is no key id. Specify key name: `/delkey <id>`", parse_mode="Markdown")


@dp.message_handler(commands=['getkey'])
@permission_check
async def getkey(message: types.Message):
    try:
        keys = get_keys()
        key_id = message.text.split()[1]
        logging.debug(f"key_id={key_id} keys={keys.keys()} - getkey")
        if key_id in keys.keys():
            logging.info(f"Get access_url for key id={key_id} successfully")
            await message.answer(f"Access url for key with id {key_id}:\n`{keys[key_id]['access_url']}`",
                                 parse_mode="Markdown")
        else:
            logging.info(f"key with id {key_id} not existed")
            await message.answer(f"Key with id {key_id} not existed")
    except IndexError:
        logging.error(f"no specified key id - getkey")
        await message.answer("There is no key id. Specify key name: `/getkey <id>`", parse_mode="Markdown")


@dp.message_handler(commands=['changelimit'])
@permission_check
async def change_data_limit(message: types.Message):
    try:
        keys = get_keys()
        command = message.text.split()
        key_id = command[1]
        data_limit = 1000 ** 3 * int(command[2]) if len(command) == 3 else \
            await message.answer(f"Please specify data limit in Gb:\n"
                                 f"`/changelimit <keyid> "
                                 f"<data_limit>`",
                                 parse_mode="Markdown")
        logging.debug(f"key_id={key_id} keys={keys.keys()}")
        if key_id in keys.keys():
            logging.info(f"Change data limit for key id={key_id} successfully")
            client.add_data_limit(int(key_id), data_limit)
            await message.answer(f"Data limit for key with id {key_id}:\n{command[2]}Gb",
                                 parse_mode="Markdown")
        else:
            logging.info(f"key with id {key_id} not existed")
            await message.answer(f"Key with id {key_id} not existed")
    except IndexError:
        logging.error(f"no specified key id - change_data_limit")
        await message.answer("There is no key id. Specify key name: "
                             "`/changelimit <id> <limit_in_Gb>`", parse_mode="Markdown")


if __name__ == '__main__':
    try:
        executor.start_polling(dp)
        print("Outline-vpn-bot is running...")
    except Exception as e:
        logging.critical(f"Telegram bot critical error:\n{e}")
