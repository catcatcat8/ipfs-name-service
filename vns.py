# Лебедев Евгений name-сервис для создания профилей пользователей в IPFS

import sys
import ecdsa
import ipfsApi
import os

def generate_keys():
    """Генерация пары ключей ECDSA secp256k1"""

    pr_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    pub_key = pr_key.get_verifying_key()

    return pr_key, pub_key

def file_updating(user_pubkey, user_ipfs_link):
    """Запись/обновление ipfs-link пользователя в файле name_service.txt"""

    updating = False  # обновление/новая запись
    with open ('name_service.txt') as f:
        for line in f:
            if line.find(user_pubkey) != -1:
                updating = True
                break
    f.close()
    if not updating:  # новая запись в name-сервис
        our_data_file = open("name_service.txt", "a")
        our_data_file.write(f'\n{user_pubkey}')
        our_data_file.write(f'\nlink:{user_ipfs_link}')
        our_data_file.close()
    else:
        with open ('name_service.txt', 'w+') as f:  # update старой записи
            for line in f:
                if line.find(user_pubkey) == -1:
                    file_str += line
        f.close()
        our_data_file = open("name_service.txt", "w")
        our_data_file.write(file_str)
        our_data_file.close()

        our_data_file = open("name_service.txt", "a")
        our_data_file.write(f'\n{user_pubkey}')
        our_data_file.write(f'\nlink:{user_ipfs_link}')
        our_data_file.close()
                    

def ipfs_generate(name, birthdate, filename):
    """Создает/обновляет файл с информацией о пользователе, добавляет его в IPFS, возвращает ipfs-link и ее sig"""

    filename = f'{name}_{filename[:5]}.txt'
    user_info_file = open(f'{filename}', "w")

    # Запись пользовательских данных в файл
    user_info_file.write(f'Name: {name}\n')
    user_info_file.write(f'Birthdate: {birthdate}')
    user_info_file.close()
    
    api = ipfsApi.Client('127.0.0.1', 5001)  # требует ipfs-daemon заранее
    res = api.add(f'{filename}')  # добавление в ipfs
    
    ipfs_link = res["Hash"]
    ipfs_link_sign = vasya_pr_key.sign(ipfs_link.encode("utf-8"))  # генерация подписи

    return ipfs_link, ipfs_link_sign.hex()


def name_service_set(username, ipfs_link, link_sign):
    """Добавление/обновление ipfs-link в name-сервис"""

    # Если пользователя еще нет в name-сервисе, проверяет подпись ipfs-link. Если она правильная, добавляет ipfs-link в сервис.
    # Если пользователь уже есть в name-сервисе, проверяет подпись ipfs-link. Если она правильная, обновляет ipfs-link в сервисе.
    vasya_pub_key_list = username.split(':')[1]
    vasya_pub_key = "".join(vasya_pub_key_list)
    vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(vasya_pub_key), curve=ecdsa.SECP256k1)
    try:
        vk.verify(bytes.fromhex(link_sign), bytes(ipfs_link, encoding="utf-8"))
    except ecdsa.keys.BadSignatureError:
        print("Wrong digital signature!\n")
    else:
        file_updating(username, ipfs_link)
        print("\nresult: ok (signature correct)\n")

def name_service_get(username):
    """Возвращает ipfs-link пользователя и data из ipfs, если он найден"""

    user_found = False
    with open('name_service.txt') as f:
        for line in f:
            if user_found == False:
                if line.strip('\n') == username:
                    user_found = True
            if user_found:
                if line.find("link") != -1:
                    ipfs_link = line
                    break
    if user_found:
        print(f'\n{ipfs_link}\n')  # возвращает ipfs-link
        print('data(from IPFS node):')
        ipfs_link = ipfs_link[ipfs_link.find(':')+1:]
        os.system(f'ipfs cat /ipfs/{ipfs_link}')  # возвращает data из ipfs
        print ('\n')
    else:
        print("\nuser not found\n")
    

if __name__ == "__main__":

    try: 
        (sys.argv[1])
    except IndexError:
        # Для отладки через IDE
        uid = '--uid=vasya:8bb50d4ecd6ac8ad31ae0b4a9cda74b1469b4473841208cfb4f4bc6c1b7bad6d9b84d84aa5c05caa1a3d6bd94c1a218d5f9c766aec45cee2c160d393015608f5'
        command = "get"
    else:
        if sys.argv[1] == "--request-type=name-record-generate":
            command = "generate"
        elif sys.argv[1] == "--request-type=name-record-set":
            uid = sys.argv[2]
            ipfs_link = sys.argv[3]
            sig = sys.argv[4]
            command = "set"
        elif sys.argv[1] == "--request-type=name-record-get":
            uid = sys.argv[2]
            command = "get"
    
    # --- Режим генерации
    if command=="generate":
        vasya_pr_key, vasya_pub_key = generate_keys()  # генерация ключей secp256k1
        pr_key_str = vasya_pr_key.to_string()
        pub_key_str = vasya_pub_key.to_string()

        pub_key_str_to_file = pub_key_str.hex()
        name = str(input("Username: "))
        birthdate = str(input("Birthdate: "))
        ipfs_link, ipfs_link_sig = ipfs_generate(name, birthdate, pub_key_str_to_file)

        our_nickname = "enter_your_nickname"
        name_service_username = f'{our_nickname}:{pub_key_str.hex()}' # name_service_username = user_name:user_public_key

        print(f'--uid={name_service_username}\n--ipfs-link={ipfs_link}\n--sig={ipfs_link_sig}')

    # --- Режим добавления/обновления
    if command == "set":
        # Обрезаем параметры командной строки начиная с '='
        uid = uid[uid.find('=')+1:]
        ipfs_link = ipfs_link[ipfs_link.find('=')+1:]
        sig = sig[sig.find('=')+1:]

        name_service_set(uid, ipfs_link, sig)

    # --- Режим запроса
    if command == "get":
        uid = uid[uid.find('=')+1:]
        name_service_get(uid)