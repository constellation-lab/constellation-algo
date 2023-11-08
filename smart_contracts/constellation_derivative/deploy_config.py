""""
import logging

import algokit_utils
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

logger = logging.getLogger(__name__)


# define deployment behaviour based on supplied app spec
def deploy(
    algod_client: AlgodClient,
    indexer_client: IndexerClient,
    app_spec: algokit_utils.ApplicationSpecification,
    deployer: algokit_utils.Account,
) -> None:
    from smart_contracts.artifacts.constellation_derivative.client import (
        ConstellationDerivativeClient,
    )

    app_client = ConstellationDerivativeClient(
        algod_client,
        creator=deployer,
        indexer_client=indexer_client,
    )
    is_mainnet = algokit_utils.is_mainnet(algod_client)
    app_client.deploy(
        on_schema_break=(
            algokit_utils.OnSchemaBreak.AppendApp
            if is_mainnet
            else algokit_utils.OnSchemaBreak.ReplaceApp
        ),
        on_update=algokit_utils.OnUpdate.AppendApp
        if is_mainnet
        else algokit_utils.OnUpdate.UpdateApp,
        allow_delete=not is_mainnet,
        allow_update=not is_mainnet,
    )

    name = "world"
    response = app_client.hello(name=name)
    logger.info(
        f"Called hello on {app_spec.contract.name} ({app_client.app_id}) "
        f"with name={name}, received: {response.return_value}"
    )
---
import logging

import algokit_utils
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
from contract import buy, create_option

from smart_contracts.constellation_derivative.contract import app

logger = logging.getLogger(__name__)

def deploy(
    algod_client: AlgodClient,
    indexer_client: IndexerClient,
    deployer: algokit_utils.Account,
) -> None:
    from smart_contracts.constellation_derivative.contract import (
        ConstellationDerivativeClient,
    )

    app_spec = app.build(algod_client)
    #app_client = ConstellationDerivativeClient(algod_client, app_spec=app_spec, signer=deployer)
    app_client = ConstellationDerivativeClient(
        algod_client,
        creator=deployer,
        indexer_client=indexer_client,
    )
    app_client.deploy()

    logger.info(f"Constellation app {app_client.app_id} deployed by {deployer}")

# Constellation logic
    option_id = app_client.call(create_option, ...)
    logger.info(f"New option {option_id} created")

    app_client.call(buy, option_id)


# Hello world logic
    is_mainnet = algokit_utils.is_mainnet(algod_client)
    app_client.deploy(
        on_schema_break=(
            algokit_utils.OnSchemaBreak.AppendApp
            if is_mainnet
            else algokit_utils.OnSchemaBreak.ReplaceApp
        ),
        on_update=algokit_utils.OnUpdate.AppendApp
        if is_mainnet
        else algokit_utils.OnUpdate.UpdateApp,
        allow_delete=not is_mainnet,
        allow_update=not is_mainnet,
    )

    name = "world"
    response = app_client.hello(name=name)
    logger.info(
        f"Called hello on {app_spec.contract.name} ({app_client.app_id}) "
        f"with name={name}, received: {response.return_value}"
    )
"""
import logging

from algokit_utils import Account, ApplicationClient  # Add these import statements
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

#from beaker import *
# Import contract functions directly from constellation_derivative.py
from constellation_derivative.constellation_derivative import (
    app,
    buy,
    create_option,
)

#from pyteal import *

logger = logging.getLogger(__name__)

def deploy(
    algod_client: AlgodClient,
    indexer_client: IndexerClient,
    deployer: Account,
) -> None:
    app_spec = app.build(algod_client)

    # Deploy the app (if needed)
    app_client = ApplicationClient(algod_client, app_spec=app_spec, signer=deployer)
    app_client.deploy()

    logger.info(f"Constellation app {app_client.app_id} deployed by {deployer}")

    # Your contract logic
    option_id = app_client.call(
        create_option,
        counter_offer=1000,  # Replace with the appropriate values
        expires=1650000000
    )
    logger.info(f"New option {option_id} created")

    app_client.call(buy, option_id)  # Call your contract functions directly

if __name__ == "__main__":
    # Replace this part with your specific deployment logic.
    pass
