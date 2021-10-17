#!/usr/bin/env python3

import sys
import argparse

from core import *

# http://primes.utm.edu/curios/page.php?number_id=4556
# Prime = (1597 * 34 ^ 2606) + 1
DEFAULT_PRIME = ((34 ** 2606) * 1597) + 1

def main():
    parser = argparse.ArgumentParser(description="Secret Splitter")
    parser.add_argument('--number', type=int, required=True,
           help='Number of shares to which the secret will be split')
    parser.add_argument('--threshold', type=int, required=True,
           help='Minimum number of shares needed to reconstruct the secret')
    parser.add_argument('--secret', type=int, required=True,
           help='The secret to be split (used only in the split mode)')
    parser.add_argument('--prime', type=int,
           default=DEFAULT_PRIME,
           help='Prime used as the basis of Galois field')

    args = parser.parse_args()

    shares = split_secret(args.secret,
                          args.number,
                          args.threshold,
                          args.prime)
    if shares == None:
        sys.stderr.write("Error: Unable to split secret!\n")
    else:
        print_shares(shares)

if __name__ == "__main__":
    main()
    sys.exit(0)
