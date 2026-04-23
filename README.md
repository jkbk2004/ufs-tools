# ufs-tools
To collect the UFS experiment tool sets: config, shell, plot scripts, etc.

* ./rt-setup_cheyenne.sh -f feature/stoch_spp -u https://github.com/JeffBeck-NOAA/ufs-weather-model -e rt-982

* ./rt-setup_orion.sh -f feature/stoch_spp -u https://github.com/JeffBeck-NOAA/ufs-weather-model -e rt-982

* cd to rt-982/tests

* export RT_COMPILER=gnu or intel

* nohup ./rt.sh -e &

* nohup ./rt.sh -e -l rt_gnu.conf &
