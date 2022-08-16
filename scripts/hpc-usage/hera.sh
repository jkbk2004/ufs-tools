#!/bin/bash

set -ex

# We are on NOAA Hera
if ( ! eval module help > /dev/null 2>&1 ) ; then
    source /apps/lmod/lmod/init/bash
fi
module purge

shpcrpt -c hera -p nems 
