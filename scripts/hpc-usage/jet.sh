#!/bin/bash

set -ex

module load contrib noaatools

shpcrpt -c jet -p h-nems

shpcrpt -c jet -p hfv3gfs
