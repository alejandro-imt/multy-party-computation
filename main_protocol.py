import numpy as np
import random
from MPC import MPC
from utils import signed_integer, mask_bits

# Parameters
k = 16
order = 2**k
vector_length = 10000
num_codes = 500
match_ratio = 0.01

def simple_test(debug=False):
    # Instatiate the MPC class
    mpc = MPC(k)

    # Generate 1 random code and 2 in database
    code1 = np.random.randint(0, 2, vector_length)
    code_db1 = np.random.randint(0, 2, vector_length)
    code_db2 = code1

    # Generate 1 random mask and 2 in database
    mask1 = np.random.randint(0, 2, vector_length)
    mask_db1= np.random.randint(0, 2, vector_length)
    mask_db2 = np.random.randint(0, 2, vector_length)

    # Masked codes
    masked_code1 = mask_bits(code1, mask1)
    masked_code_db1 = mask_bits(code_db1, mask_db1)
    masked_code_db2 = mask_bits(code_db2, mask_db2)

    if debug:
        print("Code 1: ", code1)
        print("Masked code 1: ", masked_code1)
        print("Code DB 1: ", code_db1)
        print("Masked code DB 1: ", masked_code_db1)
        print("Code DB 2: ", code_db2)
        print("Masked code DB 2: ", masked_code_db2)

    # Split thde vectors into shares
    shares_code1_p1, shares_code1_p2, shares_code1_p3 = mpc.SplitVectorSecret(masked_code1)
    shares_code_db1_p1, shares_code_db1_p2, shares_code_db1_p3 = mpc.SplitVectorSecret(masked_code_db1)
    shares_code_db2_p1, shares_code_db2_p2, shares_code_db2_p3 = mpc.SplitVectorSecret(masked_code_db2)

    if debug:
        # Printing the shares of each party
        print("\nShares of party 1 for code DB 1: ", [s.shares for s in shares_code_db1_p1.vector_shares])
        print("Shares of party 2 for code DB 1: ", [s.shares for s in shares_code_db1_p2.vector_shares])
        print("Shares of party 3 for code DB 1: ", [s.shares for s in shares_code_db1_p3.vector_shares])

    ##### Testing the dot product of code 1 and code DB 1
    print("\nTesting the dot product of code 1 and code DB 2")
    
    # Compte the dot product of codes 1 and DB 1
    dp_p1 = shares_code1_p1.LocalDotProduct(shares_code_db1_p1)
    dp_p2 = shares_code1_p2.LocalDotProduct(shares_code_db1_p2)
    dp_p3 = shares_code1_p3.LocalDotProduct(shares_code_db1_p3)
    print("Local dot products of code 1 and code DB 1: ", dp_p1, dp_p2, dp_p3)

    secret_dp_p1, secret_dp_p2, secret_dp_p3 = mpc.Resharing(dp_p1, dp_p2, dp_p3)
    dp = mpc.ReconstructSecret(secret_dp_p1, secret_dp_p3)
    dp_signed = signed_integer(dp, k)
    print("Dot product of code 1 and code DB 1: ", dp_signed)

    # Verify the dot product
    dp_real = np.dot(masked_code1, masked_code_db1)
    print("Reference dot product: ", dp_real)

    # Check if the dot product is more than the match ratio
    masks_and = np.bitwise_and(mask1, mask_db1)
    masks_ones = np.sum(masks_and)
    threshold = (1 - 2 * match_ratio) * masks_ones
    print("Threshold: ", threshold)
    if dp_signed > threshold:
        print("Codes Match")
    else:
        print("Codes Don't Match")

    ##### Now testing the dot product of code 1 and code DB 2 (which is the same as code 1)
    print("\nTesting the dot product of code 1 and code DB 2")

    # Compte the dot product of codes 1 and DB 2
    dp_p1 = shares_code1_p1.LocalDotProduct(shares_code_db2_p1)
    dp_p2 = shares_code1_p2.LocalDotProduct(shares_code_db2_p2)
    dp_p3 = shares_code1_p3.LocalDotProduct(shares_code_db2_p3)

    # Reshare the dot products
    secret_dp_p1, secret_dp_p2, secret_dp_p3 = mpc.Resharing(dp_p1, dp_p2, dp_p3)
    dp = mpc.ReconstructSecret(secret_dp_p1, secret_dp_p2)
    dp_signed = signed_integer(dp, k)
    print("Dot product of code 1 and code DB 2: ", dp_signed)

    # Verify the dot product
    dp_real = np.dot(masked_code1, masked_code_db2)
    print("Reference dot product: ", dp_real)

    # Check if the dot product is more than the match ratio
    masks_and = np.bitwise_and(mask1, mask_db2)
    masks_ones = np.sum(masks_and)
    threshold = (1 - 2 * match_ratio) * masks_ones
    print("Threshold: ", threshold)
    if dp_signed > threshold:
        print("Codes Match")
    else:
        print("Codes Don't Match")

def many_codes_test(num_codes, vector_length, match_index=None, debug=False):
    # Instatiate the MPC class
    mpc = MPC(k)

    # Generate many random codes in database
    codes_db = np.random.randint(0, 2, (num_codes, vector_length))

    # Select a code from the database to be the query code (forcing a coincidence)
    if match_index is not None:
        # check if the index is valid
        if match_index >= num_codes:
            raise ValueError("ERROR - Invalid match index")
        code_query = codes_db[match_index]
    else: # Else, generate a random query code
        code_query = np.random.randint(0, 2, vector_length)
        
    # Generate 1 random mask and 2 in database
    mask_query = np.random.randint(0, 2, vector_length)
    masks_db = np.random.randint(0, 2, (num_codes, vector_length))

    # Masked codes
    masked_code_query = mask_bits(code_query, mask_query)
    masked_codes_db = mask_bits(codes_db, masks_db)

    if debug:
        print("\nMasked code query: ", masked_code_query)
        print("Masked codes DB: ", masked_codes_db)
        print("Masked codes DB shape: ", masked_codes_db.shape)

    # Split the code query into shares
    shares_code_query_p1, shares_code_query_p2, shares_code_query_p3 = mpc.SplitVectorSecret(masked_code_query)

    # For saving the matches
    matches = []

    for i in range(num_codes):
        # Split the codes in database into shares
        shares_codes_db_p1, shares_codes_db_p2, shares_codes_db_p3 = mpc.SplitVectorSecret(masked_codes_db[i])

        # Compute the dot product of the code query and the code in database
        share_dp_p1 = shares_code_query_p1.LocalDotProduct(shares_codes_db_p1)
        share_dp_p2 = shares_code_query_p2.LocalDotProduct(shares_codes_db_p2)
        share_dp_p3 = shares_code_query_p3.LocalDotProduct(shares_codes_db_p3)

        # Reshare the dot products
        shares_dp_p1, shares_dp_p2, shares_dp_p3 = mpc.Resharing(share_dp_p1, share_dp_p2, share_dp_p3)

        # Reconstruct the dot products
        dp = mpc.ReconstructSecret(shares_dp_p1, shares_dp_p2)
        dp_signed = signed_integer(dp, k)
        dp_real = np.dot(masked_code_query, masked_codes_db[i])

        # Check if the dot product is equal to the reference dot product
        if dp_signed != dp_real:
            raise ValueError("ERROR - MPC dot product is not equal to the reference dot product")

        if debug:
            print("\nDot product of code query and code DB ", i, ": ", dp_signed)
            print("Reference dot product: ", dp_real)

        # Check if the dot product is more than the match ratio
        masks_and = np.bitwise_and(mask_query, masks_db[i])
        masks_ones = np.sum(masks_and)
        threshold = (1 - 2 * match_ratio) * masks_ones
        if dp_signed > threshold:
            matches.append([i, dp_signed, threshold])

        if debug:
            print("Threshold: ", threshold)
            if dp_signed > threshold:
                print("Codes Match. Index: ", i)
            else:
                print("Codes Don't Match. Index: ", i)

    print("\nMatches: ", matches)

# Main function
if __name__ == "__main__":
    # simple_test(debug=False)
    many_codes_test(num_codes, vector_length, match_index=100, debug=False)
