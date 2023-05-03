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

app = Application("HelloWorld", state=MyState()).apply(
  unconditional_create_approval, initialize_global_state=True).apply(
  unconditional_opt_in_approval, initialize_local_state=True)

def sub_add(a: abi.Uint64, b: abi.Uint64) -> Expr:
  return a.get() + b.get()

@app.external
def add(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
  result = sub_add(a,b)
  return Seq(
    app.state.global_sum.set(result),
    app.state.local_sum[Txn.sender()].set(result),
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
