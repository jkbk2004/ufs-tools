#!/bin/bash

set -ex

# We are on NOAA Jet
#if ( ! eval module help > /dev/null 2>&1 ) ; then
#    source /apps/lmod/lmod/init/bash
#fi

/apps/local/bin/shpcrpt -c jet -p h-nems | tee jet-h-nems.log

/apps/local/bin/shpcrpt -c jet -p hfv3gfs | tee jet-hfv3gfs.log
