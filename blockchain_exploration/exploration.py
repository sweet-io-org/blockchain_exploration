import logging
import os
from string import whitespace
from typing import Optional
from urllib.parse import urlparse

from .types import Network, is_evm_network

LOGGER = logging.getLogger()


def get_base_path(network: str) -> str:
    # To support test networks (eg Rinkeby, Goerli), it's best to change the environment variable for your block
    # explorer. It'll presumably have the same paths as the corresponding mainnet explorer, so we can still build URLs
    # without getting into the minutiae of which specific chain it is.
    if network == Network.BITCOIN_CASH:
        # Another option is bitcoin.com (redirecting to blockchair.com), but it focuses on cash rather than tokens
        result = os.getenv('SLP_EXPLORER_BASEPATH',
                         os.getenv('EXPLORER_BASEPATH', 'https://simpleledger.info'))
    elif network == Network.ETHEREUM:
        result = os.getenv('ETH_EXPLORER_BASEPATH', 'https://etherscan.io/')
    elif network == Network.POLYGON:
        # Could also be https://opensea.io/assets/matic sometimes
        result = os.getenv('MATIC_EXPLORER_BASEPATH', 'https://polygonscan.com/')
    elif network == Network.TEZOS:
        # Could also be https://better-call.dev/
        result = os.getenv('TEZOS_EXPLORER_BASEPATH', 'https://tzkt.io/')
    else:
        raise NotImplementedError(f"Exploration of the {network} network is not supported")
    return result.rstrip('/')


def get_validated_url(url: str) -> str:
    parsed = urlparse(url)
    if not (parsed.scheme and parsed.netloc and parsed.path):
        raise ValueError(f"An invalid explorer URL was generated: {url}")
    return url.strip(whitespace)


def validated_url(naïve_func):
    def validated_func(*args, **kwargs):
        result = naïve_func(*args, **kwargs)
        if result:
            return get_validated_url(url=result)
        else:
            return result
    return validated_func


@validated_url
def get_explorer_url_for_account(network: str, address: str, base_path: Optional[str] = None) -> Optional[str]:
    # An account is a place that can hold funds 💰. Use this function for non-NFT contracts too.
    if not address:
        return None
    base_path = (base_path or get_base_path(network)).rstrip('/')
    address = address.strip(whitespace)
    if network == Network.BITCOIN_CASH:
        return f"{base_path}/address/{address}"
    elif is_evm_network(network):
        if base_path.endswith('/opensea.io'):
            # https://opensea.io/0xeec4013a607d720989db8f464361cdcf2cb7a7bd
            return f"{base_path}/{address}"
        else:
            # https://etherscan.io/address/0xd75004A00Ca9d707a4D318B21353dC8aFB151E72
            return f"{base_path}/address/{address}"
    elif network == Network.TEZOS:
        # https://better-call.dev/mainnet/tz1imqR4V7ehxPeUrewsg6oy7tAPLsDBscTV/operations
        # https://tzkt.io/tz1fRXMLR27hWoD49tdtKunHyfy3CQb5XZst/operations/
        return f"{base_path}/{address}/operations/"
    else:
        raise NotImplementedError(f"No explorer URL can be constructed for {network} addresses")


@validated_url
def get_explorer_url_for_token_wallet(network: str, address: str, base_path: Optional[str] = None) -> str:
    # A token wallet holds tokens 🪙; and perhaps money
    base_path = (base_path or get_base_path(network)).rstrip('/')
    address = address.strip(whitespace)
    if network == Network.BITCOIN_CASH:
        return get_explorer_url_for_account(network, address=address)
    elif is_evm_network(network):
        address_url = get_explorer_url_for_account(network=network, address=address, base_path=base_path)
        if base_path.endswith('/opensea.io'):
            # https://opensea.io/0xeec4013a607d720989db8f464361cdcf2cb7a7bd?search[sortBy]=LISTING_DATE&search[chains][0]=MATIC
            return f"{address_url}?search[sortBy]=LISTING_DATE&search[chains][0]={network.upper()}"
        else:
            # https://etherscan.io/address/0xf8e6480aaed82328e837172d4fb450826ec547cf#tokentxnsErc721
            return f"{address_url}#tokentxnsErc721"
    elif network == Network.TEZOS:
        # https://tzkt.io/tz1ZMZddhgxqBMMB5KwSr6L5PDJFQf2nNwbK/tokens
        return f"{base_path}/{address}/tokens"
    else:
        raise NotImplementedError(f"No explorer URL can be constructed for {network} addresses")


@validated_url
def get_explorer_url_for_nft_contract(network: str, contract_address, base_path: Optional[str] = None) -> str:
    # A central overview of an NFT contract, hopefully focusing on tokens rather than blockchain implementation details
    base_path = (base_path or get_base_path(network)).rstrip('/')
    if network == Network.BITCOIN_CASH:
        # https://simpleledger.info/token/62b2b7bdadbf17685bbdb1827adcec17928baab26cf7d96e3cc27855f741fe63
        return f"{base_path}/token/{contract_address}"
    elif is_evm_network(network):
        if base_path.endswith('/opensea.io'):
            # https://opensea.io/assets?search[query]=0xc4df6018f90f91bad7e24f89279305715b3a276f
            # If we went to https://opensea.io/0xc4df6018f90f91bad7e24f89279305715b3a276f, they'd show us the tokens
            # held by that contract.
            return f"{base_path}/assets?search[query]={contract_address}"
        else:
            # https://etherscan.io/token/0xC4df6018F90f91baD7e24f89279305715B3A276F
            # https://polygonscan.com/token/0x3011810abfec25777a01d5fbef08b2ad12860460
            return f"{base_path}/token/{contract_address}"
    elif network == Network.TEZOS:
        # https://tzkt.io/KT1RFncfJGBN9heZuDGW5vJPYpMKeYcLeZuo/storage/
        return get_explorer_url_for_account(network=network, address=contract_address, base_path=base_path)
    else:
        raise NotImplementedError(f"Exploration of the {network} network by contract is not supported")


@validated_url
def get_explorer_url_for_token(network: str,
                               address: str,
                               token_id: Optional[str],
                               base_path: Optional[str] = None) -> str:
    # An individual token 🪙
    # address can be either for a token (BCH) or a contract (EVM, or Tezos)
    base_path = (base_path or get_base_path(network)).rstrip('/')
    if network == Network.BITCOIN_CASH:
        # https://simpleledger.info/token/62b2b7bdadbf17685bbdb1827adcec17928baab26cf7d96e3cc27855f741fe63
        return f"{base_path}/token/{address}"
    elif is_evm_network(network):
        if base_path.endswith('/opensea.io'):
            # https://opensea.io/assets/0xc4df6018f90f91bad7e24f89279305715b3a276f/1288
            return get_explorer_url_for_nft_contract(network=network, contract_address=address,
                                                     base_path=base_path)
        else:
            # https://polygonscan.com/token/0x3011810abfec25777a01d5fbef08b2ad12860460?a=3191
            return f"{base_path}/token/{address}/?a={token_id}"
    elif network == Network.TEZOS:
        # https://tzkt.io/KT1LHqbTKHKRtTzQAF4Z8KGa1xixQ2266S4w/operations/
        # https://better-call.dev/mainnet/KT1LHqbTKHKRtTzQAF4Z8KGa1xixQ2266S4w/tokens
        return get_explorer_url_for_nft_contract(network=network, contract_address=address,
                                                 base_path=base_path)
    else:
        raise NotImplementedError(f"Exploration of the {network} network is not supported")


def is_token_url_supported(network: str) -> bool:
    # Give callers some guidance that calling `get_explorer_url_for_token()` won't be as desriable as they might have
    # hoped for.
    if network in {Network.BITCOIN_CASH, Network.TEZOS}:
        return False
    else:
        return True


@validated_url
def get_explorer_url_for_transaction(network: str, transaction_hash: str, base_path: Optional[str] = None) -> str:
    # A blockchain transaction, eg the sending of funds or tokens 🕊
    base_path = (base_path or get_base_path(network)).rstrip('/')
    transaction_hash = transaction_hash.strip(whitespace)
    if network == Network.BITCOIN_CASH:
        # https://simpleledger.info/#tx/f63da6fedacb67d7f45fb1aab5663e239e0b09596e670c9e97ced7a80c34c24c
        if base_path.endswith("/simpleledger.info"):
            # https://blockchair.com/bitcoin-cash/transaction/62b2b7bdadbf17685bbdb1827adcec17928baab26cf7d96e3cc27855f741fe63
            return f"{base_path}/#tx/{transaction_hash}"
        else:
            raise NotImplementedError(f"{network} URLs are not supported for {base_path}")
    elif is_evm_network(network):
        if base_path.endswith('/opensea.io'):
            raise NotImplementedError(f"OpenSea does not offer links to individual transactions")
        else:
            # https://polygonscan.com/tx/0x1d13a622fd628e0c77ea28805cfe6cfd3c23ab95a13a8ff81a11cb08a17f35a3
            return f"{base_path}/tx/{transaction_hash}"
    elif network == Network.TEZOS:
        if 'better-call.dev' in base_path:
            # https://better-call.dev/mainnet/opg/ooZ2UVPNprv9GfMCwp6JgpUD54G668xrgnkPR2DRCZokfNChDrS/contents
            return f"{base_path}/opg/{transaction_hash}"
        else:
            # https://tzkt.io/ooZ2UVPNprv9GfMCwp6JgpUD54G668xrgnkPR2DRCZokfNChDrS
            return f"{base_path}/{transaction_hash}"
    else:
        raise NotImplementedError(f"Exploration of the {network} network is not supported")
