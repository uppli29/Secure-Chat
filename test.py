from random import randint
import math
from Cryptodome.Random import get_random_bytes
import time


def generatePQ():
    rand1 = randint(100, 300)
    rand2 = randint(100, 300)
    fo = open('primes-to-100k.txt', 'r')
    lines = fo.read().splitlines()
    fo.close()
    prime1 = int(lines[rand1])
    prime2 = int(lines[rand2])
    return prime1, prime2


def generate_prime():
    x = randint(100, 9999)
    while True:
        if is_prime(x):
            break
        else:
            x += 1
    return x


def is_prime(x):
    i = 2
    root = math.ceil(math.sqrt(x))
    while i <= root:
        if x % i == 0:
            return False
        i += 1
    return True


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)


def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        return None
    else:
        return x % m


if __name__ == "__main__":

    p, q = generatePQ()
    # p = 1153
    # q = 1621
    print("p: ", p)
    print("q: ", q)
    n = p * q

    n1 = (p - 1) * (q - 1)

    r = randint(2, 100)
    while True:
        if gcd(r, n1) == 1:
            break
        else:
            r += 1
    e = r
    print("e = %d" % e)

    d = modinv(e, n1)
    print("d = %d" % d)

    m = get_random_bytes(16).hex()
    encrypted_blocks = []
    ciphertext = -1

    if (len(m) > 0):

        ciphertext = ord(m[0])

        for i in range(1, len(m)):

            if (i % 2 == 0):
                encrypted_blocks.append(ciphertext)
                ciphertext = 0

            ciphertext = ciphertext * 1000 + ord(m[i])

        encrypted_blocks.append(ciphertext)

        for i in range(len(encrypted_blocks)):
            encrypted_blocks[i] = str((encrypted_blocks[i]**e) % n)
        print(encrypted_blocks)
    start_time = time.time()
    message = ""
    for i in range(len(encrypted_blocks)):
        encrypted_blocks[i] = (int(encrypted_blocks[i])**d) % n
        tmp = ""

        for c in range(2):
            tmp = chr(encrypted_blocks[i] % 1000) + tmp
            encrypted_blocks[i] //= 1000
        message += tmp
    print("--- %s seconds ---" % (time.time() - start_time))
    print(message)
