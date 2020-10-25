# Лебедев Евгений name-сервис для создания профилей пользователей в IPFS

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
    if vasya_pub_key.verify(link_sign, ipfs_link.encode("utf-8")):
        name_service[username] = ipfs_link
        file_updating(user_info_to_file)
    else:
        print("Wrong digital signature!")


if __name__ == "__main__":
    
    name_service = {}
    
    vasya_pr_key, vasya_pub_key = generate_keys()  # генерация ключей secp256k1
    pr_key_str = vasya_pr_key.to_string()
    pub_key_str = vasya_pub_key.to_string()

    our_ipfs_link = sha256(b"our_link").hexdigest()
    ipfs_link_sign = vasya_pr_key.sign(our_ipfs_link.encode("utf-8"))

    our_nickname = "vasya"
    our_data = "Name: Vasiliy Ivanovich Chapaev"
    name_service_username = f'{our_nickname}:{pub_key_str}' # name_service_username = user_name:user_public_key

    name_service_work(name_service_username, our_ipfs_link, ipfs_link_sign, our_data)

    print(f'pr_key: {pr_key_str.hex()}')
    print(f'pub_key: {pub_key_str.hex()}')
