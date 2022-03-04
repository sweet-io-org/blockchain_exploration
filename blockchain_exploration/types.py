class Network:
    BITCOIN_CASH = "bitcoin-cash"  # https://bitcoincash.org/
    ETHEREUM = "ethereum"  # http://ethereum.org/
    MATIC = "matic"  # https://polygon.technology/
    POLYGON = "matic"  # Polygon was formerly named Matic; and this value is spread around our databases
    TEZOS = "tezos"  # https://tezos.com/


def is_evm_network(network: str) -> bool:
    return network in {Network.ETHEREUM, Network.MATIC, Network.POLYGON}


def get_label_for_network(network: str) -> str:
    if not network:
        raise ValueError("No network provided")
    elif network.lower() == Network.BITCOIN_CASH.lower():
        return 'Bitcoin Cash'
    elif network.lower() == Network.ETHEREUM.lower():
        return 'Ethereum'
    elif network.lower() == Network.POLYGON.lower():
        return 'Polygon'
    elif network.lower() == Network.TEZOS.lower():
        return 'Tezos'
    else:
        raise NotImplemented(f"No label known for {network}")
