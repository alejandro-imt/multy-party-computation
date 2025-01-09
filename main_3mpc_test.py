# 3MPC scheme with additive secret sharing
import random
import numpy as np # To check the dot product

# Use the infinity
inf = float("inf")

# K value and "order"
k = 10
order = 2**k

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

# Locally adding 2 secrets
def LocalAddition(shares_secret_1: list, shares_secret_2: list):
    
    shares_secret_sum = [inf, inf, inf]
    
    for s in range(3):
        if shares_secret_1[s] != inf and shares_secret_2[s] != inf:
            shares_secret_sum[s] = shares_secret_1[s] + shares_secret_2[s]
            
    return shares_secret_sum

# Locally multiplying 2 secrets
def LocalMultiplication(shares_secret_1: list, shares_secret_2: list, r: int = 0):

    # Party ID
    for i in range(3):
        if shares_secret_1[i] == inf:
            i = i-1%3
            j = i - 1 % 3
            break
    
    # Compute the single share of the product belonging to party i
    share_secret_prod = (shares_secret_1[i] + shares_secret_1[j]) \
        * (shares_secret_2[i] + shares_secret_2[j]) \
            - (shares_secret_1[j] * shares_secret_2[j]) + r

    return share_secret_prod

# Split a vector of secrets
def SplitVectorSecret(vector: list):
    shares_vector_p1 = []
    shares_vector_p2 = []
    shares_vector_p3 = []
    for i in range(len(vector)):
        shares = SplitSecret(vector[i])
        shares_vector_p1.append(shares[0])
        shares_vector_p2.append(shares[1])
        shares_vector_p3.append(shares[2])
    return shares_vector_p1, shares_vector_p2, shares_vector_p3

# Reconstruct a vector of secrets
def ReconstructVectorSecret(sharesA: list, sharesB: list):
    recovered_vector = []
    for i in range(len(sharesA)):
        secret = ReconstructSecret(sharesA[i], sharesB[i])
        recovered_vector.append(secret)
    
    return recovered_vector

##########################################################################################

# Secret to be shared
x = random.randint(1, 100)
y = random.randint(1, 100)

print("Secrets to be shared: x = ", x, " y = ", y)

# Split the secret
shares_x_p1, shares_x_p2, shares_x_p3 = SplitSecret(x)
shares_y_p1, shares_y_p2, shares_y_p3 = SplitSecret(y)
print("\nShares of party 1 for x: ", shares_x_p1)
print("Shares of party 2 for x: ", shares_x_p2)
print("Shares of party 3 for x: ", shares_x_p3)

# Reconstruct the secret x
secret_x = ReconstructSecret(shares_x_p1, shares_x_p2)
print(f"\nRecovered secret x: {secret_x} = {shares_x_p1[0]} + {shares_x_p2[1]} + {shares_x_p3[2]}", "... Expected: ", x)

# Reconstruct the secret y
secret_y = ReconstructSecret(shares_y_p2, shares_y_p3)
print(
    f"\nRecovered secret y: {secret_y} = {shares_y_p1[0]} + {shares_y_p2[1]} + {shares_y_p3[2]}", "... Expected: ", y)

# Add the secrets
shares_z_1 = LocalAddition(shares_x_p1, shares_y_p1)
shares_z_2 = LocalAddition(shares_x_p2, shares_y_p2)
shares_z_3 = LocalAddition(shares_x_p3, shares_y_p3)

# Reconstruct the secret z
secret_z = ReconstructSecret(shares_z_1, shares_z_2)
print("\nRecovered secret x+y: ", secret_z, "... Expected: ", x + y)

# Multiply the secrets
share_prod_1 = LocalMultiplication(shares_x_p1, shares_y_p1)
share_prod_2 = LocalMultiplication(shares_x_p2, shares_y_p2)
share_prod_3 = LocalMultiplication(shares_x_p3, shares_y_p3)

print("\nProduct share of party 1: ", share_prod_1)
print("Product share of party 2: ", share_prod_2)
print("Product share of party 3: ", share_prod_3)

# Reshare the product
shares_prod_p1 = [share_prod_1, inf, share_prod_3]
shares_prod_p2 = [share_prod_1, share_prod_2, inf]
shares_prod_p3 = [inf, share_prod_2, share_prod_3]

# Reconstruct the secret product
secret_prod = ReconstructSecret(shares_prod_p1, shares_prod_p2)
print(f"\nReconstructed secret product: {secret_prod} ... Expected: ({x}*{y}) = {x * y}")

# Vector of secrets
vector_x = [random.randint(1, 100) for i in range(3)]
print("\nVector of secrets: ", vector_x)

# Split the vector
shares_vector_x_p1, shares_vector_x_p2, shares_vector_x_p3 = SplitVectorSecret(vector_x)
print("\nShares of party 1 for the vector: ", shares_vector_x_p1)
print("Shares of party 2 for the vector: ", shares_vector_x_p2)
print("Shares of party 3 for the vector: ", shares_vector_x_p3)

# Reconstruct the vector
recovered_vector_x = ReconstructVectorSecret(shares_vector_x_p1, shares_vector_x_p2)
print("\nRecovered vector: ", recovered_vector_x, "... Expected: ", vector_x)