import pytest


@pytest.fixture(scope="function")
def usdt_token(project, accounts):
    """
    Returns a new instance of a mock USDT token contract, with an initial supply of 1,000.
    """
    return project.Token.deploy("USDT", "USDT", 18, 1000, sender=accounts[0])


@pytest.fixture(scope="function")
def usdc_token(project, accounts):
    """
    Returns a new instance of a mock USDC token contract, with an initial supply of 1,000.
    """
    return project.Token.deploy("USDC", "USDC", 18, 1000, sender=accounts[0])


@pytest.fixture(scope="function")
def uviswap_pair(project, accounts):
    """
    Returns a new instance of an empty Pair contract, primarily to be used as a blueprint.
    """
    return project.UviswapPair.deploy(sender=accounts[0])


@pytest.fixture(scope="function")
def uviswap_factory(project, accounts, uviswap_pair):
    """
    Returns a new instance of a Factory contract, the main entry point of our AMM.
    """
    return project.UviswapFactory.deploy(uviswap_pair.address, sender=accounts[0])
