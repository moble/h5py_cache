import os.path
import shutil
import tempfile
import numpy as np
from h5py_cache import File, _find_next_prime
import pytest

# mdc: Number of metadata objects
# rdcc: Number of raw data chunks
# rdcc_nbytes: Size of raw data cache
# rdcc_w0: Preemption policy for data cache


def test_defaults():
    chunk_cache_mem_size = 1024**2
    w0 = 0.75
    n_cache_chunks = int(np.ceil(np.sqrt(chunk_cache_mem_size / 8)))
    nslots = _find_next_prime(100 * n_cache_chunks)
    d = tempfile.mkdtemp()
    try:
        with File(os.path.join(d, 'defaults.h5')) as f:
            mdc, rdcc, rdcc_nbytes, rdcc_w0 = f.id.get_access_plist().get_cache()
            assert mdc == 0
            assert rdcc == nslots
            assert rdcc_nbytes == chunk_cache_mem_size
            assert rdcc_w0 == w0
    finally:
        shutil.rmtree(d)


def test_args():
    chunk_cache_mem_size = 8*1024**2
    w0 = 0.25
    n_cache_chunks = 8000
    nslots = _find_next_prime(100 * n_cache_chunks)
    d = tempfile.mkdtemp()
    try:
        with File(os.path.join(d, 'args.h5'), chunk_cache_mem_size=chunk_cache_mem_size,
                  w0=w0, n_cache_chunks=n_cache_chunks) as f:
            mdc, rdcc, rdcc_nbytes, rdcc_w0 = f.id.get_access_plist().get_cache()
            assert mdc == 0
            assert rdcc == nslots
            assert rdcc_nbytes == chunk_cache_mem_size
            assert rdcc_w0 == w0
    finally:
        shutil.rmtree(d)


def test_readonly():
    d = tempfile.mkdtemp()
    try:
        for mode in ['r', 'rb']:
            # Create the file first
            with File(os.path.join(d, 'readonly_{0}.h5'.format(mode)), mode='a') as f:
                f.create_dataset('x', data=np.empty(shape=(2, 3), dtype=float))
            # Now reopen it in read-only mode and try to create another dataset
            with File(os.path.join(d, 'readonly_{0}.h5'.format(mode)), mode=mode) as f:
                with pytest.raises(ValueError) as excinfo:
                    f.create_dataset('y', data=np.empty(shape=(2, 3), dtype=float))
                assert "No write intent on file" in str(excinfo.value)
    finally:
        shutil.rmtree(d)

