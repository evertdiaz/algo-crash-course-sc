from beaker import *
from pyteal import *

################ STEP 1
app = Application("HelloWorld")

# Method add version 1
@app.external
def addV1(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
  return output.set(a.get() + b.get())

# Method add using subroutine as if it was raw pyteal
@Subroutine(TealType.uint64)
def sumv1(a: abi.Uint64, b: abi.Uint64) -> Expr:
  return a.get() + b.get()

@app.external
def addv2(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
  return output.set(sumv1(a, b))

# Method add using subroutine in beaker
def sumv2(a: abi.Uint64, b: abi.Uint64) -> Expr:
  return a.get() + b.get()

@app.external
def addv3(a: abi.Uint64, b: abi.Uint64, *, output: abi.Uint64) -> Expr:
  return output.set(sumv2(a, b))

if __name__ == "__main__":
  app.build().export("./artifacts")
