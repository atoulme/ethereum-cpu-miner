import binascii
from web3 import Web3, HTTPProvider
from ethereum.pow.ethpow import get_cache, hashimoto_light, TT64M1
from ethereum import utils
import sha3


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
        self._conn = Web3(HTTPProvider(ethereum_url))

        self._mining_hash_hex = None
        self._mining_hash_bin = None
        self._target_bin = None
        self._block_number_int = None
        self._nonce_bin = None
        self._mix_digest_bin = None

    def get_work(self):
        self._mining_hash_hex, _, target_hex, block_number_hex = self._conn.eth.getWork()
        self._mining_hash_bin, self._target_bin, self._block_number_int = \
            hex_to_bin(self._mining_hash_hex), hex_to_bin(target_hex), int(block_number_hex, 16)

    def mine(self, start_nonce=0):
        cache = get_cache(self._block_number_int)
        nonce = start_nonce
        i = 0
        difficulty = int(bin_to_hex_b(self._target_bin)[2:],16)
        print('difficulty',difficulty)
        cnt = 0
        while True:
            i += 1
            cnt+=1
            bin_nonce = utils.zpad(utils.int_to_big_endian((nonce + i)  ), 8)
            k = sha3.keccak_256()
            k.update(self._mining_hash_bin)
            k.update(bin_nonce)
            hash1 = int(k.hexdigest(), 16)
            #o = hashimoto_light(self._block_number_int, cache, self._mining_hash_bin, bin_nonce)
            if hash1 <= difficulty:
                self._nonce_bin = bin_nonce
                print('cnt',cnt)
                for x in self._mining_hash_bin:
                  print(x)
                for x in bin_nonce:
                  print(x)
                print('mh', self._mining_hash_bin, len( self._mining_hash_bin))
                print('nonce', bin_nonce, len( bin_nonce))
                return

    def submit_work(self):
        print("self nonce is", self._nonce_bin)
        nonce_hex, mix_digest_hex = bin_to_hex_b_final(self._nonce_bin), "0x"+"0"*64
        mix_digest_hex = self._mining_hash_hex
        print([nonce_hex, self._mining_hash_hex, mix_digest_hex])
        self._conn.manager.request_blocking("eth_submitWork", [nonce_hex, self._mining_hash_hex, mix_digest_hex])

    def mine_n_blocks(self, n=1):
        for _ in range(n):
            print("hi")
            self.get_work()
            print("get work")
            self.mine()
            print('done mine')
            self.submit_work()
            print('done submit mine')

