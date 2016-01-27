#! /usr/bin/env sh
set -e

# Run this script, go to anaconda.org and find your new package, click on "Settings", then "Continuous Integration",
# and enable automatic building of your package whenever there is an upload to branch 'refs/heads/master'.  Be sure to
# use the label 'main', unless you want a 'dev' sub-channel.

PWD=`pwd`
DIR=`basename $PWD`

# anaconda-build trigger moble/${DIR}

export CONDA_NPY=110
CONDA_PYs=( 27 35 )

for CONDA_PY in "${CONDA_PYs[@]}"
do

    echo CONDA_PY=${CONDA_PY} CONDA_NPY=${CONDA_NPY}
    export CONDA_PY
    conda build --no-binstar-upload ${1:-.}
    conda server upload --force `conda build ${1:-.} --output`

done

# While we're at it, update PyPi too
python setup.py register sdist upload
