# 3MPC scheme with additive secret sharing
from __future__ import annotations
import random
import numpy as np # To check the dot product
import math
import time
from utils import signed_integer

# Decorator to measure execution time
def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.process_time()
        result = func(*args, **kwargs)
        end_time = time.process_time()
        print(f"Execution time: {end_time - start_time} seconds")
        return result
    return wrapper

# Parameters
vector_length = 10

# Use the infinity
inf = float("inf")

# Class to handle local shares
class MPC_Shares:
    def __init__(self, shares: list[any], order: int) -> MPC_Shares:
        self.order = order

        if type(shares[0]) == MPC_Shares:
            self.shares = None
            self.vector_shares = shares
            self.is_vector = True
        else:
            self.shares = shares
            self.vector_shares = None
            self.is_vector = False

    # Locally adding 2 secrets
    def LocalAddition(
            self, shares_obj_to_add: MPC_Shares
        ) -> MPC_Shares:

        # Check if object is not a vector
        assert(not self.is_vector), "Exception: the object should not be a vector."

        # Check if both shares objects have the same order
        assert (
            self.order == shares_obj_to_add.order
        ), "Exception: The shares objects must have the same order."

        shares_1 = self.shares
        shares_2 = shares_obj_to_add.shares
        shares_add = [inf, inf, inf]

        for s in range(3):
            if shares_1[s] != inf and shares_2[s] != inf:
                shares_add[s] = (
                    shares_1[s] + shares_2[s]
                ) % self.order

        # Convert the shares to MPC_Shares object
        shares_obj_add = MPC_Shares(shares_add, self.order)

        return shares_obj_add

    # Locally multiplying 2 secrets
    def LocalMultiplication(
        self, shares_obj_to_mult: MPC_Shares, r: int = 0
    ) -> int:

        # Check if object is not a vector
        assert not self.is_vector, "Exception: the object should not be a vector."

        # Check if both shares objects have the same order
        assert (
            self.order == shares_obj_to_mult.order
        ), "Exception: The shares objects must have the same order."

        shares_1 = self.shares
        shares_2 = shares_obj_to_mult.shares

        # Party ID
        for i in range(3):
            if shares_1[i] == inf:
                i = i - 1 % 3
                j = i - 1 % 3
                break

        # Compute the single share of the product belonging to party i
        share_prod = (
            (shares_1[i] + shares_1[j])
            * (shares_2[i] + shares_2[j])
            - (shares_1[j] * shares_2[j])
            + r
        ) % self.order

        return share_prod

    # Compute the product of two vectors of secrets in local
    def LocalDotProduct(
        self, shares_obj_to_dot_prod: MPC_Shares, r: int = 0
    ) -> int:

        # Check if object is a vector
        assert (
            self.is_vector and shares_obj_to_dot_prod.is_vector
        ), "Exception: The objects must contain shares of vectors."

        # Check if both shares objects have the same order
        assert (
            self.order == shares_obj_to_dot_prod.order
        ), "Exception: The shares objects must have the same order."

        shares_vector_1 = self.vector_shares
        shares_vector_2 = shares_obj_to_dot_prod.vector_shares

        products = []
        for i in range(len(shares_vector_1)):
            product = shares_vector_1[i].LocalMultiplication(shares_vector_2[i])
            products.append(product)

        share_dot_product = 0
        for i in range(len(products)):
            share_dot_product += products[i]

        return share_dot_product % self.order    

# Class to handle the Global MPC operations
class MPC:
    def __init__(self, k: int=16, order: int=None) -> MPC:
        if order is not None:
            k = math.log2(order)
            assert k.is_integer(), "Exception: The order must be a power of 2." 
            self.order = order
            self.k = k
        else: 
            self.order = 2**k
            self.k = k

    def SplitSecret(self, secret: int) -> tuple[MPC_Shares, MPC_Shares, MPC_Shares]:
        # Split the secret into 2 shares
        share1 = random.randint(1, self.order)
        share2 = random.randint(1, self.order)
        share3 = (secret - share1 - share2) % self.order

        # Distribute the shares among the parties
        shares_p1 = [share1, inf, share3]
        shares_p2 = [share1, share2, inf]
        shares_p3 = [inf, share2, share3]

        # Insantiating the MPC_Shares class
        shares_obj_p1 = MPC_Shares(shares_p1, self.order)
        shares_obj_p2 = MPC_Shares(shares_p2, self.order)
        shares_obj_p3 = MPC_Shares(shares_p3, self.order)

        return shares_obj_p1, shares_obj_p2, shares_obj_p3

    # Reconstruction of the secret. Only 2 parties are needed to reconstruct the secret
    def ReconstructSecret(self, shares_obj_A: MPC_Shares, shares_obj_B: MPC_Shares) -> int:

        sharesA = shares_obj_A.shares
        sharesB = shares_obj_B.shares
        secret = 0

        for s in range(3):
            if sharesA[s] == inf:
                secret += sharesB[s]
            elif sharesB[s] == inf:
                secret += sharesA[s]
            else:
                secret += sharesA[s]

        return secret % self.order

    # Split a vector of secrets
    def SplitVectorSecret(self, vector: list) -> tuple[MPC_Shares, MPC_Shares, MPC_Shares]:

        temp_shares_vector_p1 = []
        temp_shares_vector_p2 = []
        temp_shares_vector_p3 = []

        for i in range(len(vector)):
            shares = self.SplitSecret(vector[i])
            temp_shares_vector_p1.append(shares[0])
            temp_shares_vector_p2.append(shares[1])
            temp_shares_vector_p3.append(shares[2])

        shares_vector_p1 = MPC_Shares(temp_shares_vector_p1, self.order)
        shares_vector_p2 = MPC_Shares(temp_shares_vector_p2, self.order)
        shares_vector_p3 = MPC_Shares(temp_shares_vector_p3, self.order)

        return shares_vector_p1, shares_vector_p2, shares_vector_p3

    # Reconstruct a vector of secrets
    def ReconstructVectorSecret(self, sharesA: MPC_Shares, sharesB: MPC_Shares) -> list[int]:
        recovered_vector = []
        for i in range(len(sharesA.vector_shares)):
            secret = self.ReconstructSecret(sharesA.vector_shares[i], sharesB.vector_shares[i])
            recovered_vector.append(secret)
        return recovered_vector

    # Resharing the product of two secrets
    def Resharing(self, share1: int, share2: int, share3: int) -> tuple[MPC_Shares, MPC_Shares, MPC_Shares]:

        # Distribute the shares among the parties
        shares_p1 = [share1, inf, share3]
        shares_p2 = [share1, share2, inf]
        shares_p3 = [inf, share2, share3]

        # Cast the shares to MPC_Shares object
        shares_obj_p1 = MPC_Shares(shares_p1, self.order)
        shares_obj_p2 = MPC_Shares(shares_p2, self.order)
        shares_obj_p3 = MPC_Shares(shares_p3, self.order)

        return shares_obj_p1, shares_obj_p2, shares_obj_p3
##########################################################################################
##########################################################################################
##########################################################################################

def simple_test():
    # Instantiate the MPC class
    mpc = MPC(k=15)

    # Secrets to be shared
    x = random.randint(1, 100)
    y = random.randint(1, 100)

    print("Secrets to be shared: x = ", x, " y = ", y)

    # Split the secret
    shares_x_p1, shares_x_p2, shares_x_p3 = mpc.SplitSecret(x)
    shares_y_p1, shares_y_p2, shares_y_p3 = mpc.SplitSecret(y)
    print("\nShares of party 1 for x: ", shares_x_p1.shares)
    print("Shares of party 2 for x: ", shares_x_p2.shares)
    print("Shares of party 3 for x: ", shares_x_p3.shares)

    # Reconstruct the secret x
    secret_x = mpc.ReconstructSecret(shares_x_p1, shares_x_p2)
    print(
        f"\nRecovered secret x: {secret_x} = {shares_x_p1.shares[0]} + {shares_x_p2.shares[1]} + {shares_x_p3.shares[2]}",
        "... Expected: ",
        x,
    )

    # Reconstruct the secret y
    secret_y = mpc.ReconstructSecret(shares_y_p2, shares_y_p3)
    print(
        f"\nRecovered secret y: {secret_y} = {shares_y_p1.shares[0]} + {shares_y_p2.shares[1]} + {shares_y_p3.shares[2]}",
        "... Expected: ",
        y,
    )

    # Adding the secrets
    shares_add_p1 = shares_x_p1.LocalAddition(shares_y_p1)
    shares_add_p2 = shares_x_p2.LocalAddition(shares_y_p2)
    shares_add_p3 = shares_x_p3.LocalAddition(shares_y_p3)

    # Reconstruct the addition x + y
    secret_add = mpc.ReconstructSecret(shares_add_p1, shares_add_p2)
    print("\nRecovered secret x+y: ", secret_add, "... Expected: ", (x + y) % mpc.order)

    # Multiply the secrets
    share_prod_p1 = shares_x_p1.LocalMultiplication(shares_y_p1)
    share_prod_p2 = shares_x_p2.LocalMultiplication(shares_y_p2)
    share_prod_p3 = shares_x_p3.LocalMultiplication(shares_y_p3)

    # Reshare the product
    shares_prod_p1, shares_prod_p2, shares_prod_p3 = mpc.Resharing(share_prod_p1, share_prod_p2, share_prod_p3)

    # Reconstruct the secret product
    secret_prod = mpc.ReconstructSecret(shares_prod_p1, shares_prod_p2)
    print(f"\nReconstructed secret product: {secret_prod} ... Expected: ({x}*{y}) = {(x * y) % mpc.order}")

    # Two vectors of secrets
    vector_x = [random.randint(1, 100) for i in range(vector_length)]
    vector_y = [random.randint(1, 100) for i in range(vector_length)]
    print("\nVector of secrets x: ", vector_x)
    print("\nVector of secrets y: ", vector_y)

    # Split the vectors
    shares_vector_x_p1, shares_vector_x_p2, shares_vector_x_p3 = mpc.SplitVectorSecret(vector_x)
    shares_vector_y_p1, shares_vector_y_p2, shares_vector_y_p3 = mpc.SplitVectorSecret(vector_y)
    print("\nShares of party 1 for the vector x: ", [s.shares for s in shares_vector_x_p1.vector_shares])
    print("Shares of party 2 for the vector x: ", [s.shares for s in shares_vector_x_p2.vector_shares])
    print("Shares of party 3 for the vector x: ", [s.shares for s in shares_vector_x_p3.vector_shares])

    # Reconstruct the vectors
    recovered_vector_x = mpc.ReconstructVectorSecret(shares_vector_x_p1, shares_vector_x_p2)
    recovered_vector_y = mpc.ReconstructVectorSecret(shares_vector_y_p2, shares_vector_y_p3)
    print("\nRecovered vector x: ", recovered_vector_x, "... Expected: ", vector_x)
    print("\nRecovered vector y: ", recovered_vector_y, "... Expected: ", vector_y)

    # Compute the dot product
    share_dot_product_1 = shares_vector_x_p1.LocalDotProduct(shares_vector_y_p1)
    share_dot_product_2 = shares_vector_x_p2.LocalDotProduct(shares_vector_y_p2)
    share_dot_product_3 = shares_vector_x_p3.LocalDotProduct(shares_vector_y_p3)

    # Reshare the dot product
    shares_dot_product_p1, shares_dot_product_p2, shares_dot_product_p3 \
        = mpc.Resharing(share_dot_product_1, share_dot_product_2, share_dot_product_3)
        
    # Reconstruct the dot product
    dot_product = mpc.ReconstructSecret(shares_dot_product_p1, shares_dot_product_p2)
    print("\nDot product: ", dot_product, "... Expected: ", np.dot(vector_x, vector_y) % mpc.order)

# Testing the dot product with many vectors
# Decorator to measure execution time
@measure_time
def test_mpc(num_tests):
    # Instantiate the MPC class
    mpc = MPC(k=15)
    # For coung the number of errors
    num_errors = 0
    for _ in range(num_tests):
        vector_x = [random.randint(1, 100) for i in range(vector_length)]
        vector_y = [random.randint(1, 100) for i in range(vector_length)]

        shares_vector_x_p1, shares_vector_x_p2, shares_vector_x_p3 = mpc.SplitVectorSecret(vector_x)
        shares_vector_y_p1, shares_vector_y_p2, shares_vector_y_p3 = mpc.SplitVectorSecret(vector_y)

        share_dot_product_1 = shares_vector_x_p1.LocalDotProduct(shares_vector_y_p1)
        share_dot_product_2 = shares_vector_x_p2.LocalDotProduct(shares_vector_y_p2)
        share_dot_product_3 = shares_vector_x_p3.LocalDotProduct(shares_vector_y_p3)

        shares_dot_product_p1, shares_dot_product_p2, shares_dot_product_p3 \
            = mpc.Resharing(share_dot_product_1, share_dot_product_2, share_dot_product_3)

        dot_product = mpc.ReconstructSecret(shares_dot_product_p1, shares_dot_product_p3)
        real_dot_product = np.dot(vector_x, vector_y) % mpc.order

        if dot_product != real_dot_product:
            num_errors += 1

    print("\nNumber of errors: ", num_errors, " out of ", num_tests)

if "__name__" == "__main__":
    # Simple test
    simple_test()

    # Number of tests
    num_tests = 1000000
    test_mpc(num_tests)

