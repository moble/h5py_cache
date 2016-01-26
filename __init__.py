# Copyright (c) 2016, Michael Boyle
# See LICENSE file for details: <https://github.com/moble/h5py_cache/blob/master/LICENSE>


def _find_next_prime(N):
    """Find next prime >= N"""
    def is_prime(n):
        if n % 2 == 0:
            return False
        i = 3
        while i * i <= n:
            if n % i:
                i += 2
            else:
                return False
        return True
    if N < 3:
        return 2
    if N % 2 == 0:
        N += 1
    for n in range(N, 2*N, 2):
        if is_prime(n):
            return n
    raise AssertionError("Failed to find a prime number between {0} and {1}...".format(N, 2*N))


def File(name, mode='a', chunk_cache_mem_size=1024**2, w0=0.75, n_cache_chunks=None, **kwds):
    """Create h5py File object with cache specification

    This function is basically just a wrapper around the usual h5py.File constructor,
    but accepts two additional keywords:

    Parameters
    ----------
    name : str
    mode : str
    **kwds : dict (as keywords)
        Standard h5py.File arguments, passed to its constructor
    chunk_cache_mem_size : int
        Number of bytes to use for the chunk cache.  Defaults to 1024**2 (1MB), which
        is also the default for h5py.File -- though it cannot be changed through the
        standard interface.
    w0 : float between 0.0 and 1.0
        Eviction parameter.  Defaults to 0.75.  "If the application will access the
        same data more than once, w0 should be set closer to 0, and if the application
        does not, w0 should be set closer to 1."
          --- <https://www.hdfgroup.org/HDF5/doc/Advanced/Chunking/>
    n_cache_chunks : int
        Number of chunks to be kept in cache at a time.  Defaults to the (smallest
        integer greater than) the square root of the number of elements that can fit
        into memory.  This is just used for the number of slots (nslots) maintained
        in the cache metadata, so it can be set larger than needed with little cost.

    """
    import sys
    import numpy as np
    import h5py
    name = name.encode(sys.getfilesystemencoding())
    open(name, mode).close()  # Just make sure the file exists
    if mode in [m+b for m in ['w', 'w+', 'r+', 'a', 'a+'] for b in ['', 'b']]:
        mode = h5py.h5f.ACC_RDWR
    else:
        mode = h5py.h5f.ACC_RDONLY
    if 'dtype' in kwds:
        bytes_per_object = np.dtype(kwds['dtype']).itemsize
    else:
        bytes_per_object = np.dtype(np.float).itemsize  # assume float as most likely
    if not n_cache_chunks:
        n_cache_chunks = int(np.ceil(np.sqrt(chunk_cache_mem_size / bytes_per_object)))
    nslots = _find_next_prime(100 * n_cache_chunks)
    propfaid = h5py.h5p.create(h5py.h5p.FILE_ACCESS)
    settings = list(propfaid.get_cache())
    settings[1:] = (nslots, chunk_cache_mem_size, w0)
    propfaid.set_cache(*settings)
    return h5py.File(h5py.h5f.open(name, flags=mode, fapl=propfaid), **kwds)
