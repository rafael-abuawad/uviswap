# pragma version ^0.3.10

###### INTERFACES ######

interface UviswapPair:
    def setup(_token0: address, _token1: address): nonpayable

###### STATE ######

# Pair Contract => Token <=> Token
getPair: public(HashMap[address, HashMap[address, address]])

# All pairs list
allPairs: public(DynArray[address, 30])

# Uviswap Pair contract address used to create clones of it
pairContract: address

###### CONSTRUCTOR ######

@external
def __init__(_pairContract: address):
    self.pairContract = _pairContract


###### METHODS ######

@external
def createPair(_tokenA: address, _tokenB: address) -> address:
    assert _tokenA != _tokenB, "Uviswap Factory: identical addresses"
    assert _tokenA != empty(address) and _tokenB != empty(address), "Uviswap Factory: zero address"
    assert self.getPair[_tokenA][_tokenB] == empty(address),  "Uviswap Factory: pair exists"

    # create pair smart contract
    pair: address = create_forwarder_to(self.pairContract)
    UviswapPair(pair).setup(_tokenA, _tokenB)

    # populate mapping in, and in the reverse direction
    self.getPair[_tokenA][_tokenB] = pair
    self.getPair[_tokenB][_tokenA] = pair

    # append pair to all pairs array
    self.allPairs.append(pair)

    return pair
