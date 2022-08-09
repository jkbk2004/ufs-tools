#!/bin/bash

set -ex

module load contrib noaatools

shpcrpt -c orion -p nems

shpcrpt -c orion -p epic-ps
