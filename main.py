from outline_vpn.outline_vpn import OutlineVPN
from aiogram import Bot, Dispatcher, executor, types
import os
import sys
import logging

# environment variables with credentials
API_TOKEN = os.environ.get('TELEGRAM_API_TOKEN')
OUTLINE_API_URL = os.environ.get('OUTLINE_API_URL')
# environment variables
LOGGING_LEVEL = os.environ.get('LOGGING_LEVEL', 'ERROR')
AUTHORIZED_IDS = os.environ.get('AUTHORIZED_IDS')
AUTHORIZED_IDS = AUTHORIZED_IDS.split(',') if AUTHORIZED_IDS else ""

# Setup the access with the API URL (Use the one provided to you after the server setup)
client = OutlineVPN(api_url=OUTLINE_API_URL)
# logging setup
logs = logging.getLogger()
logs.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logs.addHandler(handler)
# set logging level
if LOGGING_LEVEL.upper() == "ERROR":
    handler.setLevel(logging.ERROR)
elif LOGGING_LEVEL.upper() == "INFO":
    handler.setLevel(logging.INFO)
elif LOGGING_LEVEL.upper() == "DEBUG":
    handler.setLevel(logging.DEBUG)
elif LOGGING_LEVEL.upper() == "CRITICAL":
    handler.setLevel(logging.CRITICAL)
else:
    handler.setLevel(logging.WARNING)


def show_keys():
    keys_list = ""
    for key in client.get_keys():
        keys_list += f"{key.key_id} {key.name if key.name else 'Noname'} " \
                     f"{int(key.used_bytes / (1024 ** 3)) if key.used_bytes else 0}Gb\n"
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


def create_key(name):
    """
    :param name: key name
    :return: connection URL string
    """
    try:
        new_key = client.create_key()
        client.rename_key(new_key.key_id, name)
        client.add_data_limit(new_key.key_id, 1024 ** 3 * 50)  # 50Gb
        logging.info(f"create new key {name} successfully")
        return new_key.access_url
    except Exception as e:
        logging.exception(f"create_key {name} error {e}")


def permission_check(func):
    """
    Decorator to check telegram user permissions
    """
    async def wrapped(message: types.Message):
        # permission check code goes here
        user_id = message.from_user.id
        # For example, we only allow users with user_id 123 and 456 to run the command
        if str(user_id) not in AUTHORIZED_IDS:
            logging.error(f"user id {user_id} don't have permissions")
            await message.answer(f"You do not have permission to run this command.\nYour user_id={user_id}")
            return
        # if permission check pass, run the original function
        await func(message)
    return wrapped


# telegram bot section
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)  # look for updates


@dp.message_handler(commands=['start'])
@permission_check
async def send_welcome(message: types.Message):
    await message.reply(
        "**Create new VPN key:** /newkey <keyname>\n"
        "**List existed keys:** /showkeys\n"
        "**Delete key:** /delkey <keyid>\n", parse_mode="Markdown")


@dp.message_handler(commands=['newkey'])
@permission_check
async def newkey(message: types.Message):
    name_exists = False
    try:
        key_name = message.text.split()[1]
        keys = get_keys()
        for key in keys.values():
            if key['name'] == key_name:
                name_exists = True
        if not name_exists:
            key_access_url = create_key(key_name)
            await message.answer(f"Access URL for new key:\n`{key_access_url}`")
        else:
            logging.error(f"key {key_name} already existed")
            await message.answer(f"Key with name {key_name} already exists")
    except IndexError:
        await message.answer(f"There is no key name. Specify key name: `/newkey <keyname>`",  parse_mode="Markdown")


@dp.message_handler(commands=['showkeys'])
@permission_check
async def showkeys(message: types.Message):
    await message.answer(f"**ID Name  Traffic**:\n{show_keys()}", parse_mode="Markdown")


@dp.message_handler(commands=['delkey'])
@permission_check
async def delkey(message: types.Message):
    keys = get_keys()
    try:
        key_id = message.text.split()[1]
        if key_id in keys.values():
            client.delete_key(int(key_id))
            logging.info(f"delete key id={key_id} successfully")
            await message.answer(f"Key with id {key_id} was deleted")
        else:
            logging.info(f"key with id {key_id} not existed")
            await message.answer(f"Key with id {key_id} not existed")
    except IndexError:
        logging.error("no specified key id to delete")
        await message.answer("There is no key id. Specify key name: `/delkey <id>`")


if __name__ == '__main__':
    print("Running...")
    executor.start_polling(dp)
