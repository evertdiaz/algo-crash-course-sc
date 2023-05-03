from beaker import *
from pyteal import *


class MyState:
  global_sum = GlobalStateValue(
    stack_type=TealType.uint64,
    default=Int(999)
  )
  local_sum = LocalStateValue(
    stack_type=TealType.uint64,
    default=Int(999)
  )
  asa_id = GlobalStateValue(TealType.uint64)

app = Application("Calculator", state=MyState()).apply(
  unconditional_create_approval, initialize_global_state=True).apply(
  unconditional_opt_in_approval, initialize_local_state=True)

@app.external
def create_tokens(
  asa_name:abi.String, 
  unit_name:abi.String,
  total:abi.Uint64,
  p:abi.PaymentTransaction,
  *,
  output:abi.Uint64
  ) -> Expr:
  return Seq(
    Assert(Txn.sender() == Global.creator_address()),
    Assert(p.get().receiver() == Global.current_application_address()),
    Assert(p.get().amount() > Int(1000000)),
    InnerTxnBuilder.Execute({
      TxnField.type_enum: TxnType.AssetConfig,
      TxnField.config_asset_unit_name: unit_name.get(),
      TxnField.config_asset_name: asa_name.get(),
      TxnField.config_asset_decimals: Int(0),
      TxnField.config_asset_total: total.get()
    }),
    app.state.asa_id.set(InnerTxn.created_asset_id())
  )

def sub_add(a: abi.Uint64, b: abi.Uint64) -> Expr:
  return a.get() + b.get()

@app.external
def add(
  p: abi.PaymentTransaction, 
  a: abi.Uint64, 
  b: abi.Uint64, 
  asa: abi.Asset,
  *, 
  output: abi.Uint64
  ) -> Expr:
  result = sub_add(a,b)
  return Seq(
    Assert(Global.creator_address() != Txn.sender()),
    Assert(Global.current_application_address() == p.get().receiver()),
    Assert(p.get().amount() >= Int(100000)),
    app.state.global_sum.set(result),
    app.state.local_sum[Txn.sender()].set(result),
    InnerTxnBuilder.Execute({
      TxnField.type_enum: TxnType.AssetTransfer,
      TxnField.xfer_asset: asa.asset_id(),
      TxnField.asset_receiver: Txn.sender(),
      TxnField.asset_amount: Int(1)
    }),
    output.set(result)
  )

@app.external
def read_global(*,output: abi.Uint64) -> Expr:
  return output.set(app.state.global_sum.get())

@app.external
def read_local(*,output: abi.Uint64) -> Expr:
  return output.set(app.state.local_sum[Txn.sender()].get())


if __name__ == "__main__":
  app.build().export("./artifacts")
