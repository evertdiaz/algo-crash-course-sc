from beaker import *
from pyteal import *


class MyState:
  global_sum = GlobalStateValue(
    stack_type=TealType.uint64,
    default=Int(999)
  )

app = Application("Calculator", state=MyState())

@app.create
def create() -> Expr:
  return app.initialize_global_state()

def sub_add(a: abi.Uint64, b: abi.Uint64) -> Expr:
  return a.get() + b.get()

@app.external
def add(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
  result = sub_add(a,b)
  return Seq(
    app.state.global_sum.set(result),
    output.set(result)
  )

@app.external
def read_global(*,output: abi.Uint64) -> Expr:
  return output.set(app.state.global_sum.get())


if __name__ == "__main__":
  app.build().export("./artifacts")
