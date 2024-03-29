from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import sys
from Cryptodome.Hash import HMAC, SHA256
import os
import pickle
import bcrypt
#  --------custom imports
from configs.RSA import RSACipher
from configs.AES import AESCipher
from configs.keygen import key_generation

# Socket initialization
SERVER = socket(AF_INET, SOCK_STREAM)  # TCP

# ip and port setup
IP_ADDRESS = '127.0.0.1'
PORT = 15000
RECV_SIZE = 4096

# local storage for client information
CLIENT_LIST = {}
USER_LIST = {}
NAME_LIST = []

# set server to active
ACTIVE = True
SERVER_LOOP = None

# initialize cipher algorithms
AES = None
private_key, public_key = key_generation()
RSA = RSACipher()


def set_up_server():
    global ACTIVE
    try:
        SERVER.bind((IP_ADDRESS, PORT))
    except OSError:
        print("failed!")
        ACTIVE = False
        return

    print("Server started on port 15000")
    SERVER_LOOP = Thread(target=listen_incoming)
    SERVER_LOOP.start()
    SERVER_LOOP.join()


def listen_incoming():
    SERVER.listen()
    while ACTIVE:
        # wait on connection, then output details to server
        (client, address) = SERVER.accept()
        print(f" * {address} has connected.")
        Thread(target=client_thread, args=(client,)).start()


def client_thread(c):
    global ACTIVE
    try:
        # receive user name and public key
        user_dict = c.recv(4096)
        user_dict = pickle.loads(user_dict)
        # session_key = get_random_bytes(16)
        session_key = os.urandom(16)

        # add username:pub_key in dictionary
        for key in user_dict:
            name = key
        public_key = user_dict[name]

        enc_sess_key = RSA.encrypt(public_key, session_key)
        print(name, 'encrypted session key ', enc_sess_key, '\n'*2)
        USER_LIST[name] = [public_key, session_key]

        c.send(enc_sess_key)
        CLIENT_LIST[c] = name
        NAME_LIST.append(name)

        print("Current Users Online:")

        for client, username in CLIENT_LIST.items():
            print(username)

        user_string = "<" + name + "> "
        private_string = "[" + name + "] "  # private message delivery

        join_message = f" * {name} has joined the server.\n"
        send_all(join_message, c)

        while ACTIVE:
            # receive CT and hash from the user
            msg_and_hash = c.recv(RECV_SIZE)

            msg_and_hash = pickle.loads(msg_and_hash)

            # separate ct and hash
            message = msg_and_hash[0]
            hmac = msg_and_hash[1]

            # print(name, message, 'hash: ', mac)

            AES = AESCipher((USER_LIST[name])[1])
            print(name," : ",message)
            print('HMAC ', hmac)
            # decrypt client msg
            message = AES.decrypt(message)
            # compute hash and verify with received hash
            compute_mac = HMAC.new((USER_LIST[name])[1], digestmod=SHA256)
            compute_mac.update(message)
            if(compute_mac.digest() == hmac):

                message = message.decode('utf-8')

                if message == "/bye":  # quit handler
                    quit_message = f" * {name} has left the server.\n"
                    signal = b'exit'
                    # h256 = hashlib.sha256(signal).hexdigest()
                    compute_mac.update(signal)
                    AES = AESCipher((USER_LIST[name])[1])
                    ct = AES.encrypt(signal)
                    msg_and_hash = [ct, compute_mac.digest()]
                    c.send(pickle.dumps(msg_and_hash))
                    print(quit_message)
                    del CLIENT_LIST[c]
                    del USER_LIST[name]
                    send_all(quit_message, c)
                    c.close()
                    break

                 # private messages to specific user
                elif message.startswith("@"):
                    if len(message.split(' ')) > 1:
                        (user, msg) = message.split(' ', 1)
                        sent_msg = private_string + msg
                        send_user(sent_msg, user[1:], c)

                else:  # vanilla message
                    message = user_string + message
                    send_all(message, c)

    except ConnectionResetError:
        quit_message = f" * {name} has left the server.\n"
        print(quit_message)
        send_all(quit_message, c)
        c.close()
        del CLIENT_LIST[c]
        del USER_LIST[name]


# send msg to all users except the current user
def send_all(message, sender):
    if type(message) == str:
        message = message.encode('utf-8')
    for client, username in CLIENT_LIST.items():

        if client != sender:

            msg = message

            AES = AESCipher((USER_LIST[username])[1])
            # encrypt the msg with users session key
            hmac = HMAC.new((USER_LIST[username])[1], digestmod=SHA256)
            hmac.update(msg)
            msg = AES.encrypt(msg)
            # compute hash

            msg_and_hash = [msg, hmac.digest()]
            # send hash and cipher text
            client.send(pickle.dumps(msg_and_hash))

# send msg to the specified user


def send_user(message, recipient, sender):

    if type(message) == str:
        message = message.encode('utf-8')
    for client, username in CLIENT_LIST.items():
        # only specific client/user
        if username == recipient and client != sender:

            AES = AESCipher((USER_LIST[username])[1])
            # h256 = hashlib.sha256(message).hexdigest()
            hmac = HMAC.new((USER_LIST[username])[1], digestmod=SHA256)
            hmac.update(message)
            message = AES.encrypt(message)
            msg_and_hash = [message, hmac.digest()]
            client.send(pickle.dumps(msg_and_hash))
            break


def auth_admin():
    password = input('Enter password to start server: ')
    with open('pwd.txt', 'rb') as f:
        hash = f.read()
    try:
        bcrypt.checkpw(password.encode('utf-8'), hash)
        return True
    except:
        return False


if __name__ == "__main__":
    if(auth_admin()):
        set_up_server()
        SERVER.close()
        exit(0)
    else:
        print('Password didn\'t match!')
        sys.exit(0)
