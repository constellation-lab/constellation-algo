import beaker
import pyteal as pt
import hashlib




class ConstellationDerivativeState:
    def __init__(self, app=None):
        self.app = app

    #global_state_key: This key is used to mark whether the global state is initialized. 
    # It is set to "initialized" when the contract is created to ensure that the global state 
    # has been properly initialized.
    #option_list_key: Used to store details of each option, such as its creator, owner, collateral, counter offer, etc.
    # creator_list_key: Keeps track of options created by each unique creator.
    # owner_list_key: Keeps track of options owned by each unique owner.
    # market_list_key: Keeps track of options that are listed on the market for sale.
    # Global State Data:
    # option_list_data: Stores the concatenated data of each option for easy retrieval.
    # creator_list_data: Stores the concatenated data of options created by each creator.
    # owner_list_data: Stores the concatenated data of options owned by each owner.
    # market_list_data: Stores the concatenated data of options listed on the market.
    # Options Properties:
    # new_owner: Represents the address of the new owner when an option is being transferred.
    # new_price: Represents the new price when an owner updates the list price of an option on the market.
    # collateral_price: Represents the price of the options.
    # expires_timestamp: Represents the timestamp of the end of the expiration period or expiration time of the option.
    # options_id: Represents the unique identifier (ID) of the option.
    # options_quantity: Represents the total quantity of the Asset/Asa/token associated with the option.
    # for_sale: Represents whether an option is currently listed for sale (0 if not for sale, 1 if for sale).
    # Local State:
    # claimable_amount: Represents the amount that an account can reclaim when an option expires.

        self.global_state_key = beaker.GlobalStateValue(pt.TealType.bytes, default=pt.Bytes(""))
        self.total_options_key = beaker.GlobalStateValue(pt.TealType.bytes, default=pt.Bytes(""))
        self.option_list_key = beaker.GlobalStateValue(pt.TealType.bytes, default=pt.Bytes(""))
        self.creator_list_key = beaker.GlobalStateValue(pt.TealType.bytes, default=pt.Bytes(""))
        self.owner_list_key = beaker.GlobalStateValue(pt.TealType.bytes, default=pt.Bytes(""))
        self.market_list_key = beaker.GlobalStateValue(pt.TealType.bytes, default=pt.Bytes(""))

        self.option_list_data = beaker.GlobalStateValue(pt.TealType.bytes, default=pt.Bytes(""))
        self.creator_list_data = beaker.GlobalStateValue(pt.TealType.bytes, default=pt.Bytes(""))
        self.owner_list_data = beaker.GlobalStateValue(pt.TealType.bytes, default=pt.Bytes(""))
        self.market_list_data = beaker.GlobalStateValue(pt.TealType.bytes, default=pt.Bytes(""))
    
 

     # Options Owner: Address of the Options Owner
        self.new_owner = beaker.GlobalStateValue(
            stack_type=pt.TealType.bytes, default=pt.Bytes("")
        )

     # Options price: price of the options
        self.new_price = beaker.GlobalStateValue(
            stack_type=pt.TealType.uint64, default=pt.Int(0)
        )

        # Collateral price: price of the options
        self.collateral_price = beaker.GlobalStateValue(
            stack_type=pt.TealType.uint64, default=pt.Int(0)
        )
    
     # Option Expires: Timestamp of the end of the expiry period
        self.expires_timestamp = beaker.GlobalStateValue(
             stack_type=pt.TealType.uint64, default=pt.Int(0)
        )

        self.options_id = beaker.GlobalStateValue(stack_type=pt.TealType.uint64, default=pt.Int(0))

    # ASA amount: Total amount of ASA / options being bought or sold
        self.options_quantity = beaker.GlobalStateValue(
            stack_type=pt.TealType.uint64, default=pt.Int(0)
        )
    #for sale defaults to 0 not for sale and 1 is for sale
        self.for_sale = beaker.GlobalStateValue(
            stack_type=pt.TealType.uint64, default=pt.Int(0)
        )

    ##################################
    # Local State
    # 16 key-value pairs per account
    # 128 bytes each
    # Users must opt in before using
    ##################################

    # Claimable amount: Amount of ALGO this account can reclaim when expired
        self.claimable_amount = beaker.LocalStateValue(
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
            return app.initialize_global_state()

"""
    # opt_into_asset method that opts the contract account into an ASA
        @app.external(authorize=beaker.Authorize.only(pt.Global.creator_address()))
        def opt_into_asset(asset: pt.abi.Asset) -> pt.Expr:
         # On-chain logic that uses multiple expressions, always goes in the returned Seq
            return pt.Seq(
        # Check the asa in state hasn't already been set
            pt.Assert(app.state.asa == pt.Int(0)),
        # Set app.state.asa to the asa being auctioned
            app.state.asa.set(asset.asset_id()),
        # Send the transaction to opt in
        # Opt == transfer of 0 amount from/to the same account
        # Send a 0 asset transfer, of asset, from contract to contract
            pt.InnerTxnBuilder.Execute(
                {
                pt.TxnField.type_enum: pt.TxnType.AssetTransfer,
                pt.TxnField.asset_receiver: pt.Global.current_application_address(),
                pt.TxnField.xfer_asset: asset.asset_id(),
                pt.TxnField.asset_amount: pt.Int(0),
                # Nomrally fees are 0.0001 ALGO
                # An inner transaction is 0.0001 ALGO
                # Setting inner transaction fee to 0, means outer fee must be 0.0002 ALGO
                pt.TxnField.fee: pt.Int(0),
            }
        ),
    )
"""

state = ConstellationDerivativeState()

#app = ConstellationDerivativeState()
#app = app.build(state)

#app = pt.App("ConstellationDerivative", state=ConstellationDerivativeState)

class ConstellationDerivativeContract(pt.App):
    def __init__(self, app, state):
        self.app = app
        self.state = state

   
    #state = ConstellationDerivativeState

       # app = beaker.Application("ConstellationDerivative", state=ConstellationDerivativeState)

    #app = YourApp()
    #contract.method = app.external(contract.method)

    # create method that initializes global state
        """   
        @self.app.create(bare=True)
        def create() -> pt.Expr:
            return pt.Seq(
                app.state.global_state_key.set(pt.Bytes("initialized")),  # Set the global state to initialized
                app.state.total_options_key.set(pt.Bytes("0")),  # Set total options to 0
        )
        """  
        @self.app.external
        def create_option(self, counter_offer: pt.abi.Uint64, expires_timestamp: pt.abi.Uint64) -> pt.Expr:
            # Ensure the global state is initialized
            assert_initialized = pt.Assert(self.state.global_state_key.get() == pt.Bytes("initialized"))

            # Increment total options
            current_total_options = self.state.total_options_key.get()
# create_option method that allows accounts to create an option
            new_total_options = pt.Add(pt.Btoi(current_total_options), pt.Int(1))

        # Convert new_total_options to bytes
            new_total_options_bytes = pt.Itob(new_total_options)
            incremented_total_options = self.state.total_options_key.set(new_total_options_bytes)

        # Create the new option
            new_option_id = new_total_options
            new_option_id_bytes = pt.Itob(new_option_id)  # Convert new_option_id to bytes

            new_option = self.state.make_option(
                pt.Txn.sender(),
                pt.Txn.sender(),
                pt.Txn.assets[0],
                counter_offer,
                pt.Btoi(pt.BytesZero),#app.state.for_sale,
                pt.BytesZero,  # Use pt.BytesZero instead of pt.Global.zero
                expires_timestamp,
             )

        # Ensure new_option_id_bytes is in bytes format
            if not isinstance(new_option_id_bytes, bytes):
                new_option_id_bytes = str(new_option_id_bytes).encode()

        # option_list_data: Stores the concatenated data of each option for easy retrieval.

        # String format for concatenation
            concatenated_data = "{}:{}:{}:{}:{}:{}:{}:{}".format(
                new_option_id_bytes,  # Ensure this is in bytes
                new_option["creator"],
                new_option["owner"],
                new_option["collateral"],
                new_option["counter_offer"],
                new_option["for_sale"],
                new_option["price"],
                new_option["expires"]
            )

        # Use SHA-256 hash function
            hashed_key = hashlib.sha256(concatenated_data.encode()).hexdigest()

        # option_list_key: Used to store details of each option, such as its creator, owner, collateral, counter offer, etc.
        # creator_list_key: Keeps track of options created by each unique creator.
        # owner_list_key: Keeps track of options owned by each unique owner.

        # Update option_list with hashed key
            update_option_list = self.state.option_list_key.set(pt.Bytes(hashed_key.encode()))
    
        # Update option_data with full concatenated data
            self.state.option_list_data.set(pt.Bytes(concatenated_data.encode()))

        # Concatenate values for owner_list and creator_list
            owner_concatenated_data = "{}:{}:{}".format(
                new_option["owner"],
                new_option_id_bytes.decode(),
                new_option_id_bytes
            )

            creator_concatenated_data = "{}:{}:{}".format(
                new_option["creator"],
                new_option_id_bytes.decode(),
                new_option_id_bytes
            )

        # creator_list_data: Stores the concatenated data of options created by each creator.
        # owner_list_data: Stores the concatenated data of options owned by 

        # Use SHA-256 hash function
            owner_hashed_key = hashlib.sha256(owner_concatenated_data.encode()).hexdigest()
            creator_hashed_key = hashlib.sha256(creator_concatenated_data.encode()).hexdigest()

        # Update owner_list with hashed key
            update_owner_list = self.state.owner_list_key.set(pt.Bytes(owner_hashed_key.encode()))
    
        # Update owner_data with full concatenated data
            self.state.owner_list_data.set(pt.Bytes(owner_concatenated_data.encode()))

        # Update creator_list with hashed key
            update_creator_list = self.state.creator_list_key.set(pt.Bytes(creator_hashed_key.encode()))
    
        # Update creator_data with full concatenated data
            self.state.creator_list_data.set(pt.Bytes(creator_concatenated_data.encode()))

        # Combine all assignments in a Seq
            return pt.Seq(
                assert_initialized,
                incremented_total_options,
                update_option_list,
                update_owner_list,
                update_creator_list
            )

        def transfer_logic(self, options_id: pt.Expr, new_owner: pt.Expr) -> pt.Expr:
            assert_initialized = pt.Assert(self.state.global_state_key.get() == pt.Bytes("initialized"))
            option = self.state.option_list_key[options_id]
            assert_caller_is_owner = pt.Assert(option["owner"] == pt.Txn.sender())
            combined_operations = pt.Seq(
                assert_caller_is_owner,
            )
            return pt.Seq(
                assert_initialized,
                combined_operations
                ), pt.Int(1)

        @self.app.update
        def update_option(self, options_id, option, new_owner):
            option["owner"] = new_owner
            return self.state.option_list_key[options_id].set(option)

        @self.app.external
        def transfer(self, options_id: pt.Expr, new_owner: pt.Expr) -> pt.Expr:
            return self.transfer_logic(options_id, new_owner)


    # list_for_sale method that puts an option up for sale
        @self.app.external
        def list_for_sale(self, options_id: pt.Expr, price: pt.Expr) -> pt.Expr:
    # Ensure the global state is initialized
            assert_initialized = pt.Assert(self.state.global_state_key.get() == pt.Bytes("initialized"))

    # Get the option
            option = self.state.option_list_key[options_id]

    # Ensure the caller is the current owner
            assert_caller_is_owner = pt.Assert(option["owner"] == pt.Txn.sender())

    # Update option
            option["for_sale"] = 1 #True
            option["price"] = price

    # Update option_list
            update_option_list = self.state.option_list_key[options_id] = option

    # Update market_list
            update_market_list = self.state.market_list_key[options_id] = option

            return pt.Seq(
                assert_initialized,
                assert_caller_is_owner,
                update_option_list,
                update_market_list
            )


# remove_from_sale method that removes an option from the market
        @self.app.external
        def remove_from_sale(self, options_id: pt.Expr) -> pt.Expr:
    # Ensure the global state is initialized
            assert_initialized = pt.Assert(self.state.global_state_key.get() == pt.Bytes("initialized"))

    # Get the option
            option = self.state.option_list_key[options_id]

    # Ensure the caller is the current owner
            assert_caller_is_owner = pt.Assert(option["owner"] == pt.Txn.sender())

    # Update option
            option["for_sale"] = 0 #false
            option["price"] = pt.BytesZero

    # Update option_list
            update_option_list = self.state.option_list_key[options_id] = option

        # Update market_list
            update_market_list = self.state.market_list_key[options_id] = None

            return pt.Seq(
                assert_initialized,
                assert_caller_is_owner,
                update_option_list,
                update_market_list
            )


# buy method that allows buying an option from the market
        @self.app.external
        def buy(self, options_id: pt.Expr) -> pt.Expr:
    # Ensure the global state is initialized
            assert_initialized = pt.Assert(self.state.global_state_key.get() == pt.Bytes("initialized"))

    # Get the option
            option = self.state.option_list_key[options_id]

    # Ensure the option is for sale
            assert_option_for_sale = pt.Assert(option["for_sale"] == True)

    # Ensure the buyer has enough balance
            assert_buyer_has_enough_balance = pt.Assert(pt.Txn.sender() == option["owner"])

    # Transfer the collateral to the buyer
            transfer_collateral = pt.Txn.assets[0].transfer(option["collateral"], option["owner"], option["price"])

    # Transfer ownership
            option["owner"] = pt.Txn.sender()

    # Up date option
            option["for_sale"] = 0 #False
            option["price"] = pt.zero()

    # Update option_list
            update_option_list = self.state.option_list_key[options_id] = option

    # Update owner_list
            update_owner_list_sender = self.state.owner_list_key[pt.Txn.sender(), options_id] = option
            update_owner_list_owner = self.state.owner_list_key[option["owner"], options_id] = None

    # Update market_list
            update_market_list = self.state.market_list_key[options_id] = None

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

# Initialize the global state key, assuming it's not done elsewhere
#app.global_state.key(pt.Bytes("initialized"))

# Helper function with the logic
        @self.app.external
        def update_price_logic(self, options_id: pt.Expr, price: pt.Expr) -> pt.Expr:
    # Ensure the global state is initialized
            assert_initialized = pt.Assert(self.state.global_state_key.get() == pt.Bytes("initialized"))

    # Get the option from local state using options_id
            unset_option = pt.Unset("option", self.localGet(options_id))

    # Ensure the caller is the current owner of the option
            assert_owner = pt.Assert(pt.Ref("option")["owner"] == pt.Txn.sender())

    # Update the price of the option using .set
            update_price_expr = pt.Ref("option").set(pt.Str("price"), price)

    # Update the local state with the modified option
            update_local_state = self.localPut(options_id, pt.Ref("option"))

            return pt.Seq(
                assert_initialized,
                unset_option,
                assert_owner,
                update_price_expr,
                update_local_state
            )

# Manually construct the ABI for update_price_logic
        abi_update_price_logic = {
    "functions": [
        {
            "name": "update_price_logic",
            "arguments": [
                {"name": "options_id", "type": "uint64"},
                {"name": "price", "type": "uint64"},
            ],
            "returns": [
                {"name": "", "type": "int"}
            ],
        }
    ]
}


# External function to be called by the user
        @self.app.external
        def update_price(options_id: pt.Expr, price: pt.Expr) -> pt.Expr:
    # Call the logic function
            return update_price_logic(options_id, price)




# burn method that allows burning an option
        @self.app.external
        def burn(self, options_id: pt.Expr) -> pt.Expr:
    # Ensure the global state is initialized
            assert_initialized = pt.Assert(self.state.global_state_key.get() == pt.Bytes("initialized"))

    # Get the option
            option = self.state.option_list_key[options_id]

    # Ensure the caller is the current owner
            assert_caller_is_owner = pt.Assert(option["owner"] == pt.Txn.sender())

    # Transfer the collateral to the contract creator
            transfer_collateral = pt.Txn.assets[0].transfer(option["collateral"], self.creator_address, option["collateral"])

    # Update option_list
            update_option_list = self.state.option_list_key[options_id] = None

    # Update creator_list
            update_creator_list = self.state.creator_list_key[option["creator"], options_id] = None

    # Update owner_list
            update_owner_list = self.state.owner_list_key[option["owner"], options_id] = None

    # Update market_list
            update_market_list = self.state.market_list_key[options_id] = None

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
        @self.app.external
        def claim_expired(self, options_id: pt.Expr) -> pt.Expr:
    # Ensure the global state is initialized
            assert_initialized = pt.Assert(self.state.global_state_key.get() == pt.Bytes("initialized"))

    # Get the option
            option = self.state.option_list_key.get(options_id)

    # Ensure the option is expired
            assert_option_expired = pt.Assert(pt.Txn.group_index() > option["expires"])

    # Ensure the caller is the current owner
            assert_caller_is_owner = pt.Assert(option["owner"] == pt.Txn.sender())

    # Transfer the collateral to the owner
            transfer_collateral = pt.Txn.assets[0].transfer(option["collateral"], pt.Txn.sender(), option["collateral"])

    # Update option_list
            update_option_list = self.state.option_list_key.set(options_id, None)

    # Update creator_list
            update_creator_list = self.state.creator_list_key.set([option["creator"], options_id], None)

    # Update owner_list
            update_owner_list = self.state.owner_list_key.set([option["owner"], options_id], None)

    # Update market_list
            update_market_list = self.state.market_list_key.set(options_id, None)

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
        @self.app.external
        def execute_option(self, options_id: pt.Expr) -> pt.Expr:
    #   Ensure the global state is initialized
            assert_initialized = pt.Assert(self.state.global_state_key.get() == pt.Bytes("initialized"))

    # Get the option
            option = self.state.option_list_key.get(options_id)

    # Ensure the caller is the current owner
            assert_caller_is_owner = pt.Assert(option["owner"] == pt.Txn.sender())

    # Ensure the option is not for sale
            assert_option_not_for_sale = pt.Assert(option["for_sale"] == False)

    # Transfer the collateral to the contract creator
            transfer_collateral = pt.Txn.assets[0].transfer(option["collateral"], self.creator_address, option["collateral"])

    # Update option_list
            update_option_list = self.state.option_list_key.set(options_id, None)

    # Update creator_list
            update_creator_list = self.state.creator_list_key.set([option["creator"], options_id], None)

    # Update owner_list
            update_owner_list = self.state.owner_list_key.set([option["owner"], options_id], None)

    # Update market_list
            update_market_list = self.state.market_list_key.set(options_id, None)

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
        @self.app.external
        def close_out(self, options_id: pt.Expr) -> pt.Expr:
    # Ensure the global state is initialized
            assert_initialized = pt.Assert(self.state.global_state_key.get() == pt.Bytes("initialized"))

    # Get the option
            option = self.state.option_list_key.get(options_id)

    # Ensure the caller is the current owner
            assert_caller_is_owner = pt.Assert(option["owner"] == pt.Txn.sender())

    # Ensure the option is not for sale
            assert_option_not_for_sale = pt.Assert(option["for_sale"] == False)

    # Return the collateral to the owner
            return_collateral = pt.Txn.assets[0].transfer(option["collateral"], pt.Txn.sender(), option["collateral"])

    # Update option_list
            update_option_list = self.state.option_list_key.set(options_id, None)

    # Update creator_list
            update_creator_list = self.state.creator_list_key.set([option["creator"], options_id], None)

    # Update owner_list
            update_owner_list = self.state.owner_list_key.set([option["owner"], options_id], None)

    # Update market_list
            update_market_list = self.state.market_list_key.set(options_id, None)

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


# Add a method to retrieve the option ID from global state
        @self.app.external
        def get_option_id(self) -> pt.Expr:
            return self.state.options_id


# get_option method that allows querying an option
        @self.app.external
        def get_option(self,option_id: pt.Expr) -> pt.Expr:
            return self.state.option_list_key[option_id]

# get_options_by_creator method that allows querying options by creator
        @self.app.external
        def get_options_by_creator(self, creator: pt.Expr) -> pt.Expr:
            return self.state.creator_list_key.prefix(creator)

# get_options_by_owner method that allows querying options by owner
        @self.app.external
        def get_options_by_owner(self, owner: pt.Expr) -> pt.Expr:
            return self.state.owner_list_key.prefix(owner)

# get_options_on_market method that allows querying options on the market
        @self.app.external
        def get_options_on_market(self) -> pt.Expr:
            return self.state.market_list_key.filter()

# get_total_options method that allows querying the total number of options
        @self.app.external
        def get_total_options(self) -> pt.Expr:
            return self.state.total_options_key

# get_expired_options method that allows querying expired options
        @self.app.external
        def get_expired_options(self, current_time: pt.Expr) -> pt.Expr:    
            return self.state.option_list_key.filter(lambda k, v: v["expires"] < current_time)

# get_options_for_sale method that allows querying options that are for sale
        @self.app.external
        def get_options_for_sale(self) -> pt.Expr:
            return self.state.option_list_key.filter(lambda k, v: v["for_sale"] == True)


# if __name__ == "__main__":
# spec = app.build()
# spec.export("artifacts")

#app = beaker.Application("ConstellationDerivative", state=ConstellationDerivativeState)
 # State 
#state = ConstellationDerivativeState(app=None)  

# Contract
contract = ConstellationDerivativeContract( app=pt.App, state=state)

# Build app
app = contract.build(state)

#state.app = app

#contract.app = app

__all__ = ['app']

if __name__ == "__main__":
 

    
        
      
 """   
    if os.path.exists("approval.teal"):
        os.remove("approval.teal")

    if os.path.exists("clear.teal"):
        os.remove("clear.teal")

    if os.path.exists("abi.json"):
        os.remove("abi.json")

    if os.path.exists("app_spec.json"):
        os.remove("app_spec.json")

    with open("approval.teal", "w") as f:
        f.write(app.approval_program)

    with open("clear.teal", "w") as f:
        f.write(app.clear_program)

    with open("abi.json", "w") as f:
        f.write(json.dumps(app.contract.dictify(), indent=4))

    with open("app_spec.json", "w") as f:
        f.write(json.dumps(app.application_spec(), indent=4))
    
"""
