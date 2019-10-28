import binascii
from web3 import Web3, HTTPProvider
from ethereum.pow.ethpow import get_cache, hashimoto_light, TT64M1
from ethereum import utils
from random import randint
import sha3
import time

def hex_to_bin(data_hex):
    return binascii.unhexlify(data_hex[2:])

def bin_to_hex(data_bin):
    return '0x' + binascii.hexlify(data_bin)

def bin_to_hex_b(data_bin):
    return b'0x' + binascii.hexlify(data_bin)

def bin_to_hex_b_final(data_bin):
    return (b'0x' + binascii.hexlify(data_bin)).decode("utf-8") 

class EthereumCpuMiner(object):
    def __init__(self, ethereum_url):
        self._conn = Web3(HTTPProvider(ethereum_url, request_kwargs={'timeout':600}))

        self._mining_hash_hex = None
        self._mining_hash_bin = None
        self._target_bin = None
        self._block_number_int = None
        self._nonce_bin = None
        self._mix_digest_bin = None

        print(
        """                                                       
         _____ _____ _____ ___    _____            _____ _             
        |   __|  |  |  _  |_  |  |_   _|___ _ _   |     |_|___ ___ ___ 
        |__   |     |     |_  |    | | | . | | |  | | | | |   | -_|  _|
        |_____|__|__|__|__|___|    |_| |___|_  |  |_|_|_|_|_|_|___|_|  
        				   |___|                        
        """)
        k = sha3.keccak_256()
        k.update('ETC'.encode('utf-8'))
        print('KECCAK256 CONTROL HASH OF "ETC": '+k.hexdigest() + '\n')

    def get_work(self):
        self._mining_hash_hex, _, target_hex, block_number_hex = self._conn.eth.getWork()
        self._mining_hash_bin, self._target_bin, self._block_number_int = \
            hex_to_bin(self._mining_hash_hex), hex_to_bin(target_hex), int(block_number_hex, 16)

    def mine(self, start_nonce=0):
        cache = get_cache(self._block_number_int)
        nonce = start_nonce
        i = 0
        difficulty = int(bin_to_hex_b(self._target_bin)[2:],16)
        print('Difficulty: ',difficulty)
        print('Block Number: ', self._block_number_int)
        cnt = 0
        start = time.time()
        while True:
            i += 1
            cnt+=1
            bin_nonce = utils.zpad(utils.int_to_big_endian((nonce + i)  ), 8)
            k = sha3.keccak_256()
            k.update(self._mining_hash_bin)
            k.update(bin_nonce)
            hash1 = int(k.hexdigest(), 16)
            # o = hashimoto_light(self._block_number_int, cache, self._mining_hash_bin, bin_nonce)
            if hash1 <= difficulty:
                end = time.time()
                self._nonce_bin = bin_nonce
                print('Hashes Done: ',cnt)
                # for x in self._mining_hash_bin:
                #   print(x)
                # for x in bin_nonce:
                #   print(x)
                # print('Nonce: ', bin_nonce, len( bin_nonce))
                print('Block Mining Time: ', end - start)
                return

    def submit_work(self):
        nonce_hex = bin_to_hex_b_final(self._nonce_bin), 
        # choose a random 64 number string 
        mix_digest_hex = "0x"+(str(randint(1000, 9999))*16)
        # mix_digest_hex = self._mining_hash_hex

        work_list = [nonce_hex, self._mining_hash_hex, mix_digest_hex]

        nonce_hasher = sha3.keccak_256()
        nonce_hasher.update((nonce_hex).encode('utf-8'))
        # nonce_hasher.update(self._nonce_bin.encode('utf-8'))
        print("    NONCE IS: ",nonce_hex)

        mining_hash_hasher = sha3.keccak_256()
        mining_hash_hasher.update(self._mining_hash_hex.encode('utf-8'))
        print("    MINING HASH IS: ", self._mining_hash_hex)

        mix_hasher = sha3.keccak_256()
        mix_hasher.update((mix_digest_hex).encode('utf-8'))
        print("    MIX IS: ", self.mix_digest_hex)

        work_hasher = sha3.keccak_256()
        work_concat = ''.join(work_list)
        work_hasher.update(work_concat.encode('utf-8'))
        print('    WORK LIST: ', work_list)

        print('\n')
        print('    VERIFICATION HASH OF NONCE: ', nonce_hasher.hexdigest())
        print('    VERIIFCATION HASH OF MINING HASH: ', mining_hash_hasher.hexdigest())
        print('    VERIFICATION HASH OF MIX: ', mix_hasher.hexdigest())
        print('    VERIFICATION HASH OF WORK LIST: ', work_hasher.hexdigest())

        self._conn.manager.request_blocking("eth_submitWork", work_list)

    def mine_n_blocks(self, n=1):
        for _ in range(n):
            self.get_work()
            print("**Got Work**")
            self.mine()
            print('**Done Mining Block**')
            self.submit_work()
            print('**Submit Answer**')
            # time.sleep(10)

