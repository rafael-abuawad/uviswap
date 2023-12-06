# pragma version ^0.3.10

from vyper.interfaces import ERC20
from vyper.interfaces import ERC20Detailed

###### EVENTS ######

event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    value: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    value: uint256

###### STATE ######

# Share's token name
name: public(String[32])

# Share's token symbol
symbol: public(String[32])

# Share's token decimals
decimals: public(uint8)

# By declaring `balanceOf` as public, vyper automatically generates a 'balanceOf()' getter
# method to allow access to account balances.
balanceOf: public(HashMap[address, uint256])

# By declaring `allowance` as public, vyper automatically generates the `allowance()` getter
allowance: public(HashMap[address, HashMap[address, uint256]])

# By declaring `totalSupply` as public, we automatically create the `totalSupply()` getter
totalSupply: public(uint256)

# Tokens in the pair
token0: public(address)
token1: public(address)

# Reserves for each token
reserve0: public(uint256)
reserve1: public(uint256)

# Setup flag
_setup: bool

###### CONSTRUCTOR ######
@external
def __init__():
    self.name = "Uviswap"
    self.symbol = "UVI"
    self.decimals = 18

###### INTERNAL METHODS ######
@internal
def _mint(_to: address, _value: uint256):
    assert _to != empty(address), "ERC20: mint to the zero address"
    self.balanceOf[_to] += _value
    self.totalSupply += _value
    log Transfer(empty(address), _to, _value)


@internal
def _burn(_to: address, _value: uint256):
    assert _to != empty(address), "ERC20: burn to the zero address"
    self.balanceOf[_to] -= _value
    self.totalSupply -= _value
    log Transfer(_to, empty(address), _value)


@internal
def _update(_reserve0: uint256, _reserve1: uint256):
    self.reserve0 = _reserve0
    self.reserve1 = _reserve1


###### EXTERNAL METHODS ######
@external
def transfer(_to : address, _value : uint256) -> bool:
    assert _to != empty(address), "ERC20: transfer to the zero address"

    self.balanceOf[msg.sender] -= _value
    self.balanceOf[_to] += _value
    log Transfer(msg.sender, _to, _value)
    return True


@external
def transferFrom(_from : address, _to : address, _value : uint256) -> bool:
    self.allowance[_from][msg.sender] -= _value
    self.balanceOf[_from] -= _value
    self.balanceOf[_to] += _value

    log Transfer(_from, _to, _value)
    return True


@external
def approve(_spender : address, _value : uint256) -> bool:
    self.allowance[msg.sender][_spender] = _value
    log Approval(msg.sender, _spender, _value)
    return True


@external
def burn(_value: uint256):
    self._burn(msg.sender, _value)


@external
def setup(_token0: address, _token1: address):
    assert self._setup == False, "Uviswap Pair: already initialized"
    self.token0 = _token0
    self.token1 = _token1
    self._setup = True


@external
@nonreentrant("add")
def addLiquidity(_amount0: uint256, _amount1: uint256) -> uint256:
    # add liquidity
    ERC20(self.token0).transferFrom(msg.sender, self, _amount0)
    ERC20(self.token1).transferFrom(msg.sender, self, _amount1)

    # keep the pool balanced (k=x*y)
    if self.reserve0 > 0 or self.reserve1 > 0:
        assert self.reserve0 * _amount1 == self.reserve1 * _amount0, "Uviswap Pair: x / y != dx / dy" 

    shares: uint256 = 0
    if self.totalSupply == 0:
        shares = isqrt(_amount0 * _amount1)
    else:
        shares = min(
            (_amount0 * self.totalSupply) * self.reserve0,
            (_amount1 * self.totalSupply) * self.reserve1
        )

    assert shares > 0, "Uviswap Pair: shares were zero"

    # mint shares to liquidity provider
    self._mint(msg.sender, shares)

    # update reserves
    self._update(ERC20(self.token0).balanceOf(self), ERC20(self.token1).balanceOf(self))

    return shares

@external
@nonreentrant("remove")
def removeLiquidity(_shares: uint256) -> (uint256, uint256):
    _token0: ERC20 = ERC20(self.token0)
    _token1: ERC20 = ERC20(self.token1)

    bal0: uint256 = _token0.balanceOf(self)
    bal1: uint256 = _token1.balanceOf(self)

    amount0: uint256 = (_shares * bal0) / self.totalSupply
    amount1: uint256 = (_shares * bal1) / self.totalSupply

    # _burn checks if the user has enough shares
    self._burn(msg.sender, _shares)
    # update reserves
    self._update(bal0 - amount0, bal1 - amount1)

    # transfers the tokens back
    _token0.transfer(msg.sender, amount0)
    _token1.transfer(msg.sender, amount1)

    return (amount0, amount1)


@external
@nonreentrant("swap")
def swap(_tokenIn: address, _amountIn: uint256) -> uint256:
    assert _tokenIn == self.token0 or _tokenIn == self.token1, "Uviswap Pair: invalid token"
    assert _amountIn > 0, "Uviswap Pair: amount in is zero"

    # variables to interact with the liquidity pool
    tokenIn: ERC20 = empty(ERC20)
    tokenOut: ERC20 = empty(ERC20)
    reserveIn: uint256 = 0
    reserveOut: uint256 = 0

    # determine which token is being swapped in
    # and assigning variables accordingly
    isToken0: bool = _tokenIn == self.token0
    if isToken0:
        tokenIn = ERC20(self.token0)
        tokenOut = ERC20(self.token1)
        reserveIn = self.reserve0
        reserveOut = self.reserve1
    else:
        tokenIn = ERC20(self.token1)
        tokenOut = ERC20(self.token0)
        reserveIn = self.reserve1
        reserveOut = self.reserve0

    # transfer in the tokens
    tokenIn.transferFrom(msg.sender, self, _amountIn)

    # 0.3% fee
    amountInWithFee: uint256 = (_amountIn * 997) / 1000

    # calculate tokens to transfer
    amountOut: uint256 = (reserveOut * amountInWithFee) / (reserveIn + amountInWithFee)
    tokenOut.transfer(msg.sender, amountOut)

    # update reserves
    self._update(ERC20(self.token0).balanceOf(self), ERC20(self.token1).balanceOf(self))

    # transfer in the tokens
    return amountOut