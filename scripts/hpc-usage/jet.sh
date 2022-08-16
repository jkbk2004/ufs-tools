#!/bin/bash

set -ex

# We are on NOAA Jet
if ( ! eval module help > /dev/null 2>&1 ) ; then
    source /apps/lmod/lmod/init/bash
fi
module purge

/apps/local/bin/shpcrpt -c jet -p h-nems

/apps/local/bin/shpcrpt -c jet -p hfv3gfs
