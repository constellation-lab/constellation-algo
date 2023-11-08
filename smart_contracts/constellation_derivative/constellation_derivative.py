
"""
import beaker
import pyteal as pt
from algokit_utils import DELETABLE_TEMPLATE_NAME, UPDATABLE_TEMPLATE_NAME

app = beaker.Application("constellation_derivative")


@app.update(authorize=beaker.Authorize.only_creator(), bare=True)
def update() -> pt.Expr:
    return pt.Assert(
        pt.Tmpl.Int(UPDATABLE_TEMPLATE_NAME),
        comment="Check app is updatable",
    )


@app.delete(authorize=beaker.Authorize.only_creator(), bare=True)
def delete() -> pt.Expr:
    return pt.Assert(
        pt.Tmpl.Int(DELETABLE_TEMPLATE_NAME),
        comment="Check app is deletable",
    )


@app.external
def hello(name: pt.abi.String, *, output: pt.abi.String) -> pt.Expr:
    return output.set(pt.Concat(pt.Bytes("Hello, "), name.get()))
---

import pyteal as pt
from beaker import Application

# Inside constellation_derivative.py
module_name = "constellation_derivative"
app = Application("constellation_derivative")
#app = beaker.Application("constellation_derivative")
# Global state
total_options = pt.App.globalGet(pt.Bytes("total_options"))
option_list = pt.App.globalGet(pt.Bytes("option_list"))
creator_list = pt.App.globalGet(pt.Bytes("creator_list"))
owner_list = pt.App.globalGet(pt.Bytes("owner_list"))
market_list = pt.App.globalGet(pt.Bytes("market_list"))

# Structs
Option = pt.Struct(
    "Option",
    [
        pt.Bytes("creator"),
        pt.Bytes("owner"),
        pt.Bytes("collateral"),
        pt.Bytes("counter_offer"),
        pt.Bytes("for_sale"),
        pt.Bytes("price"),
        pt.Bytes("expires"),
    ]
)

@app.on_startup()
def initialize():
    total_options.set(0)

# Create option
@app.stateful(read_only=False)
def create_option(counter_offer: pt.abi.Currency, expires: pt.abi.Timestamp):

  total = total_options.get() + 1
  new_option = Option.from_fields(
    pt.txn.sender(),
    pt.txn.sender(),
    pt.txn.assets[0],
    counter_offer,
    False,
    pt.zero(),
    expires
  )

  option_list[total] = new_option
  creator_list[pt.txn.sender(), total] = new_option
  owner_list[pt.txn.sender(), total] = new_option

  total_options.set(total)

# Rest of actions
# Transfer ownership
@app.stateful(read_only=False)
def transfer(option_id: pt.abi.UInt64, new_owner: pt.abi.Address):

  option = option_list[option_id]
  old_owner = option.owner

  option.owner = new_owner
  option_list[option_id] = option

  del owner_list[old_owner, option_id]
  owner_list[new_owner, option_id] = option

# Put option up for sale
@app.stateful(read_only=False)
def list_for_sale(option_id: pt.abi.UInt64, price: pt.abi.Currency):

  option = option_list[option_id]

  option.for_sale = True
  option.price = price

  option_list[option_id] = option
  market_list[option_id] = option

# Remove option from market
@app.stateful(read_only=False)
def remove_from_sale(option_id: pt.abi.UInt64):

  option = option_list[option_id]

  option.for_sale = False
  option.price = pt.zero()

  option_list[option_id] = option
  del market_list[option_id]

# Buy option
@app.stateful(read_only=False)
def buy(option_id: pt.abi.UInt64):

  seller = market_list[option_id].owner
  price = market_list[option_id].price

  market_list[option_id].owner = pt.txn.sender()
  del market_list[option_id]

  pt.transfer(price, seller)

# Execute option
@app.stateful(read_only=False)
def execute(option_id: pt.abi.UInt64):

  option = option_list[option_id]

  pt.transfer(option.counter_offer, option.creator)
  pt.transfer(option.collateral, pt.txn.sender())

  del option_list[option_id]
  del owner_list[option.owner, option_id]
  del creator_list[option.creator, option_id]

# Burn option
@app.stateful(read_only=False)
def burn(option_id: pt.abi.UInt64):

  option = option_list[option_id]

  pt.transfer(option.collateral, option.creator)

  del option_list[option_id]
  del owner_list[option.owner, option_id]
  del creator_list[option.creator, option_id]

# Claim expired
@app.stateful(read_only=False)
def claim_expired(option_id: pt.abi.UInt64):

  option = option_list[option_id]

  pt.transfer(option.collateral, option.creator)

  del option_list[option_id]
  del owner_list[option.owner, option_id]
  del creator_list[option.creator, option_id]
"""

import pyteal as pt
from beaker import Application

# Inside constellation_derivative.py
module_name = "constellation_derivative"
app = Application("constellation_derivative")

# Global state
total_options = pt.Int(0)
option_list = {}
creator_list = {}
owner_list = {}
market_list = {}

# Helper function to create option dict
def make_option(creator, owner, collateral, counter_offer, for_sale, price, expires):
    return {
        "creator": creator,
        "owner": owner,
        "collateral": collateral,
        "counter_offer": counter_offer,
        "for_sale": for_sale,
        "price": price,
        "expires": expires
    }

# Initialize global state variables
def initialize():
    total_options = pt.Int(0)

    option_list = {}
    creator_list = {}
    owner_list = {}
    market_list = {}

    pt.App.globalPut(pt.Bytes("total_options"), total_options)
    pt.App.globalPut(pt.Bytes("option_list"), option_list)
    pt.App.globalPut(pt.Bytes("creator_list"), creator_list)
    pt.App.globalPut(pt.Bytes("owner_list"), owner_list)
    pt.App.globalPut(pt.Bytes("market_list"), market_list)

# Create option
@app.action
def create_option(counter_offer, expires):

    total = pt.App.globalGet(pt.Bytes("total_options"))
    new_option = make_option(
        pt.txn.sender(),
        pt.txn.sender(),
        pt.txn.assets[0],
        counter_offer,
        False,
        pt.zero(),
        expires,
    )

    total = total + 1
    pt.App.globalPut(pt.Bytes("total_options"), total)

    option_list[total] = new_option
    creator_list[total] = new_option
    owner_list[total] = new_option

# Rest of actions
# Transfer ownership
@app.action
def transfer(option_id, new_owner):
    option = pt.App.globalGet(pt.Bytes("option_list"))[option_id]
    old_owner = option["owner"]
    option["owner"] = new_owner
    pt.App.globalPut(pt.Bytes("option_list"), option_list)
    pt.App.globalDel(pt.Bytes("owner_list"), (old_owner, option_id))
    pt.App.globalPut(pt.Bytes("owner_list"), (new_owner, option_id), option)

# Put option up for sale
@app.action
def list_for_sale(option_id, price):

    option = pt.App.globalGet(pt.Bytes("option_list"))[option_id]

    option["for_sale"] = True
    option["price"] = price

    pt.App.globalPut(pt.Bytes("option_list"), option_list)
    pt.App.globalPut(pt.Bytes("market_list"), market_list)

# Remove option from market
@app.action
def remove_from_sale(option_id):

    option = pt.App.globalGet(pt.Bytes("option_list"))[option_id]

    option["for_sale"] = False
    option["price"] = pt.zero()

    pt.App.globalPut(pt.Bytes("option_list"), option_list)
    pt.App.globalDel(pt.Bytes("market_list"), option_id)

# Buy option
@app.action
def buy(option_id):

    seller = pt.App.globalGet(pt.Bytes("market_list"))[option_id]["owner"]
    price = pt.App.globalGet(pt.Bytes("market_list"))[option_id]["price"]

    option = pt.App.globalGet(pt.Bytes("option_list"))[option_id]
    option["owner"] = pt.txn.sender()

    pt.App.globalPut(pt.Bytes("option_list"), option_list)
    pt.App.globalDel(pt.Bytes("market_list"), option_id)

    pt.transfer(price, seller)

# Execute option
@app.action
def execute(option_id):

    option = pt.App.globalGet(pt.Bytes("option_list"))[option_id]

    pt.transfer(option["counter_offer"], option["creator"])
    pt.transfer(option["collateral"], pt.txn.sender())

    pt.App.globalDel(pt.Bytes("option_list"), option_id)
    pt.App.globalDel(pt.Bytes("owner_list"), (option["owner"], option_id))
    pt.App.globalDel(pt.Bytes("creator_list"), (option["creator"], option_id))


# Burn option
@app.action
def burn(option_id):

    option = pt.App.globalGet(pt.Bytes("option_list"))[option_id]

    pt.transfer(option["collateral"], option["creator"])

    pt.App.globalDel(pt.Bytes("option_list"), option_id)
    pt.App.globalDel(pt.Bytes("owner_list"), (option["owner"], option_id))
    pt.App.globalDel(pt.Bytes("creator_list"), (option["creator"], option_id))



# Claim expired
@app.action
def claim_expired(option_id):

    option = pt.App.globalGet(pt.Bytes("option_list"))[option_id]

    pt.transfer(option["collateral"], option["creator"])

    pt.App.globalDel(pt.Bytes("option_list"), option_id)
    pt.App.globalDel(pt.Bytes("owner_list"), (option["owner"], option_id))
    pt.App.globalDel(pt.Bytes("creator_list"), (option["creator"], option_id))
