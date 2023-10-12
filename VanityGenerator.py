import sys
import multiprocessing
import logging
from mnemonic import Mnemonic
from pycoin.symbols.btc import network

def find_address(substring, case_sensitive, attempt_count, lock):
    mnemo = Mnemonic("english")
    
    while True:
        # Generate a mnemonic
        mnemonic = mnemo.generate(strength=128)
        
        # Generate a private key and address from the mnemonic
        seed = mnemo.to_seed(mnemonic)
        wallet_key = network.keys.bip32_seed(seed)
        
        # Check various derivation paths
          for change in range(5):
              for address_index in range(10):
                  path = f"44'/0'/0'/{change}/{address_index}"
                  key = wallet_key.subkey_for_path(path)
                  address = key.address()
                  
                  # Update and check the number of attempts
                  with lock:
                      attempt_count.value += 1
                      if attempt_count.value % 10000 == 0:
                          logging.info(f"Attempts: {attempt_count.value}")
                          print(f"Attempts: {attempt_count.value}")
                  
                  # Check if the address contains the substring
                  if case_sensitive:
                      match = substring in address
                  else:
                      match = substring.lower() in address.lower()
                  
                  if match:
                      logging.info(f"Found! Mnemonic: {mnemonic}, Address: {address}, Derivation path: m/{path}")
                      print(f"Found! Mnemonic: {mnemonic}, Address: {address}, Derivation path: m/{path}")
                      return

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    try:
        substring = sys.argv[1]
        case_sensitive = sys.argv[2].lower() in ["1", "true"]
    except IndexError:
        print("Please provide a substring and a boolean value for case-sensitive as arguments.")
        sys.exit(1)

    num_processes = multiprocessing.cpu_count()
    attempt_count = multiprocessing.Value('i', 0)
    lock = multiprocessing.Lock()

    processes = []
    for _ in range(num_processes):
        p = multiprocessing.Process(target=find_address, args=(substring, case_sensitive, attempt_count, lock))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()
