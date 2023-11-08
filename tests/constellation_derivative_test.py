

import pytest
from algokit_utils import (
    ApplicationClient,
    ApplicationSpecification,
    get_localnet_default_account,
)
from algosdk.v2client.algod import AlgodClient

from smart_contracts.constellation_derivative import (
    contract as constellation_derivative_contract,
)


# Fixture for `constellation_derivative_app_spec`
@pytest.fixture(scope="session")
def constellation_derivative_app_spec(algod_client: AlgodClient) -> ApplicationSpecification:
    return constellation_derivative_contract.app.build(algod_client)

# Fixture for `constellation_derivative_client`
@pytest.fixture(scope="session")
def constellation_derivative_client(
    algod_client: AlgodClient, constellation_derivative_app_spec: ApplicationSpecification
) -> ApplicationClient:
    client = ApplicationClient(
        algod_client,
        app_spec=constellation_derivative_app_spec,
        signer=get_localnet_default_account(algod_client),
        template_values={"UPDATABLE": 1, "DELETABLE": 1},
    )
    client.create()
    return client

# Test for the "hello" function
def test_says_hello(constellation_derivative_client: ApplicationClient) -> None:
    result = constellation_derivative_client.call(
        constellation_derivative_contract.hello, name="World"
    )
    assert result.return_value == "Hello, World"



# Test Creating an Option
def test_create_option(constellation_derivative_client: ApplicationClient) -> None:
    # Define test data
    counter_offer = 1000
    expires = 1650000000

    # Call the create_option function
    option_id = constellation_derivative_client.call(
        constellation_derivative_contract.create_option, counter_offer, expires
    )

    # Fetch the created option from global state
    option = constellation_derivative_client.get_global_state("option_list")[option_id]

    # Verify the option was created with the expected values
    assert option.creator == constellation_derivative_client.address
    assert option.owner == constellation_derivative_client.address
    assert option.collateral == counter_offer  # Assuming collateral matches counter_offer
    assert not option.for_sale
    assert option.price == 0
    assert option.expires == expires

    # Verify global state updates
    total_options = constellation_derivative_client.get_global_state("total_options")
    assert total_options == option_id

# Test Transferring Ownership
def test_transfer_option(constellation_derivative_client: ApplicationClient) -> None:
    # Create an option first
    option_id = constellation_derivative_client.call(
        constellation_derivative_contract.create_option, 1000, 1650000000
    )

    # Define test data
    new_owner = "new_owner_address"  # Replace with a valid new owner address

    # Call the transfer function
    constellation_derivative_client.call(
        constellation_derivative_contract.transfer, option_id, new_owner
    )

    # Fetch the option from global state
    option = constellation_derivative_client.get_global_state("option_list")[option_id]

    # Verify that the new owner is the owner of the option
    assert option.owner == new_owner

    # Verify owner_list mappings
    owner_list = constellation_derivative_client.get_global_state("owner_list")
    assert (constellation_derivative_client.address, option_id) not in owner_list
    assert (new_owner, option_id) in owner_list

# Test Listing an Option for Sale
def test_list_for_sale(constellation_derivative_client: ApplicationClient) -> None:
    # Create an option first
    option_id = constellation_derivative_client.call(
        constellation_derivative_contract.create_option, 1000, 1650000000
    )

    # Define test data
    price = 500

    # Call the list_for_sale function
    constellation_derivative_client.call(
        constellation_derivative_contract.list_for_sale, option_id, price
    )

    # Fetch the option from global state
    option = constellation_derivative_client.get_global_state("option_list")[option_id]

    # Verify that the option is listed for sale with the specified price
    assert option.for_sale
    assert option.price == price

    # Verify market_list update
    market_list = constellation_derivative_client.get_global_state("market_list")
    assert option_id in market_list

# Test Removing an Option from Sale
def test_remove_from_sale(constellation_derivative_client: ApplicationClient) -> None:
    # Create an option and list it for sale
    option_id = constellation_derivative_client.call(
        constellation_derivative_contract.create_option, 1000, 1650000000
    )
    constellation_derivative_client.call(
        constellation_derivative_contract.list_for_sale, option_id, 500
    )

    # Call the remove_from_sale function
    constellation_derivative_client.call(
        constellation_derivative_contract.remove_from_sale, option_id
    )

    # Fetch the option from global state
    option = constellation_derivative_client.get_global_state("option_list")[option_id]

    # Verify that the option is no longer listed for sale
    assert not option.for_sale
    assert option.price == 0

    # Verify market_list update
    market_list = constellation_derivative_client.get_global_state("market_list")
    assert option_id not in market_list

    """
    Please make sure to replace "new_owner_address" with a valid address in the
    test_transfer_option function. These test cases assume the existence of certain
    global state variables and mappings, so make sure that they match the implementation
    of your smart contract. Adjust the test data and expected values as needed to suit
    your contract's logic.
    """

    # Test Buying an Option
def test_buy_option(constellation_derivative_client: ApplicationClient) -> None:
    # Create an option and list it for sale
    option_id = constellation_derivative_client.call(
        constellation_derivative_contract.create_option, 1000, 1650000000
    )
    constellation_derivative_client.call(
        constellation_derivative_contract.list_for_sale, option_id, 500
    )

    # Define test data
    buyer_address = "buyer_address"  # Replace with a valid buyer address
    initial_seller_balance = 10000  # Replace with the initial balance of the seller
    initial_buyer_balance = 10000  # Replace with the initial balance of the buyer

    # Set initial balances for testing
    constellation_derivative_client.set_balance(constellation_derivative_client.address, initial_seller_balance)
    constellation_derivative_client.set_balance(buyer_address, initial_buyer_balance)

    # Call the buy function
    constellation_derivative_client.call(
        constellation_derivative_contract.buy, option_id
    )

    # Verify that the buyer is now the owner of the option
    option = constellation_derivative_client.get_global_state("option_list")[option_id]
    assert option.owner == buyer_address

    # Verify market_list update
    market_list = constellation_derivative_client.get_global_state("market_list")
    assert option_id not in market_list

    # Verify balances
    seller_balance = constellation_derivative_client.get_balance(constellation_derivative_client.address)
    buyer_balance = constellation_derivative_client.get_balance(buyer_address)
    assert seller_balance == initial_seller_balance + 500  # Assuming 500 was the price
    assert buyer_balance == initial_buyer_balance - 500

# Test Executing an Option
def test_execute_option(constellation_derivative_client: ApplicationClient) -> None:
    # Create an option and set it to be executed
    option_id = constellation_derivative_client.call(
        constellation_derivative_contract.create_option, 1000, 1650000000
    )
    constellation_derivative_client.call(
        constellation_derivative_contract.execute, option_id
    )

    # Define test data
    initial_creator_balance = 10000  # Replace with the initial balance of the creator
    initial_buyer_balance = 10000  # Replace with the initial balance of the buyer

    # Set initial balances for testing
    constellation_derivative_client.set_balance(constellation_derivative_client.address, initial_creator_balance)
    constellation_derivative_client.set_balance("buyer_address", initial_buyer_balance)

    # Fetch the option from global state
    option = constellation_derivative_client.get_global_state("option_list")[option_id]

    # Call the execute function
    constellation_derivative_client.call(
        constellation_derivative_contract.execute, option_id
    )

    # Verify that the counter_offer amount was sent to the creator
    creator_balance = constellation_derivative_client.get_balance(option.creator)
    assert creator_balance == initial_creator_balance + 1000  # Assuming 1000 was the counter_offer amount

    # Verify that the collateral was sent to the buyer
    buyer_balance = constellation_derivative_client.get_balance(constellation_derivative_client.address)
    assert buyer_balance == initial_buyer_balance + 1000  # Assuming collateral amount was 1000

    # Verify that the option is deleted and mappings are removed
    option_list = constellation_derivative_client.get_global_state("option_list")
    assert option_id not in option_list
    owner_list = constellation_derivative_client.get_global_state("owner_list")
    assert (option.owner, option_id) not in owner_list
    creator_list = constellation_derivative_client.get_global_state("creator_list")
    assert (option.creator, option_id) not in creator_list

# Test Burning an Option
def test_burn_option(constellation_derivative_client: ApplicationClient) -> None:
    # Create an option and set it to be burned
    option_id = constellation_derivative_client.call(
        constellation_derivative_contract.create_option, 1000, 1650000000
    )
    constellation_derivative_client.call(
        constellation_derivative_contract.burn, option_id
    )

    # Define test data
    initial_creator_balance = 10000  # Replace with the initial balance of the creator

    # Set initial balances for testing
    constellation_derivative_client.set_balance(constellation_derivative_client.address, initial_creator_balance)

    # Fetch the option from global state
    option = constellation_derivative_client.get_global_state("option_list")[option_id]

    # Call the burn function
    constellation_derivative_client.call(
        constellation_derivative_contract.burn, option_id
    )

    # Verify that the collateral was sent to the creator
    creator_balance = constellation_derivative_client.get_balance(option.creator)
    assert creator_balance == initial_creator_balance + 1000  # Assuming collateral amount was 1000

    # Verify that the option is deleted and mappings are removed
    option_list = constellation_derivative_client.get_global_state("option_list")
    assert option_id not in option_list
    owner_list = constellation_derivative_client.get_global_state("owner_list")
    assert (option.owner, option_id) not in owner_list
    creator_list = constellation_derivative_client.get_global_state("creator_list")
    assert (option.creator, option_id) not in creator_list

# Test Claiming an Expired Option
def test_claim_expired_option(constellation_derivative_client: ApplicationClient) -> None:
    # Create an expired option
    option_id = constellation_derivative_client.call(
        constellation_derivative_contract.create_option, 1000, 0  # Set expires to an expired timestamp
    )
    constellation_derivative_client.call(
        constellation_derivative_contract.claim_expired, option_id
    )

    # Define test data
    initial_creator_balance = 10000  # Replace with the initial balance of the creator

    # Set initial balances for testing
    constellation_derivative_client.set_balance(constellation_derivative_client.address, initial_creator_balance)

    # Fetch the option from global state
    option = constellation_derivative_client.get_global_state("option_list")[option_id]

    # Call the claim_expired function
    constellation_derivative_client.call(
        constellation_derivative_contract.claim_expired, option_id
    )

    # Verify that the collateral was sent to the creator
    creator_balance = constellation_derivative_client.get_balance(option.creator)
    assert creator_balance == initial_creator_balance + 1000  # Assuming collateral amount was 1000

    # Verify that the option is deleted and mappings are removed
    option_list = constellation_derivative_client.get_global_state("option_list")
    assert option_id not in option_list
    owner_list = constellation_derivative_client.get_global_state("owner_list")
    assert (option.owner, option_id) not in owner_list
    creator_list = constellation_derivative_client.get_global_state("creator_list")
    assert (option.creator, option_id) not in creator_list

    """Please replace "buyer_address" with a valid buyer address in the test_buy_option
    function. Adapt the test data and expected values as needed to match your contract's
    logic and data types.
    """

# Test Querying an Option
def test_query_option(constellation_derivative_client: ApplicationClient) -> None:
    # Create an option and retrieve its details
    option_id = constellation_derivative_client.call(
        constellation_derivative_contract.create_option, 1000, 1650000000
    )
    option = constellation_derivative_client.get_global_state("option_list")[option_id]

    # Query the option
    queried_option = constellation_derivative_client.call(
        constellation_derivative_contract.query_option, option_id
    )

    # Verify that the queried option's details match the created option
    assert queried_option.creator == option.creator
    assert queried_option.collateral == option.collateral
    assert queried_option.owner == option.owner
    assert queried_option.counter_offer == option.counter_offer
    assert queried_option.for_sale == option.for_sale
    assert queried_option.price == option.price
    assert queried_option.expires == option.expires

# Test Querying All Options
def test_query_all_options(constellation_derivative_client: ApplicationClient) -> None:
    # Create multiple options
    option_id1 = constellation_derivative_client.call(
        constellation_derivative_contract.create_option, 1000, 1650000000
    )
    option_id2 = constellation_derivative_client.call(
        constellation_derivative_contract.create_option, 2000, 1650000000
    )

    # Query all options
    options = constellation_derivative_client.call(
        constellation_derivative_contract.query_all_options
    )

    # Verify the correct number of options returned
    assert len(options) == 2

    # Verify the details of the options
    assert options[option_id1].creator == constellation_derivative_client.address
    assert options[option_id1].collateral == 1000
    assert options[option_id2].creator == constellation_derivative_client.address
    assert options[option_id2].collateral == 2000

# Test Querying Options Owned by an Address
def test_query_owner_options(constellation_derivative_client: ApplicationClient) -> None:
    # Create an option as the owner
    option_id1 = constellation_derivative_client.call(
        constellation_derivative_contract.create_option, 1000, 1650000000
    )

    # Create another option with a different owner
    option_id2 = "option_id2"  # Replace with a different owner address
    constellation_derivative_client.call(
        constellation_derivative_contract.create_option, 2000, 1650000000
    )

    # Query options owned by the owner
    owner_options = constellation_derivative_client.call(
        constellation_derivative_contract.query_owner_options
    )

    # Verify that only option_id1 is returned
    assert len(owner_options) == 1
    assert owner_options[0].id == option_id1

"""
Please replace "buyer_address" and "option_id2" with valid addresses and values as needed.
These tests cover querying an individual option, querying all options, and querying options
owned by a specific address. Adjust the test data and expected values as per your contract
logic and data types.
"""





"""
import pytest
from .contract import app
from algokit_utils import (
    ApplicationClient,
    ApplicationSpecification,
    get_localnet_default_account,
)
from algosdk.v2client.algod import AlgodClient

from smart_contracts.constellation_derivative import contract as constellation_derivative_contract


@pytest.fixture(scope="session")
def constellation_derivative_app_spec(algod_client: AlgodClient) -> ApplicationSpecification:
    return constellation_derivative_contract.app.build(algod_client)


@pytest.fixture(scope="session")
def constellation_derivative_client(
    algod_client: AlgodClient, constellation_derivative_app_spec: ApplicationSpecification
) -> ApplicationClient:
    client = ApplicationClient(
        algod_client,
        app_spec=constellation_derivative_app_spec,
        signer=get_localnet_default_account(algod_client),
        template_values={"UPDATABLE": 1, "DELETABLE": 1},
    )
    client.create()
    return client


def test_says_hello(constellation_derivative_client: ApplicationClient) -> None:
    result = constellation_derivative_client.call(constellation_derivative_contract.hello, name="World")

    assert result.return_value == "Hello, World"
"""


""""
@pytest.fixture
def client():
  client = app.build_and_deploy()
  yield client
  client.close()

def test_create_option(client):
  option_id = client.call(
    create_option,
    counter_offer=1000,
    expires=1650000000
  )

  option = client.get_global_state("option_list")[option_id]

  assert option.creator == client.address
  assert option.collateral == 1000

def test_transfer_option(client):

  # Create option
  option_id = client.call(
    create_option,
    counter_offer=1000,
    expires=1650000000
  )

  # Transfer option
  client.call(
    transfer,
    option_id=option_id,
    new_owner=new_owner
  )

  # Check option owner updated
  option = client.get_global_state("option_list")[option_id]
  assert option.owner == new_owner

  # Check old owner mapping deleted
  assert (original_owner, option_id) not in client.get_global_state("owner_list")

  # Check new owner mapping added
  assert (new_owner, option_id) in client.get_global_state("owner_list")

  # Check option still in creator mapping
  assert (original_owner, option_id) in client.get_global_state("creator_list")


  def test_list_for_sale(client):

  # Create option
  option_id = client.call(create_option, ...)

  # List for sale
  price = 1000
  client.call(
    list_for_sale,
    option_id=option_id,
    price=price
  )

  # Verify option marked for sale
  option = client.get_global_state("option_list")[option_id]
  assert option.for_sale == True

  # Verify price set
  assert option.price == price

  # Verify added to market list
  assert option_id in client.get_global_state("market_list")

  # Verify mappings unchanged
  assert (original_owner, option_id) in client.get_global_state("owner_list")
  assert (original_creator, option_id) in client.get_global_state("creator_list")

  def test_buy(client):

  # Create option
  option_id = client.call(create_option, ...)

  # List for sale
  client.call(list_for_sale, option_id=option_id, price=1000)

  # Buy option
  client.call(buy, option_id=option_id)

  # Verify buyer is new owner
  option = client.get_global_state("option_list")[option_id]
  assert option.owner == client.address

  # Verify removed from market
  assert option_id not in client.get_global_state("market_list")

  # Verify buyer added to owner list
  assert (client.address, option_id) in client.get_global_state("owner_list")

  # Verify payment transferred to seller
  payment_amount = 1000
  assert len(client.algod.account_info(seller_address)["created-assets"]) == payment_amount

  def test_remove_from_sale(client):

  # List for sale
  client.call(list_for_sale, option_id=1, price=1000)

  # Remove from sale
  client.call(remove_from_sale, option_id=1)

  # Verify for_sale False
  option = client.get_global_state("option_list")[1]
  assert option.for_sale == False

  # Verify price reset
  assert option.price == 0

  # Not in market list
  assert 1 not in client.get_global_state("market_list")

  # Mappings unchanged
  assert (seller, 1) in client.get_global_state("owner_list")
  assert (creator, 1) in client.get_global_state("creator_list")

  def test_execute(client):

  # Create option
  id = client.call(create_option, ...)

  # Execute
  client.call(execute, id)

  # Counter offer sent to creator
  assert creator_balance increased by counter_offer_amount

  # Collateral sent to caller
  assert client.balance increased by collateral_amount

  # Option deleted
  assert id not in client.get_global_state("option_list")

  # Mappings deleted
  assert (creator, id) not in client.get_global_state("creator_list")
  assert (client.address, id) not in client.get_global_state("owner_list")

  def test_burn(client):

  # Create option
  id = client.call(create_option, ...)

  # Burn option
  client.call(burn, id)

  # Collateral sent to creator
  assert creator_balance increased by collateral_amount

  # Option deleted
  assert id not in client.get_global_state("option_list")

  # Mappings deleted
  assert (creator, id) not in client.get_global_state("creator_list")
  assert (client.address, id) not in client.get_global_state("owner_list")

  def test_claim_expired(client):

  # Create expired option
  id = client.call(create_option, ..., expires=past_time)

  # Claim expired
  client.call(claim_expired, id)

  # Collateral sent to creator
  assert creator_balance increased by collateral_amount

  # Option deleted
  assert id not in client.get_global_state("option_list")

  # Mappings deleted
  assert (creator, id) not in client.get_global_state("creator_list")
  assert (client.address, id) not in client.get_global_state("owner_list")

  def test_query_option(client):

  # Create option
  id = client.call(create_option, ...)

  # Query option
  option = client.get_global_state("option_list")[id]

  # Verify option fields
  assert option.creator == creator_address
  assert option.collateral == collateral_amount
  ...

  def test_query_all_options(client):

  # Create some options
  id1 = client.call(create_option, ...)
  id2 = client.call(create_option, ...)

  # Query all options
  options = client.get_global_state("option_list")

  # Verify correct number returned
  assert len(options) == 2

  # Verify option fields
  assert options[id1].creator == creator1
  assert options[id2].collateral == collateral2_amount

  def test_query_owner_options(client):

  # Create option as owner
  id1 = client.call(create_option, ...)

  # Create option as different owner
  id2 = other_client.call(create_option, ...)

  # Query owner options
  options = [v for k, v in client.get_global_state("owner_list").items() if k[0] == client.address]

  # Verify only option1 returned
  assert len(options) == 1
  assert options[0].id == id1

  def test_query_creator_options(client):

  # Create options as creator
  id1 = client.call(create_option, ...)
  id2 = client.call(create_option, ...)

  # Query creator options
  options = [v for k, v in client.get_global_state("creator_list").items() if k[0] == client.address]

  # Verify both options returned
  assert len(options) == 2
  assert id1 in [opt.id for opt in options]
  assert id2 in [opt.id for opt in options]

  def test_transfer_ownership(client):

  # Create option
  id = client.call(create_option, ...)

  # Transfer ownership
  new_owner = some_other_address
  client.call(transfer, id, new_owner)

  # Verify owner changed
  option = client.get_global_state("option_list")[id]
  assert option.owner == new_owner

  # Verify old owner mapping deleted
  assert (client.address, id) not in client.get_global_state("owner_list")

  # Verify new owner mapping added
  assert (new_owner, id) in client.get_global_state("owner_list")

  def test_update_sale_price(client):

  # List for sale
  id = client.call(list_for_sale, option_id=1, price=1000)

  # Update price
  new_price = 1500
  client.call(update_sale_price, id, new_price)

  # Verify price updated
  option = client.get_global_state("option_list")[1]
  assert option.price == new_price

  # Still in market
  assert id in client.get_global_state("market_list")

  def test_incorrect_payment(client):

  # List for sale
  client.call(list_for_sale, option_id=1, price=1000)

  # Try to buy with lower payment
  with pytest.raises(Exception):
    client.call(buy, option_id=1, payment=500)

    def test_expiration(client):

  # Try to create expired option
  expired_time = yesterday
  with pytest.raises(Exception):
    client.call(create_option, ..., expires=expired_time)

  # Create valid option
  id = client.call(create_option, ..., expires=tomorrow)

  # Try to execute expired
  fast_forward(client, add_days(2))
  with pytest.raises(Exception):
    client.call(execute, id)

    def test_unauthorized(client):

  # Create option
  id = client.call(create_option, ...)

  # Try to update as different user
  with pytest.raises(Exception):
    other_client.call(update_sale_price, id, 1000)

  # Try to buy as different user
  with pytest.raises(Exception):
    other_client.call(buy, id)

    def test_invalid_option_id(client):

  invalid_id = 999

  # Try to get invalid option
  with pytest.raises(Exception):
    client.get_global_state("option_list")[invalid_id]

  # Try to execute invalid option
  with pytest.raises(Exception):
    client.call(execute, invalid_id)

def test_marketplace(client):

  # List option for sale
  id = client.call(list_for_sale, option_id=1, price=1000)

  # Buy option
  buyer.call(buy, id)

  # Verify buyer is new owner
  option = client.get_global_state("option_list")[id]
  assert option.owner == buyer.address

  # Verify payment transferred
  assert buyer.balance decreased by 1000
  assert client.balance increased by 1000

  # Re-list for higher price
  client.call(list_for_sale, id, price=1500)

  # Another buyer purchases
  buyer2.call(buy, id)

  # Verify new owner and payment
  assert option.owner == buyer2.address
  assert buyer2.balance decreased by 1500
  assert client.balance increased by 1500

  def test_claim_expired(client):

  # Create expired option
  expired_time = yesterday
  id = client.call(create_option, ..., expires=expired_time)

  # Claim it
  client.call(claim_expired, id)

  # Collateral returned to creator
  assert client.balance increased by collateral_amount

  # Option deleted
  assert id not in client.get_global_state("option_list")

  def test_queries(client):

  # Create some options
  id1 = client.call(create_option, ...)
  id2 = client.call(list_for_sale, option_id=id1, price=1000)

  # Query onsale options
  onsale = [opt for opt in client.get_global_state("option_list").values() if opt.for_sale]
  assert len(onsale) == 1
  assert onsale[0].id == id2

  # Query by owner
  owners_opts = [opt for opt in client.query_by_owner(some_address)]
  assert len(owners_opts) == 2

  def test_lock_collateral(client):

  # Create option with collateral
  collateral = 1000
  id = client.call(create_option, collateral=collateral)

  # Verify collateral locked
  assert client.balance == original_balance - collateral

  # Burn option
  client.call(burn, id)

  # Verify collateral returned
  assert client.balance == original_balance

  def test_non_creator_claim(client):

  # Create expired option
  id = client.call(create_option, ..., expires=yesterday)

  # Try to claim as different user
  with pytest.raises(Exception):
    other_client.call(claim_expired, id)

    def test_concurrent_requests(client1, client2):

  # List option for sale
  id = client1.call(list_for_sale, option_id=1, price=1000)

  # Try to buy concurrently
  buyer1_txn = client1.call_async(buy, id)
  buyer2_txn = client2.call_async(buy, id)

  # Verify only one succeeds
  assert buyer1_txn.confirmed ^ buyer2_txn.confirmed

  def test_error_handling(client):

  # Try to create with invalid collateral
  with pytest.raises(Exception):
    client.call(create_option, collateral=[INVALID_ASSET])

  # Try to buy with insufficient payment
  with pytest.raises(Exception):
    client.call(buy, option_id=1, payment=10)

    def test_multi_collateral(client):

  # Create options with different collateral
  id1 = client.call(create_option, collateral=ALGO)
  id2 = client.call(create_option, collateral=ASA1)

  # Verify collateral stored properly
  opt1 = client.get_global_state("option_list")[id1]
  assert opt1.collateral == ALGO

  opt2 = client.get_global_state("option_list")[id2]
  assert opt2.collateral == ASA1

  def test_variable_expiration(client):

  # Create options expiring at different times
  id1 = client.call(create_option, ..., expires=t1)
  id2 = client.call(create_option, ..., expires=t2)

  # Verify expiration stored properly
  opt1 = client.get_global_state("option_list")[id1]
  assert opt1.expires == t1

  opt2 = client.get_global_state("option_list")[id2]
  assert opt2.expires == t2

  def test_counter_offer(client):

  # Create options with different counter offers
  id1 = client.call(create_option, counter_offer=1000)
  id2 = client.call(create_option, counter_offer=1500)

  # Verify counter offers stored properly
  opt1 = client.get_global_state("option_list")[id1]
  assert opt1.counter_offer == 1000

  opt2 = client.get_global_state("option_list")[id2]
  assert opt2.counter_offer == 1500

  def test_burn_nonexpired(client):

  # Create option
  id = client.call(create_option, ..., expires=tomorrow)

  # Try to burn non-expired option
  with pytest.raises(Exception):
    client.call(burn, id)

    def test_thirdparty_listing(client, other_client):

  # Create option
  id = client.call(create_option, ...)

  # List for sale as different user
  other_client.call(list_for_sale, id, 1000)

  # Verify listed
  assert id in other_client.get_global_state("market_list")

  def test_dup_option_ids(client):

  # Create option
  id = client.call(create_option, ...)

  # Try to create option with same id
  with pytest.raises(Exception):
    client.call(create_option, ..., id=id)

    def test_invalid_account_queries(client):

  # Query options for invalid account
  opts = client.query_by_owner(invalid_address)
  assert len(opts) == 0

  # Query as invalid creator
  opts = client.query_by_creator(invalid_address)
  assert len(opts) == 0
"""
