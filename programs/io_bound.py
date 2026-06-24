"""
Syscall / I/O-bound workload: the program spends almost all of its time issuing
system calls (write + fsync) rather than computing. Each system call, and
especially fsync (which forces the data down to the storage layer), causes the
guest to trap out of guest mode into the hypervisor / host (a "VM exit").

This is the kind of program expected to show a PERFORMANCE PENALTY on a virtual
CPU, because every VM exit costs hundreds to thousands of extra cycles compared
to running the same syscall directly on the host kernel.

The amount of work is deterministic: exactly `workload` write+fsync iterations.
"""

import os
import tempfile


def hammer_syscalls(iterations: int) -> int:
    """
    Do `iterations` rounds of: write a small block to a real file and fsync it.
    fsync is a privileged, blocking syscall that the hypervisor must mediate, so
    it is a heavy source of VM exits. Returns total bytes written.
    """
    block = b"x" * 64
    total = 0
    # Use a real on-disk temp file (NOT /dev/null) so fsync has something to do.
    fd, path = tempfile.mkstemp(prefix="iobench_")
    try:
        for _ in range(iterations):
            os.lseek(fd, 0, os.SEEK_SET)  # syscall
            os.write(fd, block)           # syscall
            os.fsync(fd)                  # heavy syscall -> VM exit + flush
            total += len(block)
    finally:
        os.close(fd)
        os.unlink(path)
    return total


def run(workload: int) -> int:
    """
    Entry point used by benchmark.py.

    `workload` is the number of write+fsync iterations. Larger -> more syscalls.
    Returns total bytes written so native and guest can be compared.
    """
    return hammer_syscalls(workload)


# Default workload sized to take roughly a couple of seconds; fsync is slow, so
# this is much smaller than the CPU workload.
DEFAULT_WORKLOAD = 10_000


if __name__ == "__main__":
    import sys

    n = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_WORKLOAD
    print(f"{n} write+fsync rounds wrote {run(n)} bytes")
