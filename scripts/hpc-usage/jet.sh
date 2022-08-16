#!/bin/bash

set -ex

# We are on NOAA Jet
if ( ! eval module help > /dev/null 2>&1 ) ; then
    source /apps/lmod/lmod/init/bash
fi
module purge

module load contrib noaatools

shpcrpt -c jet -p h-nems

shpcrpt -c jet -p hfv3gfs
