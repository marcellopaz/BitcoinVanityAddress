usage: VanityGenerator.py [-h] -s SUBSTRING [-c CASE_SENSITIVE] [-p {start,anywhere,end}] [-a {bip44,bip49,bip84}]
                         [-x PASSPHRASE] [-b BLOCKCHAIN]

Find a Bitcoin address with a specific substring.

options:
  -h, --help            show this help message and exit
  -s SUBSTRING, --substring SUBSTRING
                        The substring to search for in the address.
  -c CASE_SENSITIVE, --case-sensitive CASE_SENSITIVE
                        Whether the search should be case-sensitive. Default is False.
  -p {start,anywhere,end}, --position {start,anywhere,end}
                        Where in the address to search for the substring. Default is 'anywhere'.
  -a {bip44,bip49,bip84}, --address-type {bip44,bip49,bip84}
                        The type of address to generate. Default is 'bip44'.
  -x PASSPHRASE, --passphrase PASSPHRASE
                        Optional passphrase for generating the seed from the mnemonic. Default is an empty string.
  -b BLOCKCHAIN, --blockchain BLOCKCHAIN
                        Optional blockchain if you don't want bitcoin. Default is bitcoin.
