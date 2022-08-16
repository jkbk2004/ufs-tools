import argparse
import numpy as np
import cmocean
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.path as mpath
import cartopy
import cartopy.crs as ccrs
import xarray as xr
import datetime
import json
from matplotlib.colors import DivergingNorm
import netCDF4

##############################################################################
def draw_map_subplots(ax):
  ax.set_global()
  ax.add_feature(cartopy.feature.LAND,zorder=1)
  ax.add_feature(cartopy.feature.COASTLINE,zorder=1)
  #ax.gridlines(draw_labels=True)
  ax.set_aspect('auto',adjustable=None)
  #ax.set_extent(extent)
  return ax

def draw_map_cartopy(ax):
  ax.gridlines()
  ax.add_feature( cartopy.feature.LAND,zorder=1,edgecolor='none', facecolor=[.5,.5,.5])
  ax.add_feature(cartopy.feature.OCEAN)
  ax.coastlines(color='black')
  #ax.gridlines(alpha='0.1',color='black')
  ax.set_aspect('auto',adjustable=None)

  return ax

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', nargs='*', required=True, help='tmp.json')
    args = parser.parse_args()
    filename= str(args.json[0])
    
#1. read in json file to plot ------------------
    with open(filename) as files:
        datas = json.load(files)

    d = datas[0]
    files  = d["files"]
    grid   = d["grid"]
    level  = d["field_range"]
    figsize= d["figsize"]
    fields = d["fields"]
    projection = d["projection"]
    title_ = d["title"]
    filename=d["output_fig"]

    nc= xr.open_dataset(files[0],decode_times=False); lat= nc['yh']; lon= nc['xh']
    [lon,lat]= np.meshgrid(lon,lat)

#    nc= xr.open_dataset(files[0],decode_times=False); field0_= np.array(nc[fields[0]])
    #nc= xr.open_mfdataset(files[0], parallel=True)
    #field0_= nc[fields[0]]

    file2read = netCDF4.Dataset(files[0],'r')
    field0_ = file2read.variables[fields[0]]      
    #; field0_= np.array(nc[fields[0]])
    #field0 = field0_[0,56,:,:]
    field0 = field0_[0,:,:]
    #print(field0)
    #field0 = np.ma.masked_where(field0 == 0., field0)
    
    if projection == 'Robinson':
      crs=ccrs.Robinson(central_longitude=-120)
    if projection == 'latlon':
      #crs=
      crs=ccrs.PlateCarree(central_longitude=-120)
    fig = plt.figure()
    ax  = plt.subplot(111, projection=crs)
    ax.coastlines(resolution='110m')
    #ax.gridlines()

    print(np.mean(field0),np.std(field0))
    print(np.max(field0),np.min(field0))
    title=title_
    stats='mean:'+str(np.mean(field0))+'\n std:'+str(np.std(field0))

    csst= ax.pcolormesh(lon,lat,field0, norm=DivergingNorm(0), cmap=plt.cm.seismic, transform=ccrs.PlateCarree(),vmin=level[0],vmax=level[2])
    cd0 = fig.colorbar(csst, ax=ax, orientation='horizontal', shrink=0.8, pad=0.03, aspect=50)#, extend="both")
    cd0.ax.locator_params(nbins=10)
    
    ax.set_title(title+'\n'+stats, fontsize=10)

    #ax.text(-180, -90, stats, ha='left', va='bottom', fontsize=9)
    fig.savefig(filename,dpi=150,facecolor='w',edgecolor='w',transparent=False)
    
    plt.show()

