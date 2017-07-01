import binascii
import os

# skip, just for manual testing
import random

if __name__ == '__main__':
    for x in range(0, 128):
        from ssshare.control import fxc_web_api_service
        secret = binascii.hexlify(os.urandom(random.randint(1024,1024))).decode()
        tot = random.randint(5, 10)
        diff = random.randint(1, 4)
        tot = 12
        diff = 2
        shares = fxc_web_api_service.split(secret, tot-diff, tot)
        assert secret == fxc_web_api_service.combine(shares, tot-diff, tot)