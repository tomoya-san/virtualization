"""
CPU-bound workload: pure computation, no system calls, no I/O, no growing
memory. This is the kind of program expected to run at NEAR-NATIVE speed on a
hardware-assisted virtual CPU, because the guest executes instructions directly
on the physical CPU and almost never needs to trap to the hypervisor (no VM
exits in the hot loop).

The workload counts prime numbers up to N by trial division. It is deterministic
(the result only depends on `workload`) so the native run and the guest run do
exactly the same amount of arithmetic.
"""


def count_primes(limit: int) -> int:
    """Count primes in [2, limit) using trial division. Pure integer math."""
    if limit < 3:
        return 0
    count = 1  # account for 2
    n = 3
    while n < limit:
        is_prime = True
        i = 3
        while i * i <= n:
            if n % i == 0:
                is_prime = False
                break
            i += 2
        if is_prime:
            count += 1
        n += 2
    return count


def run(workload: int) -> int:
    """
    Entry point used by benchmark.py.

    `workload` is the upper bound for prime counting. Larger -> more CPU work.
    Returns the result so the caller can sanity-check that native and guest
    produced identical output.
    """
    return count_primes(workload)


# Default workload sized to take roughly a couple of seconds in CPython.
DEFAULT_WORKLOAD = 200_000


if __name__ == "__main__":
    import sys

    n = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_WORKLOAD
    print(f"primes below {n}: {run(n)}")
