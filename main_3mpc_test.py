# 3MPC scheme with additive secret sharing
import random

# Use the infinity
inf = float("inf")

def SplitSecret(secret: int = 1):
    # Split the secret into 3 shares
    share1 = random.randint(1, secret)
    share2 = random.randint(1, secret)
    share3 = secret - share1 - share2
    
    shares_party_1 = [share1, inf, share3]
    
    shares_party_2 = [share1, share2, inf]
    
    shares_party_3 = [inf, share2, share3]
    
    return shares_party_1, shares_party_2, shares_party_3

# Reconstruction of the secret. Only 2 partioes are needed to reconstruct the secret
def ReconstructSecret(sharesA: list, sharesB: list):
    secret = 0
    for s in range(3):
        if sharesA[s] == inf:
            secret += sharesB[s]
        elif sharesB[s] == inf:
            secret += sharesA[s]
        else:
            secret += sharesA[s]
            
    return secret

# Secret to be shared
x = 54

# Split the secret
shares1, shares2, shares3 = SplitSecret(x)

print("Shares: ", shares1, shares2, shares3)

print("Reconstructed secret: ", ReconstructSecret(shares1, shares2))
print("Reconstructed secret: ", ReconstructSecret(shares1, shares3))
print("Reconstructed secret: ", ReconstructSecret(shares2, shares3))
