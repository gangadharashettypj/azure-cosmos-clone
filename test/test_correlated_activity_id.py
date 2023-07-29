# The MIT License (MIT)
# Copyright (c) 2022 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest
from unittest.mock import MagicMock

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos.partition_key import PartitionKey

pytestmark = pytest.mark.cosmosEmulator


@pytest.mark.usefixtures("teardown")
class CorrelatedActivityIdTest(unittest.TestCase):
    configs = test_config._test_config
    host = configs.host
    masterKey = configs.masterKey

    @classmethod
    def setUpClass(cls):
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.database = cls.client.create_database_if_not_exists(test_config._test_config.TEST_DATABASE_ID)
        cls.container = cls.database.create_container(id=test_config._test_config.TEST_COLLECTION_MULTI_PARTITION_ID,
                                                      partition_key=PartitionKey(path="/id"))

    def side_effect_correlated_activity_id(self, *args):
        # Extract request headers from args
        assert args[2]["x-ms-cosmos-correlated-activityid"]  # cspell:disable-line
        raise StopIteration

    def test_correlated_activity_id(self):
        query = 'SELECT * from c ORDER BY c._ts'

        cosmos_client_connection = self.container.client_connection
        cosmos_client_connection._CosmosClientConnection__Get = MagicMock(
            side_effect=self.side_effect_correlated_activity_id)
        try:
            self.container.query_items(query=query, partition_key="pk-1")
        except StopIteration:
            pass


if __name__ == "__main__":
    unittest.main()
