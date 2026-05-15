%% Assignment for EPS 261
clear all; close all; clc

addpath /Users/xiaotingyang/Desktop/Spring2019/EPS261/MidTerm/
addpath /Users/xiaotingyang/Documents/MATLAB/MetToolbox/

plotdir='/Users/xiaotingyang/Desktop/Spring2019/EPS261/MidTerm/figures/';

mycmap=nclcmap('NCV_banded',100);
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
clf;
pcolor(lon_out,lat_out,topo_pres)
shading flat
load topo
colormap(mycmap)
colorbar; caxis([-7473 5731])
xlabel('Longitude'); ylabel('Latitude');
title(['Interpolated topography, deg=',num2str(N)]);


%% Do spherical harmonic transform of topo_pres into topo_lm
%call function spa2sph.m 
Ndeg=N;

U_coeff=Spheric_Harmonic_Decomp(topo_pres,x,w,lon_rad,Ndeg);  % a matrix containing all the coefficients


%% Do inverse spherical harmonic transform of topo_lm into topo_pres_new
%call function shp2spa.m

topo_recon=Spheric_Harmonics_Reconstruct(U_coeff,x,lon_rad,Ndeg); % reconstruct the topography

%% Plot the new topography
% topo_pres_new should be a slightly smoother version of topo_pres
figure
clf;
pcolor(lon_out,lat_out,topo_recon)
shading flat
load topo
colormap(mycmap)
colorbar; caxis([-7473 5731])
xlabel('Longitude'); ylabel('Latitude');
title(['Reconstructed topography, deg=',num2str(Ndeg)]);

%% make final version of figure for assignment submission
pos1=[0.1300,0.1100,0.3347,0.8150];
pos2=pos1; pos2(1)=pos2(1)+0.38;

pos_xlabel=zeros(4,1);
pos_xlabel(1)=pos1(1); pos_xlabel(2)=pos1(2)-0.02; 
pos_xlabel(3)=pos2(1)+pos2(3)-pos1(1); pos_xlabel(4)=0.012;

pos_ylabel=zeros(4,1);
pos_ylabel(1)=pos1(1)-0.02; pos_ylabel(2)=pos1(2);
pos_ylabel(3)=0.012; pos_ylabel(4)=pos1(4);

pos_title1=zeros(4,1);
pos_title1(1)=pos1(1); pos_title1(2)=pos1(2)+pos1(4);
pos_title1(3)=pos1(3); pos_title1(4)=0.012;

pos_title2=zeros(4,1);
pos_title2(1)=pos2(1); pos_title2(2)=pos2(2)+pos2(4);
pos_title2(3)=pos2(3); pos_title2(4)=0.012;

pos_colorbar=zeros(4,1); pos_colorbar(1)=pos2(1)+pos2(3)+0.004;
pos_colorbar(2)=pos2(2); pos_colorbar(3)=0.016; pos_colorbar(4)=pos2(4);

set(0,'defaulttextfontsize',28);
set(0,'defaultaxesfontsize',20);

fig=figure; fig.Renderer='painters'; clf;
subplot('Position',pos1);
pcolor(lon_out,lat_out,topo_pres);
shading flat
load topo
colormap(mycmap); caxis([-7473 5731]);

subplot('Position',pos2);
pcolor(lon_out,lat_out,topo_recon);
shading flat
load topo
set(gca,'yticklabel',[]);
colormap(mycmap); caxis([-7473 5731]);

colorbar('Position',pos_colorbar); colormap(mycmap); caxis([-7473,5731]);

temp=axes('Position',pos_xlabel,'visible','off'); temp.XLabel.Visible='on';
axes(temp); xlabel('Longtiude'); clear temp;

temp=axes('Position',pos_ylabel,'visible','off'); temp.YLabel.Visible='on';
axes(temp); ylabel('Latitude'); clear temp;

temp=axes('Position',pos_title1,'visible','off'); temp.Title.Visible='on';
axes(temp); title(['Original (N=',num2str(Ndeg),')']); clear temp;

temp=axes('Position',pos_title2,'visible','off'); temp.Title.Visible='on';
axes(temp); title(['Reconstructed (N=',num2str(Ndeg),')']); clear temp;

set(gcf,'PaperUnit','inches'); set(gcf,'PaperSize',[12,8]);
set(gcf,'PaperPosition',[0,0,12,8]);

saveas(gcf,[plotdir,'Topography_spheric_harnomics_N',num2str(Ndeg),'.pdf']);




 






