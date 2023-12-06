from ape import project


def test_create_pair(accounts, usdt_token, usdc_token, uviswap_factory):
    # Create a new pair contract by passing the addresses of two tokens
    uviswap_factory.createPair(
        usdt_token.address, usdc_token.address, sender=accounts[0]
    )

    # Access the address of the created pair contract
    pair_address = uviswap_factory.allPairs(0)

    # Access the pair contract object by its address
    pair = project.UviswapPair.at(pair_address)

    # Assert that the pair contract object has the expected default values
    assert pair.token0() == usdt_token.address
    assert pair.token1() == usdc_token.address
    assert pair.reserve0() == 0
    assert pair.reserve1() == 0
    assert pair.totalSupply() == 0


def test_add_liquidity(accounts, usdt_token, usdc_token, uviswap_factory):
    # Create a new pair contract by passing the addresses of two tokens
    uviswap_factory.createPair(
        usdt_token.address, usdc_token.address, sender=accounts[0]
    )

    # Access the address of the created pair contract
    pair_address = uviswap_factory.allPairs(0)

    # Access the pair contract object by its address
    pair = project.UviswapPair.at(pair_address)

    # Define the amount to add liquidity to the pair contract (500 USDC/USDT)
    amount = int(500e18)

    # Approve pair to use our tokens
    usdt_token.approve(pair_address, amount, sender=accounts[0])
    usdc_token.approve(pair_address, amount, sender=accounts[0])

    # Add liquidity to the pair contract
    pair.addLiquidity(amount, amount, sender=accounts[0])

    # Check if the liquidity is added correctly
    assert pair.balanceOf(accounts[0]) == amount  # minted shares
    assert pair.reserve0() == amount
    assert pair.reserve1() == amount
    assert usdt_token.balanceOf(pair) == amount
    assert usdc_token.balanceOf(pair) == amount


def test_remove_liquidity(accounts, usdt_token, usdc_token, uviswap_factory):
    # Create a new pair contract by passing the addresses of two tokens
    uviswap_factory.createPair(
        usdt_token.address, usdc_token.address, sender=accounts[0]
    )

    # Access the address of the created pair contract
    pair_address = uviswap_factory.allPairs(0)

    # Access the pair contract object by its address
    pair = project.UviswapPair.at(pair_address)

    # Define the amount to add liquidity to the pair contract (500 USDC/USDT)
    amount = int(500e18)

    # Approve pair to use our tokens
    usdt_token.approve(pair_address, amount, sender=accounts[0])
    usdc_token.approve(pair_address, amount, sender=accounts[0])

    # Add liquidity to the pair contract
    pair.addLiquidity(amount, amount, sender=accounts[0])

    # Get the amount of shares owned by the account
    shares = pair.balanceOf(accounts[0])

    # Remove liquidity from the pair
    pair.removeLiquidity(shares, sender=accounts[0])

    # Assert that the pool reserves and token balances are now all zero
    assert pair.balanceOf(accounts[0]) == 0  # confirm shares have been removed
    assert pair.reserve0() == 0
    assert pair.reserve1() == 0
    assert usdc_token.balanceOf(pair) == 0
    assert usdt_token.balanceOf(pair) == 0


def test_swap(accounts, usdt_token, usdc_token, uviswap_factory):
    # Create a new pair contract by passing the addresses of two tokens
    uviswap_factory.createPair(
        usdt_token.address, usdc_token.address, sender=accounts[0]
    )

    # Access the address of the created pair contract
    pair_address = uviswap_factory.allPairs(0)

    # Access the pair contract object by its address
    pair = project.UviswapPair.at(pair_address)

    # Define the amount to add liquidity to the pair contract (500 USDC/USDT)
    amount = int(500e18)

    # Approve pair to use our tokens
    usdt_token.approve(pair_address, amount, sender=accounts[0])
    usdc_token.approve(pair_address, amount, sender=accounts[0])

    # Add liquidity to the pair contract
    pair.addLiquidity(amount, amount, sender=accounts[0])

    # Save the initial balances before the swap
    initial_balances = {
        "usdt": usdt_token.balanceOf(accounts[0]),
        "usdc": usdc_token.balanceOf(accounts[0]),
    }

    # Define the amount to be swapped for the other token on the pair contract (100 USDT)
    swap_amount = int(100e18)

    # Approve token for a swap
    usdt_token.approve(pair_address, swap_amount, sender=accounts[0])

    # Perform the swap
    pair.swap(usdt_token.address, swap_amount, sender=accounts[0])

    # Get the balances after the swap
    final_balances = {
        "usdt": usdt_token.balanceOf(accounts[0]),
        "usdc": usdc_token.balanceOf(accounts[0]),
    }

    # Test that we swapped tokens correctly
    assert (
        initial_balances["usdt"] - swap_amount == final_balances["usdt"]
    )  # USDT balance should decrease (initial - swaped amount)
    assert (
        initial_balances["usdc"] < final_balances["usdc"]
    )  # USDC balance should increase


def test_collecting_fees(accounts, usdt_token, usdc_token, uviswap_factory):
    # Create a new pair contract by passing the addresses of two tokens
    uviswap_factory.createPair(
        usdt_token.address, usdc_token.address, sender=accounts[0]
    )

    # Access the address of the created pair contract
    pair_address = uviswap_factory.allPairs(0)

    # Access the pair contract object by its address
    pair = project.UviswapPair.at(pair_address)

    # Define the amount to add liquidity to the pair contract (100 USDC/USDT)
    amount = int(100e18)

    # Approve pair to use our tokens
    usdt_token.approve(pair_address, amount, sender=accounts[0])
    usdc_token.approve(pair_address, amount, sender=accounts[0])

    # Add liquidity to the pair contract
    pair.addLiquidity(amount, amount, sender=accounts[0])

    # Save the initial balances before the swap
    balances = {
        "usdt": usdt_token.balanceOf(accounts[0]),
        "usdc": usdc_token.balanceOf(accounts[0]),
    }

    # Define the amount to be swapped for the other token on the pair contract (10 USDT)
    swap_amount = int(10e18)

    # Approve token for a swap
    usdt_token.approve(pair_address, swap_amount, sender=accounts[0])

    # Perform the swap
    pair.swap(usdt_token.address, swap_amount, sender=accounts[0])

    # Get shares
    shares = pair.balanceOf(accounts[0])
    assert shares == int(
        100e18
    )  # shares received should be equal to the amount of liquidity added

    # Remove liquidity
    pair.removeLiquidity(shares, sender=accounts[0])

    # Get the balances after claiming all the shares
    balances = {
        "usdt": usdt_token.balanceOf(accounts[0]),
        "usdc": usdc_token.balanceOf(accounts[0]),
    }

    # Test that we collected fees correctly
    assert balances["usdt"] == int(1000e18)  # USDT balance should be the original mint
    assert balances["usdc"] == int(1000e18)  # USDC balance should be the original mint
    assert pair.balanceOf(accounts[0]) == 0  # confirm shares have been removed
    assert pair.reserve0() == 0
    assert pair.reserve1() == 0
    assert usdc_token.balanceOf(pair) == 0
    assert usdt_token.balanceOf(pair) == 0
