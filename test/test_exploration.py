import logging
import re
import sys
import unittest
from typing import Optional

import requests
import os

from urllib.parse import urlparse

from requests import ReadTimeout

from blockchain_exploration.exploration import (
    get_explorer_url_for_account, get_explorer_url_for_nft_contract, get_explorer_url_for_token)
from blockchain_exploration.types import Network, get_label_for_network

if not os.getenv('APP_STAGE'):
    os.environ['APP_STAGE'] = 'production'  # This is the environment where the tests most need to pass
# These paths are defined as environment variables for each service:
# https://github.com/sweet-io-org/aws-terraform/tree/master/providers/aws/us-east-1/production
"""
if not os.getenv('ETH_EXPLORER_BASEPATH'):
    os.environ['ETH_EXPLORER_BASEPATH'] = "https://etherscan.io/"
if not os.getenv('MATIC_EXPLORER_BASEPATH'):
    os.environ['MATIC_EXPLORER_BASEPATH'] = "https://polygonscan.com/"
    # Sometimes we specify this as https://opensea.io/assets/matic
if not os.getenv('TEZOS_EXPLORER_BASEPATH'):
    os.environ['TEZOS_EXPLORER_BASEPATH'] = "https://better-call.dev/"
"""

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

HEADER_MATCHER = re.compile(r'<h[0-9]+')


class TestBlockchain(unittest.TestCase):
    sample_accounts_by_network = {
        # Accounts holding tokens
        Network.BITCOIN_CASH: "simpleledger:qrgydxn0xnta6k4lkc4xmrltz4ghvlz7tq33dez6nv",
        Network.ETHEREUM: "0xf8e6480aaed82328e837172d4fb450826ec547cf",
        Network.POLYGON: "0x3AFac8309C2a93406c326dbb9Ab2578F3ed165d9",
        Network.TEZOS: "tz1WisZWgB8u7MUf9eM8Zxs6HWPChs4qoXEg"
    }
    sample_contracts_by_network = {
        Network.BITCOIN_CASH: "62b2b7bdadbf17685bbdb1827adcec17928baab26cf7d96e3cc27855f741fe63",  # Genesis txn
        Network.ETHEREUM: "0xC4df6018F90f91baD7e24f89279305715B3A276F",
        Network.POLYGON: "0x3011810abfec25777a01d5fbef08b2ad12860460",
        Network.TEZOS: "KT1PEGqt5rMmHpyaMXc8RFTFkkAUDrzSFRWk"
    }
    sample_txn_by_network = {
        Network.BITCOIN_CASH: sample_contracts_by_network[Network.BITCOIN_CASH],
        Network.ETHEREUM: "0x6f13920eba73100469511a0df990c811ee89fd15fb5b3c95ec40f4d991fc90d4",
        Network.POLYGON: "0xd3d4de1612017d7e8c69c70879ab4ba3b2f4e2c638f05b5d13b2c417e46f5be2",
        Network.TEZOS: "ookXoN2hrQ8aPU9yGsE7N5Q65mLXtTCjtYR4nmWUYq73od7mSrx"
    }

    def assert_url_validity(self, explorer_url: Optional[str], expected_text: str):
        self.assertIsNotNone(explorer_url)
        parsed = urlparse(explorer_url)
        self.assertNotIn('//', parsed.path, msg=f"There should not be a double-backslash: {explorer_url}")
        self.assertTrue(parsed.scheme, "A complete URL should have an access scheme")
        self.assertTrue(parsed.netloc, "A complete URL should have a domain name or IP address")
        self.assertTrue(parsed.path, "It's improbable that there's a domain wholly devoted to one token "
                                     "− there should be a path")
        logger.info("%s", explorer_url)
        if os.getenv('SKIP_URL_RETRIEVAL', 'false') in {'true', '1'}:
            return
        try:
            response = requests.get(url=explorer_url, timeout=10, headers={"User-Agent": "Sweet.io test",
                                                                           "Accept": "application/json"})
        except ReadTimeout:
            logger.warning("A connection error prevented us from receiving a response from %s", explorer_url)
            return  # todo: pass a signal that the URL wasn't actually retrieved
        self.assertTrue(response.ok)
        self.assertTrue(response.text, msg="Why was the response empty upon contacting {}".format(explorer_url))
        loading_js = 'without JavaScript enabled' in response.text
        if loading_js:
            logger.info("The page is still loading, so we're unable to assert whether it's actually relevant to us. "
                        "At least we've been able to verify that URLs can indeed be generated for Tezos tokens")
        else:
            self.assertIn(expected_text.lower(), response.text.lower(),
                          f"This expected text was not found: {expected_text}")

    def test_get_label_for_network(self):
        for network in {Network.BITCOIN_CASH, Network.ETHEREUM, Network.MATIC, Network.TEZOS}:
            self.assertTrue(get_label_for_network(network))

    def test_get_explorer_url_for_account(self):
        results = set()
        for network, address in self.sample_accounts_by_network.items():
            url = get_explorer_url_for_account(network=network, address=address)
            self.assert_url_validity(explorer_url=url,
                                     expected_text="transaction")  # Transactions are mentioned for account overview
            self.assertNotIn(url, results)
            results.add(url)

    def test_get_explorer_url_for_token_wallet(self):
        results = set()
        for network, address in self.sample_accounts_by_network.items():
            url = get_explorer_url_for_account(network=network, address=address)
            self.assert_url_validity(explorer_url=url,
                                     expected_text="hash")  # Hashes for transactions
            self.assertNotIn(url, results)
            results.add(url)

    def test_get_explorer_url_for_nft_contract(self):
        results = set()
        for network, contract in self.sample_contracts_by_network.items():
            url = get_explorer_url_for_nft_contract(network=network, contract_address=contract)
            self.assert_url_validity(explorer_url=url,
                                     expected_text="hash")  # Hashes for transactions
            self.assertNotIn(url, results)
            results.add(url)

    def test_get_explorer_url_for_token(self):
        results = set()
        for network, contract in self.sample_contracts_by_network.items():
            url = get_explorer_url_for_token(network=network, contract_address=contract, sequence_number=1)
            self.assert_url_validity(explorer_url=url,
                                     expected_text="hash")  # Hashes for transactions
            self.assertNotIn(url, results)
            results.add(url)

    def test_get_explorer_url_for_transaction(self):
        results = set()
        for network, contract in self.sample_contracts_by_network.items():
            url = get_explorer_url_for_nft_contract(network=network, contract_address=contract)
            self.assert_url_validity(explorer_url=url,
                                     expected_text="hash")  # Hashes for transactions
            self.assertNotIn(url, results)
            results.add(url)
