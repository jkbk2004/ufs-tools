#!/bin/bash

set -ex

module load modules
module use -a /opt/cray/ari/modulefiles
module use -a /opt/cray/pe/craype/default/modulefiles
source /etc/opt/cray/pe/admin-pe/site-config

module load hpcrpt

hpcrpt -p nggps_emc
