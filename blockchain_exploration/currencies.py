from typing import DefaultDict, Dict

from blockchain_exploration.types import Network


class CryptoCurrency(DefaultDict):
    symbol: str
    code: str
    native_token: bool
    display_text: str


# Supported ISO-style currency codes used for payment tracking.
# This aligns with for example https://coinmarketcap.com/all/views/all/
NETWORK_CURRENCIES: Dict[str, Dict[str, CryptoCurrency]] = {
    Network.BITCOIN_CASH: {
        "bch": {
            "symbol": "₿",
            "code": "bch",
            "native_token": True,
            "display_text": "BCH",
        }
    },
    Network.TEZOS: {
        "xtz": {
            "symbol": "ꜩ",
            "code": "xtz",
            "native_token": True,
            "display_text": "ꜩ"
        }
    },
    Network.MATIC: {
        "matic": {
            "symbol": "MATIC",
            "code": "matic",
            "native_token": True,
            "display_text": "MATIC",
        }
    },
    Network.ETHEREUM: {
        "eth": {
            "symbol": "ETH",
            "code": "eth",
            "native_token": True,
            "display_text": "ether",
        }
    },
}
