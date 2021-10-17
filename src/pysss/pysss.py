#!/usr/bin/env python3
"""
pysss: Shamir's secret sharing algorithm in Python

Provides two methods:

  - split_secret()
  - reconstruct_secret()

"""

import time
import random

class MInt:
    """
    Represents an integer in Galois Field p
    """
    def __init__(self, num, prime):
        """Construct a integer n mod p"""
        self.num = num % prime
        self.prime = prime

    def __repr__(self):
        return "MInt(%s, %s)" % (self.num, self.prime)

    def __add__(self, other):
        assert isinstance(other, MInt)
        assert self.prime == other.prime
        return MInt(self.num + other.num, self.prime)

    def __sub__(self, other):
        assert isinstance(other, MInt)
        assert self.prime == other.prime
        return MInt(self.num - other.num, self.prime)

    def __mul__(self, other):
        assert isinstance(other, MInt)
        assert self.prime == other.prime
        return MInt(self.num * other.num, self.prime)

    def __div__(self, other):
        assert isinstance(other, MInt)
        assert self.prime == other.prime
        return self * other.inverse()

    def __truediv__(self, other):
        assert isinstance(other, MInt)
        assert self.prime == other.prime
        return self * other.inverse()

    def __pow__(self, other):
        assert isinstance(other, int)
        result = MInt(1, self.prime)
        for _ in range(0, other):
            result = result * self
        return result

    def inverse(self):
        """Compute the inverse of n modulo p
        Taken from: https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm
        """
        t = 0
        newt = 1
        r = self.prime
        newr = self.num
        while newr != 0:
            quotient = r // newr
            (t, newt) = (newt, t - quotient * newt)
            (r, newr) = (newr, r - quotient * newr)
        if r > 1:
            raise Exception(self + " is not invertible!")
        if t < 0:
            t = t + self.prime
        return MInt(t, self.prime)


def gen_unique_randoms(num, prime):
    """Generates a unique list of random numbers where the list has length
    num. Every generated value is in the range [1, prime-1]

    Args:
        num: The number of elements to be generated
        prime: The upper bound of the range to be generated.

    Returns:
        A list of random numbers where each number is in
        the range [1, prime-1].
    """

    elements = list()
    rng = random.SystemRandom(int(time.time()))
    generated = 0
    while generated != num:
        rnd = rng.randint(1, prime - 1)
        if rnd not in elements:
            elements.extend([rnd])
            generated += 1
    assert len(elements) == num
    return elements


def split_secret(secret, num_shares, threshold, prime):
    """Takes the given secret and splits it using Shamir's Secret Sharing
    Algorithm.

    Args:
        secret: The secret to be split
        num_shares: The number of shares for which the secret will be split
        threshold: The minimum number of shares needed to reconstruct the
                   secret
        prime: A prime number that is used as the basis of the Galois field
               in which all the arithmetic is done

    Returns:
        If successful, a list of tuples (int, int) containing the shares
        of the split secret. Otherwise, None.
    """

    if num_shares < 1 or threshold < 1 or threshold > num_shares:
        return None
    if num_shares >= prime or threshold >= prime or secret >= prime:
        return None

    shares = []

    # Get random (k-1) coefficients that define a k-th degree polynomial
    coeffs = [MInt(i, prime) for i in gen_unique_randoms(threshold - 1, prime)]

    # Get the x coordinates of the shares
    shares_xs = gen_unique_randoms(num_shares, prime)

    # Evaluate the polynomial for each x to produce the corresponding y
    for x in shares_xs:
        y = MInt(secret, prime)
        degree = 1
        x_m = MInt(x, prime)
        for coeff in coeffs:
            y += coeff * pow(x_m, degree)
            degree += 1
        shares.append((x_m.num, y.num))

    # Check if the shares are OK
    assert len(shares) == num_shares
    for share in shares:
        assert secret not in (share[0], share[1])
    return shares


def reconstruct_secret(shares, prime):
    """Reconstructs the secret using the computationally efficient approach
    explained in: https://en.wikipedia.org/wiki/Shamir%27s_Secret_Sharing

    Args:
        shares: The list of shares used to reconstruct the secret
        prime: The prime used to define the Galois field in which the shares
               were computed

    Returns:
        If given enough shares (i.e., >= threshold), the reconstructed secret.
    """

    assert isinstance(shares, list)
    assert isinstance(prime, int)

    for share in shares:
        assert prime > share[0] and prime > share[1]

    secret = MInt(0, prime)

    for i, s_i in enumerate(shares):
        x_i = MInt(s_i[0], prime)
        y_i = MInt(s_i[1], prime)
        product = MInt(1, prime)
        for j, s_j in enumerate(shares):
            x_j = MInt(s_j[0], prime)
            if j != i:
                product *= (x_j / (x_j - x_i))
        secret += (y_i * product)
    return secret.num
