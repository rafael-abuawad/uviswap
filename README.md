# Uviswap: Decentralized Automated Market Maker (AMM)

Uviswap is a decentralized automated market maker (AMM) that allows users to swap tokens and provide liquidity to earn fees. This repository contains the smart contracts for the Uviswap Pair and Factory, along with testing scripts and deployment instructions.

## Table of Contents

- [Overview](#overview)
- [Smart Contracts](#smart-contracts)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Overview

Uviswap is built on the principles of automated market makers, providing a decentralized solution for token swaps and liquidity provision. It utilizes a pair-based model where users can add liquidity to pairs of tokens, and swaps are executed based on the liquidity available in the pairs.

## Smart Contracts

### UviswapPair

The `UviswapPair` smart contract represents an individual token pair. It includes functions for adding liquidity, removing liquidity, swapping tokens, and collecting fees.

- [UviswapPair.sol](contracts/UviswapPair.vy): The source code for the `UviswapPair` smart contract.

### UviswapFactory

The `UviswapFactory` smart contract is responsible for creating and managing pairs of tokens. It includes a method for creating new pairs and deploying instances of the `UviswapPair` contract.

- [UviswapFactory.sol](contracts/UviswapFactory.vy): The source code for the `UviswapFactory` smart contract.

## Testing

The testing scripts are provided in the `tests` folder, specifically in the [test_uviswap.py](tests/test_uviswap.py) file. These tests cover various functionalities, including adding and removing liquidity, swapping tokens, and collecting fees.

To run the tests locally, use the following command:

```bash
$ ape test
```

Make sure to configure the testing fixtures and accounts in [conftest.py](tests/conftest.py) based on your requirements.

## Deployment

To deploy the Uviswap application, follow these steps:

1. Install the Avalanche plugin:

   ```bash
   $ ape plugins install avalanche
   ```

2. Configure the RPC URL endpoints in `ape-config.yaml` for the desired network (mainnet or testnet).

3. Create accounts for deployment:

   ```bash
   $ ape accounts generate <name_of_your_account>
   ```
Make sure to replace `<name_of_your_account>` in the instructions with the actual name you used for the deployment account. Additionally, customize the content based on any specific details or features of your Uviswap application.


4. Customize the deployment script in [deploy.py](scripts/deploy.py) if needed.

5. Run the deployment script:

   ```bash
   $ ape run deploy --network avalanche:fuji  # For Avalanche Testnet
   ```

   ```bash
   $ ape run deploy --network avalanche:mainnet  # For Avalanche Mainnet
   ```

## Contributing

Contributions are welcome! If you have any improvements, bug fixes, or additional features to add, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
