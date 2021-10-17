#!/usr/bin/env python3

import os
import sys
import time
import random
import unittest

sys.path.insert(0, os.path.abspath('../src'))

from pysss import MInt, split_secret, reconstruct_secret


class TestMInt(unittest.TestCase):

    def setUp(self):
        self.unity =  MInt(1, 23)
        self.zero =  MInt(0, 23)
        self.a = MInt(7, 23)
        self.b = MInt(20, 23)

    def test_add(self):
        self.assertEqual( (self.a + self.b).num, 4)

    def test_sub(self):
        self.assertEqual( (self.a - self.b).num, 10)

    def test_inv(self):
        self.assertEqual( (self.a * (self.unity / self.a)).num, 1)
        self.assertEqual( (self.b * (self.unity / self.b)).num, 1)

    def test_pow(self):
        self.assertEqual( pow(self.b, 3).num, 19)

class TestShamir(unittest.TestCase):

    def setUp(self):
        self.rng = random.SystemRandom(int(time.time()))

    def test_shamir1(self):
        # 1000 digit prime (3322 bits)
        # Source: http://primes.utm.edu/curios/page.php?number_id=4032
        # Prime = (85 * (10 ^ 999) + 41) / 9 + 4040054550
        prime = ((((10 ** 999) * 85) + 41) // 9) + 4040054550
        secret = self.rng.getrandbits(1024) # length of secret in bits
        print("\tsecret: " + str(hex(secret)))
        num_shares = 9
        threshold = 5

        shares = split_secret(secret,
                              num_shares,
                              threshold,
                              prime)
        self.assertIsNotNone(shares)
        self.assertEqual(len(shares), num_shares)

        for s in shares:
            self.assertTrue(isinstance(s[0], int))
            self.assertTrue(isinstance(s[1], int))
            self.assertNotEqual(s[0], secret)
            self.assertNotEqual(s[1], secret)

        points = shares[0:threshold]
        new_secret = reconstruct_secret(points, prime)
        self.assertEqual(new_secret, secret)

        points = shares[0:threshold+1]
        new_secret = reconstruct_secret(points, prime)
        self.assertEqual(new_secret, secret)

        points = shares[0:num_shares]
        new_secret = reconstruct_secret(points, prime)
        self.assertEqual(new_secret, secret)

        points = shares[0:threshold-1]
        new_secret = reconstruct_secret(points, prime)
        self.assertNotEqual(new_secret, secret)

        points = shares[0:threshold-2]
        new_secret = reconstruct_secret(points, prime)
        self.assertNotEqual(new_secret, secret)

    def test_shamir2(self):

        # http://primes.utm.edu/curios/page.php?number_id=4556
        # Prime = (1597 * 34 ^ 2606) + 1
        prime = (1597 * (34 ** 2606)) + 1
        secret = 123
        print("\tsecret: " + str(hex(secret)))
        num_shares = 5
        threshold = 3

        shares = split_secret(secret,
                              num_shares,
                              threshold,
                              prime)
        self.assertIsNotNone(shares)
        self.assertEqual(len(shares), num_shares)

        for s in shares:
            self.assertTrue(isinstance(s[0], int))
            self.assertTrue(isinstance(s[1], int))
            self.assertNotEqual(s[0], secret)
            self.assertNotEqual(s[1], secret)

        points = shares[0:threshold]
        new_secret = reconstruct_secret(points, prime)
        self.assertEqual(new_secret, secret)

        points = shares[0:threshold+1]
        new_secret = reconstruct_secret(points, prime)
        self.assertEqual(new_secret, secret)

        points = shares[0:num_shares]
        new_secret = reconstruct_secret(points, prime)
        self.assertEqual(new_secret, secret)

        points = shares[0:threshold-1]
        new_secret = reconstruct_secret(points, prime)
        self.assertNotEqual(new_secret, secret)

        points = shares[0:threshold-2]
        new_secret = reconstruct_secret(points, prime)
        self.assertNotEqual(new_secret, secret)

if __name__ == "__main__":
    unittest.main()

