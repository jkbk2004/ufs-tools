#!/bin/bash

set -ex

# We are on GAEA.
if ( ! eval module help > /dev/null 2>&1 ) ; then
  # We cannot simply load the module command.  The GAEA
  # /etc/profile modifies a number of module-related variables
  # before loading the module command.  Without those variables,
  # the module command fails.  Hence we actually have to source
  # /etc/profile here.
  source /etc/profile
  __ms_source_etc_profile=yes
else
  __ms_source_etc_profile=no
fi
module purge
# clean up after purge
unset _LMFILES_
unset _LMFILES_000
unset _LMFILES_001
unset LOADEDMODULES
module load modules
if [[ -d /opt/cray/ari/modulefiles ]] ; then
  module use -a /opt/cray/ari/modulefiles
fi
if [[ -d /opt/cray/pe/ari/modulefiles ]] ; then
  module use -a /opt/cray/pe/ari/modulefiles
fi
if [[ -d /opt/cray/pe/craype/default/modulefiles ]] ; then
  module use -a /opt/cray/pe/craype/default/modulefiles
fi
if [[ -s /etc/opt/cray/pe/admin-pe/site-config ]] ; then
  source /etc/opt/cray/pe/admin-pe/site-config
fi
if [[ "$__ms_source_etc_profile" == yes ]] ; then
  source /etc/profile
  unset __ms_source_etc_profile
fi

module load hpcrpt

hpcrpt -p nggps_emc
