# DO NOT USE THESE FOR SWEET.IO INTERNAL NETWORK REFERENCES, THESE
# ARE ONLY RELEVANT TO THIS PACKAGE.
class Network:
    BITCOIN_CASH = "bitcoin-cash"  # https://bitcoincash.org/
    ETHEREUM = "ethereum"  # http://ethereum.org/
    MATIC = "matic"  # https://polygon.technology/
    TEZOS = "tezos"  # https://tezos.com/
    SUI = "sui"


class TokenType:
    SLP = "slp"
    ERC721_ETH = "erc721-eth"
    ERC721_MATIC = "erc721-matic"
    TEZOS = "tezos"
    SUI = "sui"


def is_evm_network(network: str) -> bool:
    return network in {Network.ETHEREUM, Network.MATIC}


def get_label_for_network(network: str) -> str:
    return str(network)
