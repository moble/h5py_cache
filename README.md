# h5py_cache <a href="https://travis-ci.org/moble/h5py_cache"><img align="right" hspace="3" alt="Status of automatic build and test suite" src="https://travis-ci.org/moble/h5py_cache.svg?branch=master"></a> <a href="https://github.com/moble/h5py_cache/blob/master/LICENSE"><img align="right" hspace="3" alt="Code distributed under the open-source MIT license" src="http://moble.github.io/spherical_functions/images/MITLicenseBadge.svg"></a>

Create h5py File object with specified cache

This is just a simple package for creating `h5py.File` objects with a given cache.  The cache interacts with `HDF5`
chunks in a complicated way, which can in some cases have a huge effect on the performance of `HDF5` I/O.  While
chunking is well documented and easily accessed through the `h5py` interface, the cache is not.  This package attempts
to make it easier to control the cache size.


## Usage

The main function in this little package is `h5py_cache.File`, which is just a wrapper for `h5py.File`, with a couple
extra arguments to set the cache.  (Note that the function name is capitalized, despite the fact that it is not a class
object.  This is just for calling consistency.)  The most important new argument is the `chunk_cache_mem_size`, which
is the size in bytes to be used for the chunk cache.  This defaults to `1024**2` (1MB), which is also the default used
by `h5py`.  However, you may wish to set it much larger, for example:

```python
import h5py_cache
with h5py_cache.File('test.h5', chunk_cache_mem_size=1024**3, 'a') as f:
    f.create_dataset(...)
```

Setting the cache size cannot be done with the usual "friendly" `h5py` interface; it requires the low-level interface,
which is how this function works under the hood.

For more details see the docstring of `h5py_cache.File`.


## Chunks

The `HDF5` format on which `h5py` is based uses "chunks" to store data on disk, which are basically subsets of the data.
A chunk is a contiguous segment of storage on disk.  Chunking happens at the level of the `dataset`.  Each `HDF5` file
can contain many `dataset`s (and even `group`s, which are collections of `dataset`s, much like directories of a
filesystem).  So when you create your `dataset`, you can tell `HDF5` how to chunk it.  The `dataset` will then consist
of a collection of chunks, and a collection of metadata, telling `HDF5` where the various chunks are stored on disk.

The access speed for `HDF5` files can depend extremely strongly on how these chunks are arranged.  In particular, if any
element is read from a chunk, the entire chunk must be read into memory.  So for example, if the data is a 2-D array,
chunked by rows, but you want to read a single column, each row must be read in its entirety, just to get that one
element from that chunk.  Thus, it would be better to chunk that data by column, if you are only going to read by
column.  Similarly, if you are only reading by row, it is best to chunk the data by column.

There's a lot of documentation on the web about chunking, one of the more useful of which is
[this reference](https://www.hdfgroup.org/HDF5/doc/Advanced/Chunking/).  Just be aware that if your `HDF5` reading or
writing is slow, chunking could potentially save you vast amounts of time.


## Cache

When a chunk of an `HDF5` file is read or written, that chunk is actually cached in memory.  By default, this cache is
just 1MB in size.  Typically, when the cache is full, the oldest chunk is ejected from memory to make room for the
newest one (though there is another behavior which will be discussed below).  Thus, if you need to use the same chunk
several times, you want it to stay in cache if possible.  Typically, this means that you will need to first set the
size of the cache to some particular value, related to your chunk size.


## An example: Transposing an array

My motivation for this project came when I had to transpose large data sets stored as `HDF5` files, which I now present
as an example.  These data sets can be of order 8GB in size, but my computer only ever has at most 12GB of free memory.
Thus, I can't do the transposition in memory; I need to read some of the input file, transpose it, and write to the
output file, then step through the entire data set in this way.  My naive first attempt involved reading the data
row-by-row, and writing column-by-column.  However, because of the access patterns I needed, the optimal chunk layouts
had to chunk along the rows for both input and output.  Thus, I would either have to read inefficiently, or write
inefficiently.  That naive first attempt took roughly 20 minutes for a 1GB file, which is hundreds of times slower than
simply copying a file of that size, which suggests that it should be possible to do far better.

To improve this, I adjusted my approach to work with groups of chunks at a time.  Basically, I would read a rectangular
subset of the input data, transpose it in memory, and then write that array out to file.  If `N` elements would fit in
memory at one time, I would make my chunks of size `sqrt(N)`, and read/write `sqrt(N)` of those chunks at a time.
(Here, I'm pretending that `sqrt(N)` is an integer, but you get the idea.)  Remembering that access to any element of a
chunk requires that entire chunk to be read/written, you can see that my new approach minimizes the number of separate
reads/writes I need to do.  The only problem is that this was roughly the same speed as before.

Eventually, I figured out that the reason was these chunks actually had to be read more than just once each, and the
underlying problem boiled down to the cache.  Each of my `sqrt(N)` chunks was being read in, and I had written a loop
to read all of them before writing their transposed version to disk.  But HDF5's cache was ejecting these from the cache
before the result could be written to disk.  That was because the default cache size that is created can only store
1MB worth of chunks.  (Which was not many in my case.)  So I needed to increase the chunk cache size.  This wasn't as
easy through the `h5py` interface as I would have hoped, but once I had done it, so that all `N` elements could fit in
the cache at one time, the transposition was blazing fast: 12 seconds, or about 100 times faster than my first attempt.



## Acknowledgments

The work of creating this code was supported in part by the Sherman Fairchild
Foundation and by NSF Grants No. PHY-1306125 and AST-1333129.
