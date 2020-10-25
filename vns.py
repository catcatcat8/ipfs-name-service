# Лебедев Евгений name-сервис для создания профилей пользователей в IPFS

import sys
import ecdsa
from hashlib import sha256

def generate_keys():
    """Генерация пары ключей ECDSA secp256k1"""

    pr_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    pub_key = pr_key.get_verifying_key()

    return pr_key, pub_key

def file_updating(user_data):
    """Запись/обновление информации о пользователе в файле"""

    our_data_file = open("data.txt", "w")
    our_data_file.write(user_data)


def name_service_work(username, ipfs_link, link_sign, user_info_to_file):
    """Добавление/обновление ipfs-link в name-сервис"""

    # Если пользователя еще нет в name-сервисе, проверяет подпись ipfs-link. Если она правильная, сохраняет строку в файл, добавляет ipfs-link в сервис.
    # Если пользователь уже есть в name-сервисе, проверяет подпись ipfs-link. Если она правильная, обновляет строку файла, обновляет ipfs-link в сервисе.
    vasya_pub_key_list = username.split(':')[1]
    vasya_pub_key = "".join(vasya_pub_key_list)
    vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(vasya_pub_key), curve=ecdsa.SECP256k1, hashfunc=sha256)
    if vk.verify(bytes.fromhex(link_sign), bytes.fromhex(ipfs_link)):
        name_service[username] = ipfs_link
        file_updating(user_info_to_file)
    else:
        print("Wrong digital signature!")


if __name__ == "__main__":

    try: 
        (sys.argv[1])
    except IndexError:
        uid = "--uid=vasya:e4de58fc3eee8412d75e203ede6f2693baa658b0ef8bb5662fcf44f5baa59705acff74f7756b92f1c733f7b57b046892929da3fe62a21620833e043b69bdfd3e"
        ipfs_link = "--ipfs-link=a16991c90fc509a9bb31f9b89d12afc5e9d1badb591a622c49c76e3f8b159cc1"
        sig = "--sig=d5bbbd4c7474503e460c825e46d26109838283e2d813fefecfe5f334021048dd3db59b5a145ad5d0f67a8f634d5dec17703d6a7babfb3b7a78efb8525b9dba6e"
        update_data = "666"
        command = "set"
    else:
        if sys.argv[1] == "--request-type=name-record-generate":
            command = "generate"
        elif sys.argv[1] == "--request-type=name-record-set":
            uid = sys.argv[2]
            ipfs_link = sys.argv[3]
            sig = sys.argv[4]
            update_data = sys.argv[5]
            command = "set"
    
    if command=="generate":
        name_service = {}
    
        vasya_pr_key, vasya_pub_key = generate_keys()  # генерация ключей secp256k1
        pr_key_str = vasya_pr_key.to_string()
        pub_key_str = vasya_pub_key.to_string()

        our_ipfs_link = sha256(b"our_link").hexdigest()
        ipfs_link_sign = vasya_pr_key.sign(our_ipfs_link.encode("utf-8"))

        our_nickname = "vasya"
        name_service_username = f'{our_nickname}:{pub_key_str.hex()}' # name_service_username = user_name:user_public_key

        print(f'--uid={name_service_username}\n--ipfs-link={our_ipfs_link}\n--sig={ipfs_link_sign.hex()}')

    if command=="set":
        # Обрезаем параметры командной строки начиная с '='
        uid = uid[uid.find('=')+1:]
        ipfs_link = ipfs_link[ipfs_link.find('=')+1:]
        sig = sig[sig.find('=')+1:]
        update_data = update_data[update_data.find('=')+1:]

        name_service = {}

        name_service_work(uid, ipfs_link, sig, update_data)

