# Balancer APY
Simple script to compute APY of a pool or a liquidity provider's portfolio.

## Requirements
* Python 3
* An ethereum node (for querying blocks timestamps) 

## Setup
* Install required packages: `pip install -r requirements.txt`
* Configure environment variable:
  * `ENDPOINT_URL`: URL to an ethereum node that can be queried via Websockets
  
## Usage
### Pool APY
`python3 bal_apy.py pool <pool_address>`
### Liquidity Provider's APY
`python3 bal_apy.py lp <liquidity_provider_address>`