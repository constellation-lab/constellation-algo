import beaker
import pyteal as pt
import hashlib


class ConstellationDerivativeState:
    # Global state keys
           ##################################
    # Global State
    # 64 key-value pairs per contract
    # 128 bytes each
    ##################################
    global_state_key = beaker.GlobalStateValue(pt.TealType.bytes, default=pt.Bytes(""))
    total_options_key = beaker.GlobalStateValue(pt.TealType.bytes, default=pt.Bytes(""))
    option_list_key = beaker.GlobalStateValue(pt.TealType.bytes, default=pt.Bytes(""))
    creator_list_key = beaker.GlobalStateValue(pt.TealType.bytes, default=pt.Bytes(""))
    owner_list_key = beaker.GlobalStateValue(pt.TealType.bytes, default=pt.Bytes(""))
    market_list_key = beaker.GlobalStateValue(pt.TealType.bytes, default=pt.Bytes(""))

    option_list_data = beaker.GlobalStateValue(pt.TealType.bytes, default=pt.Bytes(""))
    creator_list_data = beaker.GlobalStateValue(pt.TealType.bytes, default=pt.Bytes(""))
    owner_list_data = beaker.GlobalStateValue(pt.TealType.bytes, default=pt.Bytes(""))
    market_list_data = beaker.GlobalStateValue(pt.TealType.bytes, default=pt.Bytes(""))
    
 

    # Options Owner: Address of the Options Owner
    new_owner = beaker.GlobalStateValue(
        stack_type=pt.TealType.bytes, default=pt.Bytes("")
    )

    # Options price: price of the options
    new_price = beaker.GlobalStateValue(
        stack_type=pt.TealType.uint64, default=pt.Int(0)
    )

        # Collateral price: price of the options
    collateral_price = beaker.GlobalStateValue(
        stack_type=pt.TealType.uint64, default=pt.Int(0)
    )
    
    # Option Expires: Timestamp of the end of the auction
    expires_timestamp = beaker.GlobalStateValue(
        stack_type=pt.TealType.uint64, default=pt.Int(0)
        )

    # REMINDER: ASA === Algorand Standard Asset === Asset === Token

    # ASA: ID of the ASA - of the option
    options_id = beaker.GlobalStateValue(stack_type=pt.TealType.uint64, default=pt.Int(0))

    # ASA amount: Total amount of ASA / options being bought or sold
    options_quantity = beaker.GlobalStateValue(
        stack_type=pt.TealType.uint64, default=pt.Int(0)
    )
    #for sale defaults to 0 not for sale and 1 is for sale
    for_sale = beaker.GlobalStateValue(
        stack_type=pt.TealType.uint64, default=pt.Int(0)
    )

    ##################################
    # Local State
    # 16 key-value pairs per account
    # 128 bytes each
    # Users must opt in before using
    ##################################

    # Claimable amount: Amount of ALGO this account can reclaim when expired
    claimable_amount = beaker.LocalStateValue(
        stack_type=pt.TealType.uint64, default=pt.Int(0)
    )

    # Helper function to create option dict
    @staticmethod
    def make_option(creator, owner, collateral, counter_offer, for_sale, price, expires):
        return {
            "creator": creator,
            "owner": owner,
            "collateral": collateral,
            "counter_offer": counter_offer,
            "for_sale": for_sale,
            "price": price,
            "expires": expires,
        }


app = beaker.Application("ConstellationDerivative", state=ConstellationDerivativeState)

# create method that initializes global state
@app.create(bare=True)
def create() -> pt.Expr:
    return pt.Seq(
        app.state.global_state_key.set(pt.Bytes("initialized")),  # Set the global state to initialized
        app.state.total_options_key.set(pt.Bytes("0")),  # Set total options to 0
    )



# create_option method that allows accounts to create an option
@app.external
def create_option(counter_offer: pt.abi.Uint64, expires_timestamp: pt.abi.Uint64) -> pt.Expr:
    # Ensure the global state is initialized
    assert_initialized = pt.Assert(app.state.global_state_key.get() == pt.Bytes("initialized"))

    # Increment total options
    current_total_options = app.state.total_options_key.get()
    new_total_options = pt.Add(pt.Btoi(current_total_options), pt.Int(1))

    # Convert new_total_options to bytes
    new_total_options_bytes = pt.Itob(new_total_options)
    increment_total_options = app.state.total_options_key.set(new_total_options_bytes)

    # Create the new option
    new_option_id = new_total_options
    new_option_id_bytes = pt.Itob(new_option_id)  # Convert new_option_id to bytes

    new_option = app.state.make_option(
        pt.Txn.sender(),
        pt.Txn.sender(),
        pt.Txn.assets[0],
        counter_offer,
        app.state.for_sale,
        pt.BytesZero,  # Use pt.BytesZero instead of pt.Global.zero
        expires_timestamp,
    )

    # Convert new_option values to PyTeal expressions
    new_option_expr = {
        "creator": new_option["creator"],
        "owner": new_option["owner"],
        "collateral": new_option["collateral"],
        "counter_offer": new_option["counter_offer"],
        "for_sale": app.state.for_sale,
        "price": pt.BytesZero,
        "expires": new_option["expires"],
    }

    # Ensure new_option_id_bytes is in bytes format
    if not isinstance(new_option_id_bytes, bytes):
        new_option_id_bytes = str(new_option_id_bytes).encode()

    # String format for concatenation
    concatenated_data = "{}:{}:{}:{}:{}:{}:{}:{}".format(
        new_option_id_bytes,  # Ensure this is in bytes
        new_option_expr["creator"],
        new_option_expr["owner"],
        new_option_expr["collateral"],
        new_option_expr["counter_offer"],
        new_option_expr["for_sale"],
        new_option_expr["price"],
        new_option_expr["expires"]
    )

    # Use SHA-256 hash function
    hashed_key = hashlib.sha256(concatenated_data.encode()).hexdigest()

    # Update option_list with hashed key
    update_option_list = app.state.option_list_key.set(pt.Bytes(hashed_key.encode()))
    # Update option_data with full concatenated data
    app.state.option_list_data.set(pt.Bytes(concatenated_data.encode()))

    # Concatenate values for owner_list and creator_list
    owner_concatenated_data = "{}:{}:{}".format(
        new_option_expr["owner"],
        new_option_id_bytes.decode(),
        new_option_id_bytes
    )

    creator_concatenated_data = "{}:{}:{}".format(
        new_option_expr["creator"],
        new_option_id_bytes.decode(),
        new_option_id_bytes
    )

    # Use SHA-256 hash function
    owner_hashed_key = hashlib.sha256(owner_concatenated_data.encode()).hexdigest()
    creator_hashed_key = hashlib.sha256(creator_concatenated_data.encode()).hexdigest()

    # Update owner_list with hashed key
    update_owner_list = app.state.owner_list_key.set(pt.Bytes(owner_hashed_key.encode()))
    # Update owner_data with full concatenated data
    app.state.owner_list_data.set(pt.Bytes(owner_concatenated_data.encode()))

    # Update creator_list with hashed key
    update_creator_list = app.state.creator_list_key.set(pt.Bytes(creator_hashed_key.encode()))
    # Update creator_data with full concatenated data
    app.state.creator_list_data.set(pt.Bytes(creator_concatenated_data.encode()))

    # Combine all assignments in a Seq
    return pt.Seq(
        assert_initialized,
        increment_total_options,
        update_option_list,
        update_owner_list,
        update_creator_list
    )

    # Combine all assignments in a Seq
    return pt.Seq(
        assert_initialized,
        increment_total_options,
        update_option_list,
        update_creator_list,
        update_owner_list
    )

# transfer method that allows transferring ownership of an option
def transfer(options_id: pt.Expr, new_owner: pt.Expr) -> pt.Expr:
    # Ensure the global state is initialized
    assert_initialized = pt.Assert(app.state.global_state_key.get() == pt.Bytes("initialized"))

    # Get the option
    option = app.state.option_list_key[options_id]

    # Ensure the caller is the current owner
    assert_caller_is_owner = pt.Assert(option["owner"] == pt.Txn.sender())

    # Transfer ownership
    option["owner"] = new_owner

    # Update option_list
    update_option_list = app.state.option_list_key[options_id] = option

    # Update owner_list
    update_owner_list_sender = app.state.owner_list_key[pt.Txn.sender(), options_id] = None
    update_owner_list_new_owner = app.state.owner_list_key[new_owner, options_id] = option

    return pt.Seq(
        assert_initialized,
        assert_caller_is_owner,
        update_option_list,
        update_owner_list_sender,
        update_owner_list_new_owner
    )



# list_for_sale method that puts an option up for sale
def list_for_sale(options_id: pt.Expr, price: pt.Expr) -> pt.Expr:
    # Ensure the global state is initialized
    assert_initialized = pt.Assert(app.state.global_state_key.get() == pt.Bytes("initialized"))

    # Get the option
    option = app.state.option_list_key[options_id]

    # Ensure the caller is the current owner
    assert_caller_is_owner = pt.Assert(option["owner"] == pt.Txn.sender())

    # Update option
    option["for_sale"] = True
    option["price"] = price

    # Update option_list
    update_option_list = app.state.option_list_key[options_id] = option

    # Update market_list
    update_market_list = app.state.market_list_key[options_id] = option

    return pt.Seq(
        assert_initialized,
        assert_caller_is_owner,
        update_option_list,
        update_market_list
    )


# remove_from_sale method that removes an option from the market
def remove_from_sale(options_id: pt.Expr) -> pt.Expr:
    # Ensure the global state is initialized
    assert_initialized = pt.Assert(app.state.global_state_key.get() == pt.Bytes("initialized"))

    # Get the option
    option = app.state.option_list_key[options_id]

    # Ensure the caller is the current owner
    assert_caller_is_owner = pt.Assert(option["owner"] == pt.Txn.sender())

    # Update option
    option["for_sale"] = False
    option["price"] = pt.BytesZero

    # Update option_list
    update_option_list = app.state.option_list_key[options_id] = option

    # Update market_list
    update_market_list = app.state.market_list_key[options_id] = None

    return pt.Seq(
        assert_initialized,
        assert_caller_is_owner,
        update_option_list,
        update_market_list
    )


# buy method that allows buying an option from the market
def buy(options_id: pt.Expr) -> pt.Expr:
    # Ensure the global state is initialized
    assert_initialized = pt.Assert(app.state.global_state_key.get() == pt.Bytes("initialized"))

    # Get the option
    option = app.state.option_list_key[options_id]

    # Ensure the option is for sale
    assert_option_for_sale = pt.Assert(option["for_sale"] == True)

    # Ensure the buyer has enough balance
    assert_buyer_has_enough_balance = pt.Assert(pt.Txn.sender() == option["owner"])

    # Transfer the collateral to the buyer
    transfer_collateral = pt.Txn.assets[0].transfer(option["collateral"], option["owner"], option["price"])

    # Transfer ownership
    option["owner"] = pt.Txn.sender()

    # Update option
    option["for_sale"] = False
    option["price"] = pt.zero()

    # Update option_list
    update_option_list = app.state.option_list_key[options_id] = option

    # Update owner_list
    update_owner_list_sender = app.state.owner_list_key[pt.Txn.sender(), options_id] = option
    update_owner_list_owner = app.state.owner_list_key[option["owner"], options_id] = None

    # Update market_list
    update_market_list = app.state.market_list_key[options_id] = None

    return pt.Seq(
        assert_initialized,
        assert_option_for_sale,
        assert_buyer_has_enough_balance,
        transfer_collateral,
        update_option_list,
        update_owner_list_sender,
        update_owner_list_owner,
        update_market_list
    )


# update_price method that allows updating the price of an option
def update_price(options_id: pt.Expr, price: pt.Expr) -> pt.Expr:
    # Ensure the global state is initialized
    assert_initialized = pt.Assert(app.state.global_state_key.get() == pt.Bytes("initialized"))

    # Get the option
    option = app.state.option_list_key[options_id]

    # Ensure the caller is the current owner
    assert_caller_is_owner = pt.Assert(option["owner"] == pt.Txn.sender())

    # Update the price
    option["price"] = price

    # Update option_list
    update_option_list = app.state.option_list_key[options_id] = option

    return pt.Seq(
        assert_initialized,
        assert_caller_is_owner,
        update_option_list
    )

# burn method that allows burning an option
def burn(options_id: pt.Expr) -> pt.Expr:
    # Ensure the global state is initialized
    assert_initialized = pt.Assert(app.state.global_state_key.get() == pt.Bytes("initialized"))

    # Get the option
    option = app.state.option_list_key[options_id]

    # Ensure the caller is the current owner
    assert_caller_is_owner = pt.Assert(option["owner"] == pt.Txn.sender())

    # Transfer the collateral to the contract creator
    transfer_collateral = pt.Txn.assets[0].transfer(option["collateral"], app.creator_address, option["collateral"])

    # Update option_list
    update_option_list = app.state.option_list_key[options_id] = None

    # Update creator_list
    update_creator_list = app.state.creator_list_key[option["creator"], options_id] = None

    # Update owner_list
    update_owner_list = app.state.owner_list_key[option["owner"], options_id] = None

    # Update market_list
    update_market_list = app.state.market_list_key[options_id] = None

    return pt.Seq(
        assert_initialized,
        assert_caller_is_owner,
        transfer_collateral,
        update_option_list,
        update_creator_list,
        update_owner_list,
        update_market_list
    )
# claim_expired method that allows claiming the collateral of an expired option
def claim_expired(options_id: pt.Expr) -> pt.Expr:
    # Ensure the global state is initialized
    assert_initialized = pt.Assert(app.state.global_state_key.get() == pt.Bytes("initialized"))

    # Get the option
    option = app.state.option_list_key.get(options_id)

    # Ensure the option is expired
    assert_option_expired = pt.Assert(pt.Txn.group_index() > option["expires"])

    # Ensure the caller is the current owner
    assert_caller_is_owner = pt.Assert(option["owner"] == pt.Txn.sender())

    # Transfer the collateral to the owner
    transfer_collateral = pt.Txn.assets[0].transfer(option["collateral"], pt.Txn.sender(), option["collateral"])

    # Update option_list
    update_option_list = app.state.option_list_key.set(options_id, None)

    # Update creator_list
    update_creator_list = app.state.creator_list_key.set([option["creator"], options_id], None)

    # Update owner_list
    update_owner_list = app.state.owner_list_key.set([option["owner"], options_id], None)

    # Update market_list
    update_market_list = app.state.market_list_key.set(options_id, None)

    return pt.Seq(
        assert_initialized,
        assert_option_expired,
        assert_caller_is_owner,
        transfer_collateral,
        update_option_list,
        update_creator_list,
        update_owner_list,
        update_market_list
    )

# execute_option method that allows executing an option
def execute_option(options_id: pt.Expr) -> pt.Expr:
    # Ensure the global state is initialized
    assert_initialized = pt.Assert(app.state.global_state_key.get() == pt.Bytes("initialized"))

    # Get the option
    option = app.state.option_list_key.get(options_id)

    # Ensure the caller is the current owner
    assert_caller_is_owner = pt.Assert(option["owner"] == pt.Txn.sender())

    # Ensure the option is not for sale
    assert_option_not_for_sale = pt.Assert(option["for_sale"] == False)

    # Transfer the collateral to the contract creator
    transfer_collateral = pt.Txn.assets[0].transfer(option["collateral"], app.creator_address, option["collateral"])

    # Update option_list
    update_option_list = app.state.option_list_key.set(options_id, None)

    # Update creator_list
    update_creator_list = app.state.creator_list_key.set([option["creator"], options_id], None)

    # Update owner_list
    update_owner_list = app.state.owner_list_key.set([option["owner"], options_id], None)

    # Update market_list
    update_market_list = app.state.market_list_key.set(options_id, None)

    return pt.Seq(
        assert_initialized,
        assert_caller_is_owner,
        assert_option_not_for_sale,
        transfer_collateral,
        update_option_list,
        update_creator_list,
        update_owner_list,
        update_market_list
    )


# close_out method that allows closing out an option
def close_out(options_id: pt.Expr) -> pt.Expr:
    # Ensure the global state is initialized
    assert_initialized = pt.Assert(app.state.global_state_key.get() == pt.Bytes("initialized"))

    # Get the option
    option = app.state.option_list_key.get(options_id)

    # Ensure the caller is the current owner
    assert_caller_is_owner = pt.Assert(option["owner"] == pt.Txn.sender())

    # Ensure the option is not for sale
    assert_option_not_for_sale = pt.Assert(option["for_sale"] == False)

    # Return the collateral to the owner
    return_collateral = pt.Txn.assets[0].transfer(option["collateral"], pt.Txn.sender(), option["collateral"])

    # Update option_list
    update_option_list = app.state.option_list_key.set(options_id, None)

    # Update creator_list
    update_creator_list = app.state.creator_list_key.set([option["creator"], options_id], None)

    # Update owner_list
    update_owner_list = app.state.owner_list_key.set([option["owner"], options_id], None)

    # Update market_list
    update_market_list = app.state.market_list_key.set(options_id, None)

    return pt.Seq(
        assert_initialized,
        assert_caller_is_owner,
        assert_option_not_for_sale,
        return_collateral,
        update_option_list,
        update_creator_list,
        update_owner_list,
        update_market_list
    )
# Helper function for transferring ownership
@pt.Subroutine 
def _internal_transfer(options_id: pt.Expr, new_owner: pt.Expr) -> pt.Expr:
    return transfer(options_id, new_owner)

# Helper function for listing an option for sale
@pt.Subroutine
def _internal_list_for_sale(options_id: pt.Expr, price: pt.Expr) -> pt.Expr:
    return list_for_sale(options_id, price)

# Helper function for buying an option
@pt.Subroutine
def _internal_buy(options_id: pt.Expr) -> pt.Expr:
    return buy(options_id)

# Helper function for burning an option
@pt.Subroutine
def _internal_burn(options_id: pt.Expr) -> pt.Expr:
    return burn(options_id)

# Helper function for executing an option
@pt.Subroutine
def _internal_execute_option(options_id: pt.Expr) -> pt.Expr:
    return execute_option(options_id)

# Helper function for claiming an expired option
@pt.Subroutine
def _internal_claim_expired(options_id: pt.Expr) -> pt.Expr:
    return claim_expired(options_id)

# Helper function for closing out an option
@pt.Subroutine
def _internal_close_out(options_id: pt.Expr) -> pt.Expr:
    return close_out(options_id)
