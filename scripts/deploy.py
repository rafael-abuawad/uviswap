from ape import project, accounts

def main():
    test_account = accounts.load("test_account")
    uviswap_pair = project.UviswapPair.deploy(sender=test_account)
    project.UviswapFactory.deploy(uviswap_pair.address, sender=test_account)
