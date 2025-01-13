# Description: This script computes the hamming distance between two vectors
# defined over a binary field and a ring.
import numpy as np

# Parameters
k = 16
order = 2**k

# Compute the hamming distance between two vectors over a binary field
def hamming_distance_binary(bin_vec1, bin_vec2):
    # Check if the two vectors are of the same length
    if len(bin_vec1) != len(bin_vec2):
        raise ValueError("The two vectors must be of the same length")
    
    # Compute the hamming distance with numpy
    hamming_distance = np.sum(bin_vec1 != bin_vec2)
    return hamming_distance

# Hamming distance between two vectors defined over a ring
def hamming_distance_ring(vec1, vec2):
    # Check if the two vectors are of the same length
    if len(vec1) != len(vec2):
        raise ValueError("The two vectors must be of the same length")
    
    # Compute the hamming distance with numpy
    hamming_distance = np.sum(vec1) + np.sum(vec2) - 2 * np.dot(vec1, vec2)
    return hamming_distance

# Masked bit representation
def mask_bits(vector, mask):
    masked_vector = mask - 2*(np.bitwise_and(vector, mask))
    return masked_vector
#############################################################################

# Testing the dot product of masked codes
vector_length = 12000
match_ratio = 0.001
    
# Two random codes
code1 = np.random.randint(0, 2, vector_length)
code2 = np.random.randint(0, 2, vector_length)

# Two random masks
mask1 = np.random.randint(0, 2, vector_length)
mask2 = np.random.randint(0, 2, vector_length)

# Masked codes
masked_code1 = mask_bits(code1, mask1)
masked_code2 = mask_bits(code2, mask2)

# Dot product
dp = np.dot(masked_code1, masked_code2)

print("Code 1: ", code1)
print("Masked code 1: ", masked_code1)
print("Code 2: ", code2)
print("Masked code 2: ", masked_code2)
print("\nDot product: ", dp)

# Comparison formula
masks_and = np.bitwise_and(mask1, mask2)
mask_ones = np.sum(masks_and)
comparision_reference = (1-2*match_ratio)*mask_ones
print("ml = ", mask_ones)
print("Reference: ", comparision_reference)

if dp > comparision_reference:
    print("\tMATCH")
else:
    print("\tNo match")

# Running the test for a large number of times
num_tests = 10000
num_matches = 0

for _ in range(num_tests):
    
    code1 = np.random.randint(0, 2, vector_length)
    code2 = np.random.randint(0, 2, vector_length)
    
    mask1 = np.random.randint(0, 2, vector_length)
    mask2 = np.random.randint(0, 2, vector_length)
    
    masked_code1 = mask_bits(code1, mask1)
    masked_code2 = mask_bits(code2, mask2)
    
    dp = np.dot(masked_code1, masked_code2)
    masks_and = np.bitwise_and(mask1, mask2)
    mask_ones = np.sum(masks_and)
    comparision_reference = (1-2*match_ratio)*mask_ones
    
    if dp > comparision_reference:
        # if dot_product < mask_ones:
        num_matches += 1
        # break
print("\nNumber of matches ", num_matches)
