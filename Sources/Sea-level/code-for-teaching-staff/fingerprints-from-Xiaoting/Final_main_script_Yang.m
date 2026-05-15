%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% EPS261 final assignment main script; written by Xiaoting Yang
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% *Eli: commented these out
%addpath /Users/xiaotingyang/Desktop/Spring2019/EPS261/Final/Matlab/
%addpath /Users/xiaotingyang/Documents/MATLAB/MetToolbox/

mycmap=jet; % *Eli: nclcmap('NCV_banded',100);
mycmap2=[0.8,0.8,0.8;
    0.3,0.4,1.0];
mycmap3=jet; % *Eli: nclcmap('CBR_coldhot',51);

% *Eli: changed these to local folders:
datadir='./';
plotdir='./Figures/';
targetdir='./Output/';

% read love numbers
myfile=fopen([datadir,'lovenumbers.txt'],'r'); formatSpec='%d %f %f %f';
lovenumbers=fscanf(myfile,formatSpec); fclose(myfile); clear myfile;

h_love=lovenumbers(2:4:(end-2)); k_love=lovenumbers(3:4:(end-1));
% density of water and ice, radius and mass of earth
rho_w=1025.0;
rho_i=910.0;
a=6371000.0; Me=6.0e24;

% Specify maximum degree to which spherical transformations should be done
maxdeg = 256; % *Eli: (64, 128 (default) or 256)

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
clf; hold on;
pcolor(lon_out,lat_out,topo_pres)
shading flat
load topo
colormap(mycmap)
colorbar; caxis([-7473 5731])
rectangle('Position',[300,60,40,22.31],'linewidth',1.2);
rectangle('Position',[min(min(lon_out)),min(min(lat_out)),max(max(lon_out))-min(min(lon_out)),-66-min(min(lat_out))],'linewidth',1.2);
xlabel('Longitude'); ylabel('Latitude');
xlim([min(min(lon_out)),max(max(lon_out))]); ylim([min(min(lat_out)),max(max(lat_out))]);
title(['Interpolated topography, deg=',num2str(N)]);
%% save as pdf/fig:
set(gcf, 'PaperUnits', 'inches'); set(gcf, 'PaperSize', [5 4]);
set(gcf, 'PaperPosition', [0 0 5 4]); % [left, bottom, width, height];
saveas(gcf,sprintf('Figures/topography.pdf'));
saveas(gcf,sprintf('Figures/topography.fig'));

% define C function
C=0*topo_pres;
C(topo_pres<=0.0)=1.0; % Ocean function

% plot ocean function
figure
clf; hold on;
pcolor(lon_out,lat_out,C)
shading flat
load topo
colormap(mycmap2); colorbar; caxis([0,1]);
contour(lon_out,lat_out,topo_pres,[0.0,0.0],'linewidth',1.2,'color','black')
xlabel('Longitude'); ylabel('Latitude');
xlim([min(lon_GL),max(lon_GL)]); ylim([min(x_GL),max(x_GL)]);
title(['Ocean function, deg=',num2str(N)]);
%% save as pdf/fig:
set(gcf, 'PaperUnits', 'inches'); set(gcf, 'PaperSize', [5 4]);
set(gcf, 'PaperPosition', [0 0 5 4]); % [left, bottom, width, height];
saveas(gcf,sprintf('Figures/ocean-mask.pdf'));
saveas(gcf,sprintf('Figures/ocean-mask.fig'));

% define unit ice change on Greenland, and Antartctica
% Ig=0*topo_pres; 
% for i=1:length(lon_GL)
%     for j=1:length(x_GL)
%         if lon_GL(i)>=300.0 && lon_GL(i)<=340.0 && x_GL(j)<=82.31 && x_GL(j)>=60.0 && topo_pres(j,i)>0.0
%             Ig(j,i)=-1.0;
%         end
%     end
% end
% 
% Ia=0*topo_pres;
% for i=1:length(lon_GL)
%     for j=1:length(x_GL)
%         if x_GL(j)<=-66.0 && topo_pres(j,i)>=0.0
%             Ia(j,i)=-1.0;
%         end
%     end
% end

load([datadir,'ice_masks.mat']);
Ig=interp2(lon_mask,lat_mask,Greenland_mask,lon_GL,x_GL);
Ia=interp2(lon_mask,lat_mask,WAIS_mask,lon_GL,x_GL);

clear lon_mask lat_mask Greenland_mask WAIS_mask;

figure
clf; hold on;
imagesc(lon_GL,x_GL,Ig)
set(gca,'Ydir','normal');
colormap(mycmap2); colorbar; caxis([0,1]);
contour(lon_out,lat_out,topo_pres,[0.0,0.0],'linewidth',1.2,'color','black')
rectangle('Position',[300,60,40,22.31],'linewidth',1.2);
xlabel('Longitude'); ylabel('Latitude');
xlim([min(lon_GL),max(lon_GL)]); ylim([min(x_GL),max(x_GL)]);
title(['Greenland Ice Change, deg=',num2str(N)]);
%% save as pdf/fig:
set(gcf, 'PaperUnits', 'inches'); set(gcf, 'PaperSize', [5 4]);
set(gcf, 'PaperPosition', [0 0 5 4]); % [left, bottom, width, height];
saveas(gcf,sprintf('Figures/Greenland-ice-change.pdf'));
saveas(gcf,sprintf('Figures/Greenland-ice-change.fig'));


figure
clf; hold on;
imagesc(lon_GL,x_GL,Ia)
set(gca,'Ydir','normal');
colormap(mycmap2); colorbar; caxis([0,1]);
contour(lon_out,lat_out,topo_pres,[0.0,0.0],'linewidth',1.2,'color','black')
rectangle('Position',[min(lon_GL),min(x_GL),max(lon_GL)-min(lon_GL),-66-min(x_GL)],'linewidth',1.2);
xlabel('Longitude'); ylabel('Latitude');
xlim([min(lon_GL),max(lon_GL)]); ylim([min(x_GL),max(x_GL)]);
title(['Antarctica Ice change, deg=',num2str(N)]);
%% save as pdf/fig:
set(gcf, 'PaperUnits', 'inches'); set(gcf, 'PaperSize', [5 4]);
set(gcf, 'PaperPosition', [0 0 5 4]); % [left, bottom, width, height];
saveas(gcf,sprintf('Figures/Antarctica-ice-change.pdf'));
saveas(gcf,sprintf('Figures/Antarctica-ice-change.fig'));


Ia=-Ia; Ig=-Ig;
% Do spherical harmonic transform of Delta_I for both continents
% and of the ocean function C
Ndeg=N;

Ia_coeff=Spheric_Harmonic_Decomp(Ia,x,w,lon_rad,Ndeg);
Ig_coeff=Spheric_Harmonic_Decomp(Ig,x,w,lon_rad,Ndeg);
C_coeff=Spheric_Harmonic_Decomp(C,x,w,lon_rad,Ndeg);

Ia_coeff00=Ia_coeff(1,1); Ig_coeff00=Ig_coeff(1,1); 
C_coeff00=C_coeff(1,1);
clear C_coeff;

Nround=3;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%      Greenland ice change
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% start interations for sea level equation, starting with a initial guess
Delta_S=-(rho_i/rho_w)*(Ig_coeff00/C_coeff00)*C;

for n=1:Nround
    Delta_S_coeff=Spheric_Harmonic_Decomp(Delta_S,x,w,lon_rad,Ndeg);
    Delta_SL_coeff=0*Delta_S_coeff;
    
    for l=1:(Ndeg+1)
        T=4*pi*a^3/(Me*(2*l-1));
        if l==1
            E=1;
        else
            E=1+k_love(l-1)-h_love(l-1);
        end
        Delta_SL_coeff(l,:)=T*E*(rho_i*Ig_coeff(l,:)+rho_w*Delta_S_coeff(l,:));
    end
    
    Delta_SL=Spheric_Harmonics_Reconstruct(Delta_SL_coeff,x,lon_rad,Ndeg);
    
    RO=Delta_SL.*C; 
    RO_coeff=Spheric_Harmonic_Decomp(RO,x,w,lon_rad,Ndeg); RO_coeff00=RO_coeff(1,1);
    clear RO_coeff;
    
    Delta_phi_g=-(rho_i*Ig_coeff00/(rho_w*C_coeff00))-(RO_coeff00/C_coeff00);
    Delta_S=(Delta_SL+Delta_phi_g).*C;
end

% calculate global average
Delta_S(C==0.0)=NaN;
% res=0.0; area=0.0;
% for i=1:length(lon_GL)
%     for j=1:length(x_GL)
%          if ~isnan(Delta_S(j,i))
%              res=res+Delta_S(j,i)*cos(x_GL(j)*pi/180);
%              area=area+cos(x_GL(j)*pi/180);
%          end
%     end
% end
avg=nanmean(Delta_S(:)); 
Delta_S=Delta_S/avg;

Delta_Sg=Delta_S; clear Delta_S;

figure; clf; hold on;
fill([lon_GL(1),lon_GL(end),lon_GL(end),lon_GL(1)],[x_GL(1),x_GL(1),x_GL(end),x_GL(end)],[0.8,0.8,0.8]);
h=imagesc(lon_GL,x_GL,Delta_Sg);
set(h,'AlphaData',~isnan(Delta_Sg));
set(gca,'Ydir','normal');
colormap(mycmap3); colorbar; caxis([-2,2]);
xlabel('Longitude'); ylabel('Latitude')
title('Greenland Ice Change')
xlim([min(lon_GL),max(lon_GL)]); ylim([x_GL(end),x_GL(1)]);
%% save as pdf/fig:
set(gcf, 'PaperUnits', 'inches'); set(gcf, 'PaperSize', [5 4]);
set(gcf, 'PaperPosition', [0 0 5 4]); % [left, bottom, width, height];
saveas(gcf,sprintf('Figures/sea-level-response-to-Greenland-ice-change.pdf'));
saveas(gcf,sprintf('Figures/sea-level-response-to-Greenland-ice-change.fig'));

% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% %      Antarctica ice change
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% % start interations for sea level equation, starting with a initial guess
% % start interations for sea level equation, starting with a initial guess
Delta_S=-(rho_i/rho_w)*(Ia_coeff00/C_coeff00)*C;

for n=1:Nround
    Delta_S_coeff=Spheric_Harmonic_Decomp(Delta_S,x,w,lon_rad,Ndeg);
    Delta_SL_coeff=0*Delta_S_coeff;
    
    for l=1:(Ndeg+1)
        T=4*pi*a^3/(Me*(2*l-1));
        if l==1
            E=1;
        else
            E=1+k_love(l-1)-h_love(l-1);
        end
        Delta_SL_coeff(l,:)=T*E*(rho_i*Ia_coeff(l,:)+rho_w*Delta_S_coeff(l,:));
    end
    
    Delta_SL=Spheric_Harmonics_Reconstruct(Delta_SL_coeff,x,lon_rad,Ndeg);
    
    RO=Delta_SL.*C; 
    RO_coeff=Spheric_Harmonic_Decomp(RO,x,w,lon_rad,Ndeg); RO_coeff00=RO_coeff(1,1);
    clear RO_coeff;
    
    Delta_phi_g=-(rho_i*Ia_coeff00/(rho_w*C_coeff00))-(RO_coeff00/C_coeff00);
    Delta_S=(Delta_SL+Delta_phi_g).*C;
end

% calculate global average
 Delta_S(C==0.0)=NaN;
% res=0.0; area=0.0;
% for i=1:length(lon_GL)
%     for j=1:length(x_GL)
%          if ~isnan(Delta_S(j,i))
%              res=res+Delta_S(j,i)*cos(x_GL(j)*pi/180);
%              area=area+cos(x_GL(j)*pi/180);
%          end
%     end
% end


avg=nanmean(Delta_S(:)); 
Delta_S=Delta_S/avg;
Delta_Sa=Delta_S; clear Delta_S;

%% *Eli: save for plotting in python:
Ice_mask_Greenland=Ig;
Ice_mask_Antarctica=Ia;
Delta_S_Greenland=Delta_Sg;
Delta_S_Antarctica=Delta_Sa;
lat_GL=x_GL;
ocean_mask=C;
save([targetdir,'fingerprinting-output-Greenland-and-Antarctica.mat'] ...
     ,'lon_GL','lat_GL','ocean_mask','topo_pres' ...
     ,'Delta_S_Greenland','Ice_mask_Greenland' ...
     ,'Delta_S_Antarctica','Ice_mask_Antarctica');


figure; clf; hold on;
fill([lon_GL(1),lon_GL(end),lon_GL(end),lon_GL(1)],[x_GL(1),x_GL(1),x_GL(end),x_GL(end)],[0.8,0.8,0.8]);
h=imagesc(lon_GL,x_GL,Delta_Sa);
set(h,'AlphaData',~isnan(Delta_Sa));
set(gca,'Ydir','normal');
colormap(mycmap3); colorbar; caxis([-2,2]);
xlabel('Longitude'); ylabel('Latitude')
title('West Antartctic Ice Change')
xlim([min(lon_GL),max(lon_GL)]); ylim([x_GL(end),x_GL(1)]);
%% save as pdf/fig:
set(gcf, 'PaperUnits', 'inches'); set(gcf, 'PaperSize', [5 4]);
set(gcf, 'PaperPosition', [0 0 5 4]); % [left, bottom, width, height];
saveas(gcf,sprintf('Figures/sea-level-response-to-west-Antarctica-ice-change.pdf'));
saveas(gcf,sprintf('Figures/sea-level-response-to-west-Antarctica-ice-change.fig'));



