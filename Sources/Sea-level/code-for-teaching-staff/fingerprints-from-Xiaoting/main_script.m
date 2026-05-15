%% Assignment for EPS 261

% Specify maximum degree to which spherical transformations should be done
maxdeg = 256;

% set up Gauss Legendre Grid
N = maxdeg; 
[x,w] = GaussQuad(N); % Gauss Quadrature points (x) and weights (w)
x_GL = acos(x)*180/pi - 90; % cos(x_GL) are Quadrature points for P(cos(theta))
lon_GL = linspace(0,360,2*N+1);
lon_GL = lon_GL(1:end-1);

lon_rad = lon_GL*pi/180;
colat_rad = (90-x_GL)*pi/180;

[lon_out,lat_out] = meshgrid(lon_GL,x_GL);

% load preloaded etopo (including ice)
load topo_Assignement

% interpolate topography grid onto Gauss Legendre Grid
topo_pres = interp2(lon_topo,lat_topo,topo_ice,lon_out,lat_out);

figure
pcolor(lon_out,lat_out,topo_pres)
shading flat
caxis([-7473 5731])

%% Do spherical harmonic transform of topo_pres into topo_lm
%call function spa2sph.m 
% note construct legendre polynomials with matlab function
% P_lm = legendre_me(l,cos(colat'*pi/180),'me');
topo_lm = spa2sph(topo_pres, maxdeg,lon_rad,colat_rad);


%% Do inverse spherical harmonic transform of topo_lm into topo_pres_new
%call function sph2spa.m

topo_pres_new = sph2spa(colat_rad,lon_rad,topo_lm,maxdeg);

%% Plot the new topography
% topo_pres_new should be a slightly smoother version of topo_pres

