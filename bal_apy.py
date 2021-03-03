import pandas as pd
import requests
import json
from web3 import Web3
import os
import sys
THEGRAPH_URL = 'https://api.thegraph.com/subgraphs/name/balancer-labs/balancer'
try:
    web3_provider = os.environ['ENDPOINT_URL']
    w3 = Web3(Web3.WebsocketProvider(web3_provider))
except:
    sys.exit('You must set the ENDPOINT_URL environment variable')

def query_thegraph(query):
    r = requests.post(THEGRAPH_URL, json = {'query':query})
    try:
        return json.loads(r.content)['data']
    except:
        print(query)
        print(r.content)
        raise


def get_pool_data(pools, block=0):
    if type(pools) == str:
        pools = [pools.lower()]
    else:
        pools = list(map(lambda x: x.lower(), pools))
    if block==0:
        query = '''
        query {{
            pools(first: 1000, 
                    where: {{id_in: ["{0}"]}}) {{
                id
                liquidity
                totalSwapFee
                totalShares
            }}
        }}'''.format('","'.join(pools))
    else:
        query = '''
        query {{
            pools(first: 1000, block: {{number: {1}}},
                    where: {{id_in: ["{0}"]}}) {{
                id
                liquidity
                totalSwapFee
                totalShares
            }}
        }}'''.format('","'.join(pools), block)
    
    p = query_thegraph(query)['pools']
    df = pd.DataFrame(p).set_index('id').astype(float)
    return df



def get_pools_APY(pools, end_block=None):
    if end_block:
        m = end_block
    else:
        m = w3.eth.getBlock('latest').number - 10 #can't use the actual latest because Subgraph lags behind
    n = m-6600
    t_m = w3.eth.getBlock(m).timestamp
    t_n = w3.eth.getBlock(n).timestamp
    m_data = get_pool_data(pools, m)#.set_index('id')
    n_data = get_pool_data(pools, n)#.set_index('id')
    merge = n_data.join(m_data, lsuffix='_n', rsuffix='_m')
    merge.drop(columns=['liquidity_n','totalShares_n'], inplace=True)
    merge['APY'] = 31556926 / (t_m - t_n) * (merge['totalSwapFee_m'] - merge['totalSwapFee_n']) / merge['liquidity_m']
    return merge[['liquidity_m','totalShares_m','APY']]




def get_pools(liquidity_provider, block=0):
    liquidity_provider = liquidity_provider.lower()
    if block==0:
        query = '''
        query {{
            users(first: 1000, 
                    where: {{id: "{0}"}}) {{
                sharesOwned (where: {{balance_gt: 0}}) {{
                    poolId {{id}}
                    balance
                }}
            }}
        }}'''.format(liquidity_provider)
    else:
        query = '''
        query {{
            users(first: 1000, block: {{number: {1}}},
                    where: {{id: "{0}"}}) {{
                sharesOwned (where: {{balance_gt: 0}}) {{
                    poolId {{id}}
                    balance
                }}
            }}
        }}'''.format(liquidity_provider, block)
    
    balances = query_thegraph(query)['users'][0]['sharesOwned']
    balances = list(map(lambda x: (x['poolId']['id'], x['balance']), balances))
    df = pd.DataFrame(balances)
    df.columns = ['id', 'balance']
    df = df.set_index('id').astype(float)
    return df



def get_lp_APY(lp, block=0):
    if block==0:
        m = w3.eth.getBlock('latest').number - 10
    else:
        m = block
    lp_pools = get_pools(lp, m)
    lp_pools_apy = get_pools_APY(lp_pools.index.values, m)
    merge = lp_pools_apy.join(lp_pools)
    merge['lp_liquidity'] = merge['liquidity_m'] * merge['balance'] / merge['totalShares_m']
    lp_apy = (merge['lp_liquidity'] * merge['APY']).sum() / merge['lp_liquidity'].sum()
    return lp_apy

if sys.argv[1] == 'pool':
    print(f'APY for pool {sys.argv[2]}')
    a = get_pools_APY(sys.argv[2]).loc[sys.argv[2],'APY']
    print('{:.2%}'.format(a))
if sys.argv[1] == 'lp':
    print(f'APY for LP {sys.argv[2]}')
    a = get_lp_APY(sys.argv[2])
    print('{:.2%}'.format(a))

