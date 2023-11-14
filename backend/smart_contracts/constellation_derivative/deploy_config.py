import logging
import algokit_utils
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient

logger = logging.getLogger(__name__)

# define deployment behavior based on the supplied app spec
def deploy(
    algod_client: AlgodClient,
    indexer_client: IndexerClient,
    app_spec: algokit_utils.ApplicationSpecification,
    deployer: algokit_utils.Account,
) -> None:
    from smart_contracts.artifacts.ConstellationDerivative.client import ConstellationDerivativeClient

    app_client = ConstellationDerivativeClient(
        algod_client=algod_client,
        creator=deployer,
        indexer_client=indexer_client,
        existing_deployments=None,  # Update with your existing deployments if needed
        app_id=0,  # Update with your app_id if you have one
        signer=None,  # Update with your signer if needed
        sender=None,  # Update with your sender address if needed
        suggested_params=None,  # Update with your suggested_params if needed
        template_values=None,  # Update with your template values if needed
        app_name="Constellaiton",  # Update with your application name
    )
    app_client.deploy(
        on_schema_break=algokit_utils.OnSchemaBreak.AppendApp,
        on_update=algokit_utils.OnUpdate.AppendApp,
    )

    # Example usage of contract functionality after deployment
    counter_offer = 1000  # Replace with your desired amount (as uint64)
    expires = 1677647999  # Replace with your desired timestamp (as uint64)

  # Create an option
    create_option_txn = app_client.create_option(
    counter_offer=counter_offer,
    expires_timestamp=expires,
    transaction_parameters= None  # replace with actual transaction parameters if needed
)
    logger.info(f"Option creation transaction ID: {create_option_txn}")

""""
    # Retrieve the option ID from the transaction response (assuming your create_option method returns the option ID)
    option_id = app_client.get_option_id_from_transaction_response(create_option_txn)
    
    # Transfer ownership internally
    transfer_txn = _internal_transfer(option_id, new_owner)
    logger.info(f"Ownership transferred. Transaction ID: {transfer_txn}")

    # List the option for sale internally
    list_for_sale_txn = _internal_list_for_sale(option_id, price)
    logger.info(f"Option listed for sale. Transaction ID: {list_for_sale_txn}")

    # Buy the option internally
    buy_txn = _internal_buy(option_id)
    logger.info(f"Option bought. Transaction ID: {buy_txn}")

    # Execute the option internally
    execute_option_txn = _internal_execute_option(option_id)
    logger.info(f"Option executed. Transaction ID: {execute_option_txn}")

    # Claim expired option internally
    claim_expired_txn = _internal_claim_expired(option_id)
    logger.info(f"Option claimed as expired. Transaction ID: {claim_expired_txn}")

    # Close out the option internally
    close_out_txn = _internal_close_out(option_id)
    logger.info(f"Option closed out. Transaction ID: {close_out_txn}")
"""    
logger.info("Deployment and contract interactions completed.")
