from beaker import *
from pyteal import *


class MyState:
    asa_id = GlobalStateValue(TealType.uint64)


app = Application("Calculator", state=MyState())


@app.external
def new_global_box() -> Expr:
    return Seq(
        Assert(Txn.sender() == Global.creator_address()),
        BoxPut(Bytes("globalBox"), Itob(Int(999))),
    )


@app.external
def new_local_box(address: abi.String) -> Expr:
    return Seq(BoxPut(address.get(), Itob(Int(999))))


@app.external
def read_box(a: abi.String, *, output: abi.Uint64) -> Expr:
    return Seq(
        boxval := App.box_get(a.get()),
        Assert(boxval.hasValue()),
        output.set(Btoi(boxval.value())),
    )


@app.external
def create_tokens(
    asa_name: abi.String,
    unit_name: abi.String,
    total: abi.Uint64,
    *,
    output: abi.Uint64,
) -> Expr:
    return Seq(
        Assert(Txn.sender() == Global.creator_address()),
        InnerTxnBuilder.Execute(
            {
                TxnField.type_enum: TxnType.AssetConfig,
                TxnField.config_asset_unit_name: unit_name.get(),
                TxnField.config_asset_name: asa_name.get(),
                TxnField.config_asset_decimals: Int(0),
                TxnField.config_asset_total: total.get(),
            }
        ),
        app.state.asa_id.set(InnerTxn.created_asset_id()),
        output.set(InnerTxn.created_asset_id()),
    )


def sub_add(a: abi.Uint64, b: abi.Uint64) -> Expr:
    return a.get() + b.get()


@app.external
def add(
    p: abi.PaymentTransaction,
    a: abi.Uint64,
    b: abi.Uint64,
    address: abi.String,
    asa: abi.Asset,
    *,
    output: abi.Uint64,
) -> Expr:
    result = sub_add(a, b)
    return Seq(
        Assert(Global.creator_address() != Txn.sender()),
        Assert(Global.current_application_address() == p.get().receiver()),
        Assert(p.get().amount() >= Int(100000)),
        App.box_put(Bytes("globalBox"), Itob(result)),
        App.box_put(address.get(), Itob(result)),
        InnerTxnBuilder.Execute(
            {
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.xfer_asset: asa.asset_id(),
                TxnField.asset_receiver: Txn.sender(),
                TxnField.asset_amount: Int(1),
            }
        ),
        output.set(result),
    )


if __name__ == "__main__":
    app.build().export("./artifacts")
