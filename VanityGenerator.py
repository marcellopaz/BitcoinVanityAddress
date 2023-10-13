import argparse
import multiprocessing
import logging
from bip_utils import (
    Bip39MnemonicGenerator, Bip39SeedGenerator,
    Bip44, Bip44Coins, Bip44Changes,
    Bip49, Bip49Coins,
    Bip84, Bip84Coins
)

def find_address(blockchain, address_type, substring, passphrase, case_sensitive, position, attempt_count, lock):
    """
    Busca por um endereço Bitcoin que contenha uma substring específica.

    :param address_type: str, Tipo de endereço a ser gerado (bip44, bip49, bip84).
    :param substring: str, Substring para procurar no endereço.
    :param passphrase: str, Senha para geração da seed a partir da mnemônica.
    :param case_sensitive: bool, Se a busca deve ser sensível a maiúsculas/minúsculas.
    :param position: str, Posição da substring no endereço (start, anywhere, end).
    :param attempt_count: multiprocessing.Value, Contador de tentativas.
    :param lock: multiprocessing.Lock, Lock para controle de acesso ao contador.
    """
    while True:
        # Gera uma mnemônica
        generatormn = Bip39MnemonicGenerator()
        mnemonic = generatormn.FromWordsNumber(12)
        
        # Gera uma seed a partir da mnemônica
        seed_bytes = Bip39SeedGenerator(mnemonic).Generate(passphrase)
        if blockchain == "bitcoin":
            # Cria uma carteira do tipo especificado
            if address_type == "bip44":
                bip_obj_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
                start_with = "1"
                derivation_prefix = "44'/0'/"
            elif address_type == "bip49":
                bip_obj_mst = Bip49.FromSeed(seed_bytes, Bip49Coins.BITCOIN)
                start_with = "3"
                derivation_prefix = "49'/0'/"
            elif address_type == "bip84":
                bip_obj_mst = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)
                start_with = "bc1q"
                derivation_prefix = "84'/0'/"

            else:
                raise ValueError("Tipo de endereço não suportado.")
        elif blockchain == "ethereum":
            #For Ethereum the patern is always Bip44
            bip_obj_mst = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
            start_with = "0x"
            derivation_prefix = "44'/60'/"


        # Deriva uma chave e um endereço da carteira
        for account in range(1):
            for change in range(1):
                for address_index in range(50):
                    # Cria o caminho de derivação
                    derivation_path = f"m/{derivation_prefix}{account}'/{change}/{address_index}"
                    
                    # Deriva a chave usando o caminho
                    bip_obj_c = (
                        bip_obj_mst.Purpose()
                        .Coin()
                        .Account(0)
                        .Change(Bip44Changes.CHAIN_EXT)
                        .AddressIndex(address_index)
                    )
                    # Obtém o endereço P2SH-P2WPKH (começa com "3")
                    address = bip_obj_c.PublicKey().ToAddress()
                    
                    # Atualiza e verifica o número de tentativas
                    with lock:
                        attempt_count.value += 1
                        if attempt_count.value % 1000000 == 0:
                            logging.info(f"Attempts: {attempt_count.value}")
                            print(f"Attempts: {attempt_count.value}")
                    
                    # Verifica se o endereço contém a substring
                    if case_sensitive:
                        match = (
                            (position == 'start' and address.startswith(start_with + substring)) or
                            (position == 'anywhere' and substring in address) or
                            (position == 'end' and address.endswith(substring))
                        )
                    else:
                        match = (
                            (position == 'start' and address.lower().startswith(start_with + substring.lower())) or
                            (position == 'anywhere' and substring.lower() in address.lower()) or
                            (position == 'end' and address.lower().endswith(substring.lower()))
                        )
                    
                    # Se encontrou, loga e retorna
                    if match:
                        logging.info(f"Found! Mnemonic: {mnemonic}, Address: {address}, Derivation Path: {derivation_path}")
                        print(f"Found! Mnemonic: {mnemonic}, Address: {address}, Derivation Path: {derivation_path}")
                        return

def parse_arguments():
    """
    Analisa os argumentos de linha de comando.

    :return: Namespace, Argumentos parseados.
    """
    parser = argparse.ArgumentParser(description="Find a Bitcoin address with a specific substring.")
    parser.add_argument("-s", "--substring", required=True, help="The substring to search for in the address.")
    parser.add_argument("-c", "--case-sensitive", type=bool, default=False, help="Whether the search should be case-sensitive. Default is False.")
    parser.add_argument("-p", "--position", choices=['start', 'anywhere', 'end'], default='anywhere', help="Where in the address to search for the substring. Default is 'anywhere'.")
    parser.add_argument("-a", "--address-type", choices=['bip44', 'bip49', 'bip84'], default='bip44', help="The type of address to generate. Default is 'bip44'.")
    parser.add_argument("-x", "--passphrase", default="", help="Optional passphrase for generating the seed from the mnemonic. Default is an empty string.")
    parser.add_argument("-b", "--blockchain", default="bitcoin", help="Optional blockchain if you don't want bitcoin. Default is bitcoin.")
    
    return parser.parse_args()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Parse dos argumentos de linha de comando
    args = parse_arguments()
    
    # Obtém o número de processos com base no número de CPUs disponíveis
    num_processes = multiprocessing.cpu_count()
    
    # Inicializa um contador de tentativas e um lock para controle de acesso
    attempt_count = multiprocessing.Value('i', 0)
    lock = multiprocessing.Lock()

    # Cria e inicia os processos
    processes = []
    for _ in range(num_processes):
        p = multiprocessing.Process(
            target=find_address,
            args=(
                args.blockchain,
                args.address_type,
                args.substring,
                args.passphrase,
                args.case_sensitive,
                args.position,
                attempt_count,
                lock
            )
        )
        processes.append(p)
        p.start()

    # Aguarda todos os processos terminarem
    for p in processes:
        p.join()

