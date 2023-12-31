# flake8: noqa
# fmt: off
# mypy: disable-error-code="no-any-return, no-untyped-call"
# This file was automatically generated by algokit-client-generator.
# DO NOT MODIFY IT BY HAND.
# requires: algokit-utils@^1.2.0
import base64
import dataclasses
import decimal
import typing
from abc import ABC, abstractmethod

import algokit_utils
import algosdk
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    AtomicTransactionResponse,
    TransactionSigner,
    TransactionWithSigner
)

_APP_SPEC_JSON = r"""{
    "hints": {
        "create_option(uint64,uint64)void": {
            "call_config": {
                "no_op": "CALL"
            }
        }
    },
    "source": {
        "approval": "I3ByYWdtYSB2ZXJzaW9uIDgKaW50Y2Jsb2NrIDAgMQpieXRlY2Jsb2NrIDB4NzQ2Zjc0NjE2YzVmNmY3MDc0Njk2ZjZlNzM1ZjZiNjU3OSAweDY3NmM2ZjYyNjE2YzVmNzM3NDYxNzQ2NTVmNmI2NTc5IDB4Njk2ZTY5NzQ2OTYxNmM2OTdhNjU2NCAweDM4MzEzODY0NjYzODM5MzkzMDM5MzgzNjY0MzIzODYxMzUzMDY1MzYzNzMxMzEzMTMwNjUzMjYyMzM2MzY2MzUzNTY0NjU2MzM2NjI2NDYyMzUzMzYyMzE2NjYyMzczNDMxNjUzODYzNjMzMDYyMzQzMDM0MzYzOTY1NjM2NDM3CnR4biBOdW1BcHBBcmdzCmludGNfMCAvLyAwCj09CmJueiBtYWluX2w0CnR4bmEgQXBwbGljYXRpb25BcmdzIDAKcHVzaGJ5dGVzIDB4N2FlOTUzNmMgLy8gImNyZWF0ZV9vcHRpb24odWludDY0LHVpbnQ2NCl2b2lkIgo9PQpibnogbWFpbl9sMwplcnIKbWFpbl9sMzoKdHhuIE9uQ29tcGxldGlvbgppbnRjXzAgLy8gTm9PcAo9PQp0eG4gQXBwbGljYXRpb25JRAppbnRjXzAgLy8gMAohPQomJgphc3NlcnQKY2FsbHN1YiBjcmVhdGVvcHRpb25jYXN0ZXJfMgppbnRjXzEgLy8gMQpyZXR1cm4KbWFpbl9sNDoKdHhuIE9uQ29tcGxldGlvbgppbnRjXzAgLy8gTm9PcAo9PQpibnogbWFpbl9sNgplcnIKbWFpbl9sNjoKdHhuIEFwcGxpY2F0aW9uSUQKaW50Y18wIC8vIDAKPT0KYXNzZXJ0CmNhbGxzdWIgY3JlYXRlXzAKaW50Y18xIC8vIDEKcmV0dXJuCgovLyBjcmVhdGUKY3JlYXRlXzA6CnByb3RvIDAgMApieXRlY18xIC8vICJnbG9iYWxfc3RhdGVfa2V5IgpieXRlY18yIC8vICJpbml0aWFsaXplZCIKYXBwX2dsb2JhbF9wdXQKYnl0ZWNfMCAvLyAidG90YWxfb3B0aW9uc19rZXkiCnB1c2hieXRlcyAweDMwIC8vICIwIgphcHBfZ2xvYmFsX3B1dApyZXRzdWIKCi8vIGNyZWF0ZV9vcHRpb24KY3JlYXRlb3B0aW9uXzE6CnByb3RvIDIgMApieXRlY18xIC8vICJnbG9iYWxfc3RhdGVfa2V5IgphcHBfZ2xvYmFsX2dldApieXRlY18yIC8vICJpbml0aWFsaXplZCIKPT0KYXNzZXJ0CmJ5dGVjXzAgLy8gInRvdGFsX29wdGlvbnNfa2V5IgpieXRlY18wIC8vICJ0b3RhbF9vcHRpb25zX2tleSIKYXBwX2dsb2JhbF9nZXQKYnRvaQppbnRjXzEgLy8gMQorCml0b2IKYXBwX2dsb2JhbF9wdXQKcHVzaGJ5dGVzIDB4NmY3MDc0Njk2ZjZlNWY2YzY5NzM3NDVmNmI2NTc5IC8vICJvcHRpb25fbGlzdF9rZXkiCnB1c2hieXRlcyAweDM1NjIzODM2MzUzMjM1NjUzMDMzNjIzMzMwMzczNDM3MzI2MzM3Mzg2NTMxNjM2NDM5MzIzNDMxMzkzNjM3NjIzMzY2MzIzMzM2NjEzNzM5MzIzOTM4MzQzMTM5MzE2MjY2MzIzMjMyMzQ2MzYyMzUzODM2NjU2NDYzNjIzNDM4IC8vIDB4MzU2MjM4MzYzNTMyMzU2NTMwMzM2MjMzMzAzNzM0MzczMjYzMzczODY1MzE2MzY0MzkzMjM0MzEzOTM2Mzc2MjMzNjYzMjMzMzY2MTM3MzkzMjM5MzgzNDMxMzkzMTYyNjYzMjMyMzIzNDYzNjIzNTM4MzY2NTY0NjM2MjM0MzgKYXBwX2dsb2JhbF9wdXQKcHVzaGJ5dGVzIDB4NmY3NzZlNjU3MjVmNmM2OTczNzQ1ZjZiNjU3OSAvLyAib3duZXJfbGlzdF9rZXkiCmJ5dGVjXzMgLy8gMHgzODMxMzg2NDY2MzgzOTM5MzAzOTM4MzY2NDMyMzg2MTM1MzA2NTM2MzczMTMxMzEzMDY1MzI2MjMzNjM2NjM1MzU2NDY1NjMzNjYyNjQ2MjM1MzM2MjMxNjY2MjM3MzQzMTY1Mzg2MzYzMzA2MjM0MzAzNDM2Mzk2NTYzNjQzNwphcHBfZ2xvYmFsX3B1dApwdXNoYnl0ZXMgMHg2MzcyNjU2MTc0NmY3MjVmNmM2OTczNzQ1ZjZiNjU3OSAvLyAiY3JlYXRvcl9saXN0X2tleSIKYnl0ZWNfMyAvLyAweDM4MzEzODY0NjYzODM5MzkzMDM5MzgzNjY0MzIzODYxMzUzMDY1MzYzNzMxMzEzMTMwNjUzMjYyMzM2MzY2MzUzNTY0NjU2MzM2NjI2NDYyMzUzMzYyMzE2NjYyMzczNDMxNjUzODYzNjMzMDYyMzQzMDM0MzYzOTY1NjM2NDM3CmFwcF9nbG9iYWxfcHV0CnJldHN1YgoKLy8gY3JlYXRlX29wdGlvbl9jYXN0ZXIKY3JlYXRlb3B0aW9uY2FzdGVyXzI6CnByb3RvIDAgMAppbnRjXzAgLy8gMApkdXAKdHhuYSBBcHBsaWNhdGlvbkFyZ3MgMQpidG9pCmZyYW1lX2J1cnkgMAp0eG5hIEFwcGxpY2F0aW9uQXJncyAyCmJ0b2kKZnJhbWVfYnVyeSAxCmZyYW1lX2RpZyAwCmZyYW1lX2RpZyAxCmNhbGxzdWIgY3JlYXRlb3B0aW9uXzEKcmV0c3Vi",
        "clear": "I3ByYWdtYSB2ZXJzaW9uIDgKcHVzaGludCAwIC8vIDAKcmV0dXJu"
    },
    "state": {
        "global": {
            "num_byte_slices": 11,
            "num_uints": 6
        },
        "local": {
            "num_byte_slices": 0,
            "num_uints": 1
        }
    },
    "schema": {
        "global": {
            "declared": {
                "collateral_price": {
                    "type": "uint64",
                    "key": "collateral_price",
                    "descr": ""
                },
                "creator_list_data": {
                    "type": "bytes",
                    "key": "creator_list_data",
                    "descr": ""
                },
                "creator_list_key": {
                    "type": "bytes",
                    "key": "creator_list_key",
                    "descr": ""
                },
                "expires_timestamp": {
                    "type": "uint64",
                    "key": "expires_timestamp",
                    "descr": ""
                },
                "for_sale": {
                    "type": "uint64",
                    "key": "for_sale",
                    "descr": ""
                },
                "global_state_key": {
                    "type": "bytes",
                    "key": "global_state_key",
                    "descr": ""
                },
                "market_list_data": {
                    "type": "bytes",
                    "key": "market_list_data",
                    "descr": ""
                },
                "market_list_key": {
                    "type": "bytes",
                    "key": "market_list_key",
                    "descr": ""
                },
                "new_owner": {
                    "type": "bytes",
                    "key": "new_owner",
                    "descr": ""
                },
                "new_price": {
                    "type": "uint64",
                    "key": "new_price",
                    "descr": ""
                },
                "option_list_data": {
                    "type": "bytes",
                    "key": "option_list_data",
                    "descr": ""
                },
                "option_list_key": {
                    "type": "bytes",
                    "key": "option_list_key",
                    "descr": ""
                },
                "options_id": {
                    "type": "uint64",
                    "key": "options_id",
                    "descr": ""
                },
                "options_quantity": {
                    "type": "uint64",
                    "key": "options_quantity",
                    "descr": ""
                },
                "owner_list_data": {
                    "type": "bytes",
                    "key": "owner_list_data",
                    "descr": ""
                },
                "owner_list_key": {
                    "type": "bytes",
                    "key": "owner_list_key",
                    "descr": ""
                },
                "total_options_key": {
                    "type": "bytes",
                    "key": "total_options_key",
                    "descr": ""
                }
            },
            "reserved": {}
        },
        "local": {
            "declared": {
                "claimable_amount": {
                    "type": "uint64",
                    "key": "claimable_amount",
                    "descr": ""
                }
            },
            "reserved": {}
        }
    },
    "contract": {
        "name": "ConstellationDerivative",
        "methods": [
            {
                "name": "create_option",
                "args": [
                    {
                        "type": "uint64",
                        "name": "counter_offer"
                    },
                    {
                        "type": "uint64",
                        "name": "expires_timestamp"
                    }
                ],
                "returns": {
                    "type": "void"
                }
            }
        ],
        "networks": {}
    },
    "bare_call_config": {
        "no_op": "CREATE"
    }
}"""
APP_SPEC = algokit_utils.ApplicationSpecification.from_json(_APP_SPEC_JSON)
_TReturn = typing.TypeVar("_TReturn")


class _ArgsBase(ABC, typing.Generic[_TReturn]):
    @staticmethod
    @abstractmethod
    def method() -> str:
        ...


_TArgs = typing.TypeVar("_TArgs", bound=_ArgsBase[typing.Any])


@dataclasses.dataclass(kw_only=True)
class _TArgsHolder(typing.Generic[_TArgs]):
    args: _TArgs


def _filter_none(value: dict | typing.Any) -> dict | typing.Any:
    if isinstance(value, dict):
        return {k: _filter_none(v) for k, v in value.items() if v is not None}
    return value


def _as_dict(data: typing.Any, *, convert_all: bool = True) -> dict[str, typing.Any]:
    if data is None:
        return {}
    if not dataclasses.is_dataclass(data):
        raise TypeError(f"{data} must be a dataclass")
    if convert_all:
        result = dataclasses.asdict(data)
    else:
        result = {f.name: getattr(data, f.name) for f in dataclasses.fields(data)}
    return _filter_none(result)


def _convert_transaction_parameters(
    transaction_parameters: algokit_utils.TransactionParameters | None,
) -> algokit_utils.TransactionParametersDict:
    return typing.cast(algokit_utils.TransactionParametersDict, _as_dict(transaction_parameters))


def _convert_call_transaction_parameters(
    transaction_parameters: algokit_utils.TransactionParameters | None,
) -> algokit_utils.OnCompleteCallParametersDict:
    return typing.cast(algokit_utils.OnCompleteCallParametersDict, _as_dict(transaction_parameters))


def _convert_create_transaction_parameters(
    transaction_parameters: algokit_utils.TransactionParameters | None,
    on_complete: algokit_utils.OnCompleteActionName,
) -> algokit_utils.CreateCallParametersDict:
    result = typing.cast(algokit_utils.CreateCallParametersDict, _as_dict(transaction_parameters))
    on_complete_enum = on_complete.replace("_", " ").title().replace(" ", "") + "OC"
    result["on_complete"] = getattr(algosdk.transaction.OnComplete, on_complete_enum)
    return result


def _convert_deploy_args(
    deploy_args: algokit_utils.DeployCallArgs | None,
) -> algokit_utils.ABICreateCallArgsDict | None:
    if deploy_args is None:
        return None

    deploy_args_dict = typing.cast(algokit_utils.ABICreateCallArgsDict, _as_dict(deploy_args))
    if isinstance(deploy_args, _TArgsHolder):
        deploy_args_dict["args"] = _as_dict(deploy_args.args)
        deploy_args_dict["method"] = deploy_args.args.method()

    return deploy_args_dict


@dataclasses.dataclass(kw_only=True)
class CreateOptionArgs(_ArgsBase[None]):
    counter_offer: int
    expires_timestamp: int

    @staticmethod
    def method() -> str:
        return "create_option(uint64,uint64)void"


class ByteReader:
    def __init__(self, data: bytes):
        self._data = data

    @property
    def as_bytes(self) -> bytes:
        return self._data

    @property
    def as_str(self) -> str:
        return self._data.decode("utf8")

    @property
    def as_base64(self) -> str:
        return base64.b64encode(self._data).decode("utf8")

    @property
    def as_hex(self) -> str:
        return self._data.hex()


class GlobalState:
    def __init__(self, data: dict[bytes, bytes | int]):
        self.collateral_price = typing.cast(int, data.get(b"collateral_price"))
        self.creator_list_data = ByteReader(typing.cast(bytes, data.get(b"creator_list_data")))
        self.creator_list_key = ByteReader(typing.cast(bytes, data.get(b"creator_list_key")))
        self.expires_timestamp = typing.cast(int, data.get(b"expires_timestamp"))
        self.for_sale = typing.cast(int, data.get(b"for_sale"))
        self.global_state_key = ByteReader(typing.cast(bytes, data.get(b"global_state_key")))
        self.market_list_data = ByteReader(typing.cast(bytes, data.get(b"market_list_data")))
        self.market_list_key = ByteReader(typing.cast(bytes, data.get(b"market_list_key")))
        self.new_owner = ByteReader(typing.cast(bytes, data.get(b"new_owner")))
        self.new_price = typing.cast(int, data.get(b"new_price"))
        self.option_list_data = ByteReader(typing.cast(bytes, data.get(b"option_list_data")))
        self.option_list_key = ByteReader(typing.cast(bytes, data.get(b"option_list_key")))
        self.options_id = typing.cast(int, data.get(b"options_id"))
        self.options_quantity = typing.cast(int, data.get(b"options_quantity"))
        self.owner_list_data = ByteReader(typing.cast(bytes, data.get(b"owner_list_data")))
        self.owner_list_key = ByteReader(typing.cast(bytes, data.get(b"owner_list_key")))
        self.total_options_key = ByteReader(typing.cast(bytes, data.get(b"total_options_key")))


class LocalState:
    def __init__(self, data: dict[bytes, bytes | int]):
        self.claimable_amount = typing.cast(int, data.get(b"claimable_amount"))


class Composer:

    def __init__(self, app_client: algokit_utils.ApplicationClient, atc: AtomicTransactionComposer):
        self.app_client = app_client
        self.atc = atc

    def build(self) -> AtomicTransactionComposer:
        return self.atc

    def execute(self) -> AtomicTransactionResponse:
        return self.app_client.execute_atc(self.atc)

    def create_option(
        self,
        *,
        counter_offer: int,
        expires_timestamp: int,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
    ) -> "Composer":
        """Adds a call to `create_option(uint64,uint64)void` ABI method
        
        :param int counter_offer: The `counter_offer` ABI parameter
        :param int expires_timestamp: The `expires_timestamp` ABI parameter
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns Composer: This Composer instance"""

        args = CreateOptionArgs(
            counter_offer=counter_offer,
            expires_timestamp=expires_timestamp,
        )
        self.app_client.compose_call(
            self.atc,
            call_abi_method=args.method(),
            transaction_parameters=_convert_call_transaction_parameters(transaction_parameters),
            **_as_dict(args, convert_all=True),
        )
        return self

    def create_bare(
        self,
        *,
        on_complete: typing.Literal["no_op"] = "no_op",
        transaction_parameters: algokit_utils.CreateTransactionParameters | None = None,
    ) -> "Composer":
        """Adds a call to create an application using the no_op bare method
        
        :param typing.Literal[no_op] on_complete: On completion type to use
        :param algokit_utils.CreateTransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns Composer: This Composer instance"""

        self.app_client.compose_create(
            self.atc,
            call_abi_method=False,
            transaction_parameters=_convert_create_transaction_parameters(transaction_parameters, on_complete),
        )
        return self

    def clear_state(
        self,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
        app_args: list[bytes] | None = None,
    ) -> "Composer":
        """Adds a call to the application with on completion set to ClearState
    
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :param list[bytes] | None app_args: (optional) Application args to pass"""
    
        self.app_client.compose_clear_state(self.atc, _convert_transaction_parameters(transaction_parameters), app_args)
        return self


class ConstellationDerivativeClient:
    """A class for interacting with the ConstellationDerivative app providing high productivity and
    strongly typed methods to deploy and call the app"""

    @typing.overload
    def __init__(
        self,
        algod_client: algosdk.v2client.algod.AlgodClient,
        *,
        app_id: int = 0,
        signer: TransactionSigner | algokit_utils.Account | None = None,
        sender: str | None = None,
        suggested_params: algosdk.transaction.SuggestedParams | None = None,
        template_values: algokit_utils.TemplateValueMapping | None = None,
        app_name: str | None = None,
    ) -> None:
        ...

    @typing.overload
    def __init__(
        self,
        algod_client: algosdk.v2client.algod.AlgodClient,
        *,
        creator: str | algokit_utils.Account,
        indexer_client: algosdk.v2client.indexer.IndexerClient | None = None,
        existing_deployments: algokit_utils.AppLookup | None = None,
        signer: TransactionSigner | algokit_utils.Account | None = None,
        sender: str | None = None,
        suggested_params: algosdk.transaction.SuggestedParams | None = None,
        template_values: algokit_utils.TemplateValueMapping | None = None,
        app_name: str | None = None,
    ) -> None:
        ...

    def __init__(
        self,
        algod_client: algosdk.v2client.algod.AlgodClient,
        *,
        creator: str | algokit_utils.Account | None = None,
        indexer_client: algosdk.v2client.indexer.IndexerClient | None = None,
        existing_deployments: algokit_utils.AppLookup | None = None,
        app_id: int = 0,
        signer: TransactionSigner | algokit_utils.Account | None = None,
        sender: str | None = None,
        suggested_params: algosdk.transaction.SuggestedParams | None = None,
        template_values: algokit_utils.TemplateValueMapping | None = None,
        app_name: str | None = None,
    ) -> None:
        """
        ConstellationDerivativeClient can be created with an app_id to interact with an existing application, alternatively
        it can be created with a creator and indexer_client specified to find existing applications by name and creator.
        
        :param AlgodClient algod_client: AlgoSDK algod client
        :param int app_id: The app_id of an existing application, to instead find the application by creator and name
        use the creator and indexer_client parameters
        :param str | Account creator: The address or Account of the app creator to resolve the app_id
        :param IndexerClient indexer_client: AlgoSDK indexer client, only required if deploying or finding app_id by
        creator and app name
        :param AppLookup existing_deployments:
        :param TransactionSigner | Account signer: Account or signer to use to sign transactions, if not specified and
        creator was passed as an Account will use that.
        :param str sender: Address to use as the sender for all transactions, will use the address associated with the
        signer if not specified.
        :param TemplateValueMapping template_values: Values to use for TMPL_* template variables, dictionary keys should
        *NOT* include the TMPL_ prefix
        :param str | None app_name: Name of application to use when deploying, defaults to name defined on the
        Application Specification
            """

        self.app_spec = APP_SPEC
        
        # calling full __init__ signature, so ignoring mypy warning about overloads
        self.app_client = algokit_utils.ApplicationClient(  # type: ignore[call-overload, misc]
            algod_client=algod_client,
            app_spec=self.app_spec,
            app_id=app_id,
            creator=creator,
            indexer_client=indexer_client,
            existing_deployments=existing_deployments,
            signer=signer,
            sender=sender,
            suggested_params=suggested_params,
            template_values=template_values,
            app_name=app_name,
        )

    @property
    def algod_client(self) -> algosdk.v2client.algod.AlgodClient:
        return self.app_client.algod_client

    @property
    def app_id(self) -> int:
        return self.app_client.app_id

    @app_id.setter
    def app_id(self, value: int) -> None:
        self.app_client.app_id = value

    @property
    def app_address(self) -> str:
        return self.app_client.app_address

    @property
    def sender(self) -> str | None:
        return self.app_client.sender

    @sender.setter
    def sender(self, value: str) -> None:
        self.app_client.sender = value

    @property
    def signer(self) -> TransactionSigner | None:
        return self.app_client.signer

    @signer.setter
    def signer(self, value: TransactionSigner) -> None:
        self.app_client.signer = value

    @property
    def suggested_params(self) -> algosdk.transaction.SuggestedParams | None:
        return self.app_client.suggested_params

    @suggested_params.setter
    def suggested_params(self, value: algosdk.transaction.SuggestedParams | None) -> None:
        self.app_client.suggested_params = value

    def get_global_state(self) -> GlobalState:
        """Returns the application's global state wrapped in a strongly typed class with options to format the stored value"""

        state = typing.cast(dict[bytes, bytes | int], self.app_client.get_global_state(raw=True))
        return GlobalState(state)

    def get_local_state(self, account: str | None = None) -> LocalState:
        """Returns the application's local state wrapped in a strongly typed class with options to format the stored value"""

        state = typing.cast(dict[bytes, bytes | int], self.app_client.get_local_state(account, raw=True))
        return LocalState(state)

    def create_option(
        self,
        *,
        counter_offer: int,
        expires_timestamp: int,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
    ) -> algokit_utils.ABITransactionResponse[None]:
        """Calls `create_option(uint64,uint64)void` ABI method
        
        :param int counter_offer: The `counter_offer` ABI parameter
        :param int expires_timestamp: The `expires_timestamp` ABI parameter
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns algokit_utils.ABITransactionResponse[None]: The result of the transaction"""

        args = CreateOptionArgs(
            counter_offer=counter_offer,
            expires_timestamp=expires_timestamp,
        )
        result = self.app_client.call(
            call_abi_method=args.method(),
            transaction_parameters=_convert_call_transaction_parameters(transaction_parameters),
            **_as_dict(args, convert_all=True),
        )
        return result

    def create_bare(
        self,
        *,
        on_complete: typing.Literal["no_op"] = "no_op",
        transaction_parameters: algokit_utils.CreateTransactionParameters | None = None,
    ) -> algokit_utils.TransactionResponse:
        """Creates an application using the no_op bare method
        
        :param typing.Literal[no_op] on_complete: On completion type to use
        :param algokit_utils.CreateTransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns algokit_utils.TransactionResponse: The result of the transaction"""

        result = self.app_client.create(
            call_abi_method=False,
            transaction_parameters=_convert_create_transaction_parameters(transaction_parameters, on_complete),
        )
        return result

    def clear_state(
        self,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
        app_args: list[bytes] | None = None,
    ) -> algokit_utils.TransactionResponse:
        """Calls the application with on completion set to ClearState
    
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :param list[bytes] | None app_args: (optional) Application args to pass
        :returns algokit_utils.TransactionResponse: The result of the transaction"""
    
        return self.app_client.clear_state(_convert_transaction_parameters(transaction_parameters), app_args)

    def deploy(
        self,
        version: str | None = None,
        *,
        signer: TransactionSigner | None = None,
        sender: str | None = None,
        allow_update: bool | None = None,
        allow_delete: bool | None = None,
        on_update: algokit_utils.OnUpdate = algokit_utils.OnUpdate.Fail,
        on_schema_break: algokit_utils.OnSchemaBreak = algokit_utils.OnSchemaBreak.Fail,
        template_values: algokit_utils.TemplateValueMapping | None = None,
        create_args: algokit_utils.DeployCallArgs | None = None,
        update_args: algokit_utils.DeployCallArgs | None = None,
        delete_args: algokit_utils.DeployCallArgs | None = None,
    ) -> algokit_utils.DeployResponse:
        """Deploy an application and update client to reference it.
        
        Idempotently deploy (create, update/delete if changed) an app against the given name via the given creator
        account, including deploy-time template placeholder substitutions.
        To understand the architecture decisions behind this functionality please see
        <https://github.com/algorandfoundation/algokit-cli/blob/main/docs/architecture-decisions/2023-01-12_smart-contract-deployment.md>
        
        ```{note}
        If there is a breaking state schema change to an existing app (and `on_schema_break` is set to
        'ReplaceApp' the existing app will be deleted and re-created.
        ```
        
        ```{note}
        If there is an update (different TEAL code) to an existing app (and `on_update` is set to 'ReplaceApp')
        the existing app will be deleted and re-created.
        ```
        
        :param str version: version to use when creating or updating app, if None version will be auto incremented
        :param algosdk.atomic_transaction_composer.TransactionSigner signer: signer to use when deploying app
        , if None uses self.signer
        :param str sender: sender address to use when deploying app, if None uses self.sender
        :param bool allow_delete: Used to set the `TMPL_DELETABLE` template variable to conditionally control if an app
        can be deleted
        :param bool allow_update: Used to set the `TMPL_UPDATABLE` template variable to conditionally control if an app
        can be updated
        :param OnUpdate on_update: Determines what action to take if an application update is required
        :param OnSchemaBreak on_schema_break: Determines what action to take if an application schema requirements
        has increased beyond the current allocation
        :param dict[str, int|str|bytes] template_values: Values to use for `TMPL_*` template variables, dictionary keys
        should *NOT* include the TMPL_ prefix
        :param algokit_utils.DeployCallArgs | None create_args: Arguments used when creating an application
        :param algokit_utils.DeployCallArgs | None update_args: Arguments used when updating an application
        :param algokit_utils.DeployCallArgs | None delete_args: Arguments used when deleting an application
        :return DeployResponse: details action taken and relevant transactions
        :raises DeploymentError: If the deployment failed"""

        return self.app_client.deploy(
            version,
            signer=signer,
            sender=sender,
            allow_update=allow_update,
            allow_delete=allow_delete,
            on_update=on_update,
            on_schema_break=on_schema_break,
            template_values=template_values,
            create_args=_convert_deploy_args(create_args),
            update_args=_convert_deploy_args(update_args),
            delete_args=_convert_deploy_args(delete_args),
        )

    def compose(self, atc: AtomicTransactionComposer | None = None) -> Composer:
        return Composer(self.app_client, atc or AtomicTransactionComposer())
