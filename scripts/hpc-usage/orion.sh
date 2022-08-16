#!/bin/bash

set -ex

# We are on Orion
if ( ! eval module help > /dev/null 2>&1 ) ; then
    source /apps/lmod/init/bash
fi
module purge

module load contrib noaatools

shpcrpt -c orion -p nems

shpcrpt -c orion -p epic-ps
