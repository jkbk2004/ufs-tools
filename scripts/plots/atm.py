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
#from matplotlib.colors import DivergingNorm
import netCDF4 as nc
import matplotlib.colors as colors
from matplotlib.colors import ListedColormap
import cmocean.cm as cmo
import numpy.ma as ma
from cartopy.examples.waves import sample_data

class MidpointNormalize(colors.Normalize):
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))

def cmap_map(function, cmap):
    """ Applies function (which should operate on vectors of shape 3: [r, g, b]), on colormap cmap.
    This routine will break any discontinuous points in a colormap.
    """
    cdict = cmap._segmentdata
    step_dict = {}
    # Firt get the list of points where the segments start or end
    for key in ('red', 'green', 'blue'):
        step_dict[key] = list(map(lambda x: x[0], cdict[key]))
    step_list = sum(step_dict.values(), [])
    step_list = np.array(list(set(step_list)))
    # Then compute the LUT, and apply the function to the LUT
    reduced_cmap = lambda step : np.array(cmap(step)[0:3])
    old_LUT = np.array(list(map(reduced_cmap, step_list)))
    new_LUT = np.array(list(map(function, old_LUT)))
    # Now try to make a minimal segment definition of the new LUT
    cdict = {}
    for i, key in enumerate(['red','green','blue']):
        this_cdict = {}
        for j, step in enumerate(step_list):
            if step in step_dict[key]:
                this_cdict[step] = new_LUT[j, i]
            elif new_LUT[j,i] != old_LUT[j, i]:
                this_cdict[step] = new_LUT[j, i]
        colorvector = list(map(lambda x: x + (x[1], ), this_cdict.items()))
        colorvector.sort()
        cdict[key] = colorvector

    return matplotlib.colors.LinearSegmentedColormap('colormap',cdict,1024)

def get_circle():
    """
    Compute a circle in axes coordinates, which we can use as a boundary
    for the map. We can pan/zoom as much as we like - the boundary will be
    permanently circular.
    """
    theta = np.linspace(0, 2*np.pi, 100)
    center, radius = [0.5, 0.5], 0.5
    verts = np.vstack([np.sin(theta), np.cos(theta)]).T

    return mpath.Path(verts * radius + center)

def get_circle():
    """
    Compute a circle in axes coordinates, which we can use as a boundary
    for the map. We can pan/zoom as much as we like - the boundary will be
    permanently circular.
    """
    theta = np.linspace(0, 2*np.pi, 100)
    center, radius = [0.5, 0.5], 0.5
    verts = np.vstack([np.sin(theta), np.cos(theta)]).T

    return mpath.Path(verts * radius + center)

def draw_map_subplots(ax,d):
    projection = d["projection"]
    ax.set_global()
    ax.add_feature(cartopy.feature.LAND,zorder=1)
    ax.add_feature(cartopy.feature.COASTLINE,zorder=1)
    ax.set_aspect('auto',adjustable=None)
    trans = ccrs.PlateCarree()
    if projection == 'PolarNorth':
        ax.set_extent([-180,180,60,90],crs=ccrs.PlateCarree())
        kw=dict(central_latitude=90,central_longitude=-45,true_scale_latitude=70)
    if projection == 'PolarSouth':
        ax.set_extent([-180,180,-90,-60],crs=ccrs.PlateCarree())
        kw=dict(central_latitude=-90,central_longitude=0,true_scale_latitude=-70)
    if projection == 'PolarSouth' or projection == 'PolarNorth':
        ax.gridlines()
        circle_value = get_circle()
        ax.set_boundary(circle_value, transform=ax.transAxes)
        trans = ccrs.Stereographic(**kw)
    return ax, trans

def set_projection_cmap(projection, cmap_in):
    if projection == 'PolarNorth': crs=ccrs.NorthPolarStereo()
    if projection == 'PolarSouth': crs=ccrs.SouthPolarStereo()
    if projection == 'Robinson'  : crs=ccrs.Robinson(central_longitude=-120)
    if cmap_in == "plt.cm.jet": cmap_=plt.cm.jet
    if cmap_in == "plt.cm.jet": cmap_=cmap_map(lambda x:x*.85,matplotlib.cm.jet)
    if cmap_in == "plt.cm.coolwarm": cmap_=plt.cm.coolwarm
    if cmap_in == "plt.cm.seismic": cmap_=plt.cm.seismic
    if cmap_in == "plt.cm.RdBu_r": cmap_=plt.cm.RdBu_r
    if cmap_in == "cmocean.cm.thermal": cmap_=cmocean.cm.thermal
    if cmap_in == "cmo.ice": cmap_=cmo.ice
    return crs, cmap_

def draw_colorbar(ax, cs, d, fig):
    cbar_label = d["cbar_label"]
    cbar_label_font = d["cbar_label_font"]
    cax,kw1=matplotlib.colorbar.make_axes([ax],location='bottom',shrink=0.6, pad=0.05, fraction=0.1)
    cbar=fig.colorbar(cs,cax=cax,**kw1)
    cbar.ax.tick_params(labelsize=cbar_label_font)
    cbar.set_label(cbar_label,size=6)
    
def draw_subplots(lat, lon, field, d, fig):
    level      = d["field_range"]
    figsize    = d["figsize"]
    projection = d["projection"]
    field_range= d["field_range"]
    cmap_in    = d["cmap"]
    
    crs, cmap_ = set_projection_cmap(projection, cmap_in)
    ax       = plt.subplot(111, projection=crs)
    ax,trans = draw_map_subplots(ax,d)
    levels= np.arange(field_range[0],field_range[1],field_range[2])
    min_  = levels[0]
    max_  = levels[-1] + field_range[2]
    
    cs = ax.contourf(lon,lat,field,norm=MidpointNormalize(midpoint=0.),cmap=cmap_,levels=levels,vmin=min_,vmax=max_,transform=trans)
    #cs = ax.contourf(lon,lat,field,cmap=cmap_,transform=trans)
    #if projection == 'PolarSouth' or projection == 'PolarNorth':
    #    cs = ax.contour(lon,lat,field,levels=[0.15],vmin=min_,vmax=max_,colors='y',linewidths=2.0,transform=trans)

    return ax, cs

def get_geofield(grid,fname,d,fieldname,field_dim):
    yh_var    = d["grid_vars"][0]
    xh_var    = d["grid_vars"][1]
    grid_type = d["grid_vars"][2]
    nc = xr.open_dataset(grid,decode_times=False)
    yh = nc[yh_var][:]; xh = nc[xh_var][:]
    nc.close()
    if grid_type == '1darray': [xh,yh]= np.meshgrid(xh, yh)

    nc=xr.open_dataset(fname,decode_times=False); field_= nc[fieldname][:]
    if field_dim=="3d":
        field = field_[0,:,:]+field_[1,:,:]+field_[2,:,:]+field_[3,:,:]+field_[4,:,:]
        print(np.mean(field))
    else:
        #field = field_
        field = field_[0,7,:,:]
    nc.close()
    return yh,xh,field

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-json', nargs='*', required=True, help='tmp.json')
    args = parser.parse_args()
    filename= str(args.json[0])
    
#1. read in json file to plot ------------------
    with open(filename) as files:
        datas = json.load(files)
        
    for d in datas:
        plot_type = d["plot_type"]
        fname     = d["files"]
        grid      = d["grid"]
        fontsize  = d["fontsize"]
        figsize   = d["figsize"]
        title     = d["title"]
        title_font= d["title_font"]
        output_fig= d["output_fig"]
        fieldname = d["fields"]
        fieldim   = d["field_dim"]
        
        yh,xh,field = get_geofield(grid,fname[0],d,fieldname[0],fieldim[0])
        #if 'field_scales' in d:
        #    field=field/d["field_scales"][0]
        #if 'field_mask' in d: field= ma.masked_greater(field, 1.0)

        if plot_type=="diff":
            yh_,xh_,field1=get_geofield(grid,fname[1],d,fieldname[1],fieldim[1])
            if 'field_scales' in d:
                field1=field1/d["field_scales"][1]
            if 'field_mask' in d: field1=ma.masked_greater(field1,1.0)
            field=np.array(field)-np.array(field1)


        field_range= d["field_range"]
        level      = d["field_range"]
        cmap_in    = d["cmap"]
        projection = d["projection"]
        levels= np.arange(field_range[0],field_range[1],field_range[2])
        min_  = levels[0]
        max_  = levels[1]#levels[-1] + field_range[2]

        fig = plt.figure(figsize=(8, 4))

        #crs=ccrs.NorthPolarStereo()
        #cmap_=cmo.ice

        crs, cmap_ = set_projection_cmap(projection, cmap_in)
        ax   = plt.subplot(111, projection=crs)
        ax1,trans = draw_map_subplots(ax,d)

        #cs1 = ax.contourf(xh,yh,field,cmap='gist_ncar',transform=trans,cmap='gist_ncar')
        cs1 = ax1.contourf(xh, yh, field, cmap=cmap_, levels=levels,vmin=min_,vmax=max_, transform=ccrs.PlateCarree())
        # first plot with default settings
        #ax1 = fig.add_subplot(121, projection=ccrs.NorthPolarStereo())
        #cs1 = ax1.contourf(xh, yh, field, transform=ccrs.PlateCarree(),
        #                   cmap='gist_ncar')

        #ax1.set_extent([0, 360, 0, 90], crs=ccrs.PlateCarree())
        #ax1.set_extent([-180, 180, 60, 90], crs=ccrs.PlateCarree())
        ax1.coastlines()
        ax1.set_title('Centred on 0$^\circ$ (default)')
        plt.show()



            
        #fig = plt.figure(figsize=figsize)
        #print(yh,xh,field)
        #ax, cs = draw_subplots(yh,xh,field,d,fig)
        #ax.set_title(title,fontsize=title_font)
        #draw_colorbar(ax,cs,d,fig)
        #xfig.savefig(output_fig)
        
        #plt.show()
