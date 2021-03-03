# Computing APY

## Pool APY
### Approach
* compute the pool's revenue over the past 24h and assume it remains constant for the next 365 days;
* assume liquidity remains constant for the next 365 days; 
* APY is the ratio between the 365 days expected revenue and the liquidity

### Formulas and data sources
$A_m$: Expected future APY at block $m$  
$F_m$: `totalSwapFee` at block $m$  
$F_n$: `totalSwapFee` at block $n$  
$L_m$: `liquidity` at block $m$  
$L_n$: `liquidity` at block $n$  
$t_m$: `timestamp` of block $m$  
$t_n$: `timestamp` of block $n$  

1. Read $m$ from web3
2. Define $n=m-6500$ (roughly 24h worth of blocks)
3. Read $t_m$ and $t_n$ from web3

$$ A_m = \frac{31556926}{t_m - t_n}\cdot\frac{F_m-F_n}{L_m} $$

Alternatively, we could explore the pros and cons of an estimator of the average liquidity over the , eg. the average between the snapshot blocks
 
$$ A_m = \frac{31556926}{t_m - t_n}\cdot\ \frac{F_m-F_n}{\frac{L_m+L_n}{2}} $$

## Liquidity Provider's APY
### Approach
* compute the pool's APY for each pool the LP has liquidity in
* compute the share of the pool held by the LP
* The LP's APY is the weighted arithmetic mean of the APY of the pools they provided liquidity in (weights are the LP's liquidity in each pool)

### Formulas and data sources
$A_{l,m}$: Expected future APY of LP's $l$ position at block $m$  
$A_{p,m}$: Expected future APY of pool $p$ at block $m$  
$L_{p,m}$: `liquidity` of pool $p$ at block $m$  
$L_{l,p,m}$: liquidity provided by LP $l$ at pool $p$ at block $m$  
$S_{p,m}$: `totalShares` of pool $p$ at block $m$  
$B_{l,p,m}$: `balance` of `PoolShare` for LP $l$ at pool $p$ at block $m$  

1. Given an LP $X$, find the set of pools $P$ such that $B_{X,p,m}>0$ (query subgraph `users`)

2. For all pools in $P$, compute $L_{X,p,m}$ and $A_{p,m}$   
$$ L_{X,p,m} = \frac{B_{X,p,m}L_{p,m}}{S_{p,m}} \forall{p\in{P}}$$   
$$ A_{p,m} = \frac{31556926}{t_m - t_n}\cdot\frac{F_{p,m}-F_{p,n}}{L_{p,m}} \forall{p\in{P}}$$

3. Compute $A_{X,m}$  
$$ A_{X,m} = \frac{\sum\limits_{p\in{P}}{A_{p,m}L_{X,p,m}}}{\sum{L_{X,p,m}}} $$