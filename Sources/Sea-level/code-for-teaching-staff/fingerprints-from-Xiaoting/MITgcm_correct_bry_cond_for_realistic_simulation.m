%% Correct the boundary conditions for Indian Ocean
addpath /Users/xiaotingyang/Documents/MATLAB/GSW/
addpath /Users/xiaotingyang/Documents/MATLAB/GSW/library/
addpath /Users/xiaotingyang/Documents/MATLAB/GSW/pdf/
addpath /Users/xiaotingyang/Documents/MATLAB/GSW/html/
addpath /Users/xiaotingyang/Documents/MATLAB/GSW/thermodynamics_from_t/

addpath /Users/xiaotingyang/Documents/MATLAB/MetToolbox/
mycmap=nclcmap('CBR_coldhot',11);
mycmap2=nclcmap('GMT_panoply',16);

casename='DEBC03_Indian_monthly_bry_cond_small';
datadir=['/Users/xiaotingyang/Desktop/DeepEasternBoundaryCurrent/MITgcm/',casename,'/input_prep/'];

V0=0.05; Z0=-3000.0; sig_z=750.0; sig_x=0.5; % in degree
rho0=1000.0; g=9.8; 

grdfile=netcdf.open([datadir,'grid_global.nc'],'NOWRITE');
varid=netcdf.inqVarID(grdfile,'X');
X=double(netcdf.getVar(grdfile,varid));
varid=netcdf.inqVarID(grdfile,'Y');
Y=double(netcdf.getVar(grdfile,varid));
varid=netcdf.inqVarID(grdfile,'RC');
RC=double(netcdf.getVar(grdfile,varid));
varid=netcdf.inqVarID(grdfile,'dxC');
dxC=double(netcdf.getVar(grdfile,varid));
varid=netcdf.inqVarID(grdfile,'drC');
drC=double(netcdf.getVar(grdfile,varid));
varid=netcdf.inqVarID(grdfile,'drF');
drF=double(netcdf.getVar(grdfile,varid));
varid=netcdf.inqVarID(grdfile,'fCori');
fCori=double(netcdf.getVar(grdfile,varid));
varid=netcdf.inqVarID(grdfile,'HFacC');
mask=double(netcdf.getVar(grdfile,varid));
netcdf.close(grdfile);

Nx=length(X); Ny=length(Y); Nz=length(RC);

% read bathymetry
bathfile=fopen([datadir,'bathymetry.bin'],'r','b');
bath=fread(bathfile,[Nx,Ny],'real*8');
fclose(bathfile); clear bathfile;

figure; clf;
plot(X,squeeze(bath(:,1)),'bo-','linewidth',1.2,'markersize',6);
xlabel('Longitude'); ylabel('Depth'); title('South bathymetry');

figure; clf;
plot(X,squeeze(bath(:,end)),'bo-','linewidth',1.2,'markersize',6);
xlabel('Longitude'); ylabel('Depth'); title('North bathymetry');

% define velocity
V_north=zeros(Nx,Nz); V_south=zeros(Nx,Nz);

% for the northern boundary
profile=squeeze(bath(:,end));
i0=Nx;
for i=(Nx-1):(-1):1
    if profile(i)<=Z0 && profile(i+1)>=Z0
        i0=i; break;
    end
end

for i=1:Nx
    for k=1:Nz
        V_north(i,k)=-V0*exp(-(X(i)-X(i0))^2/sig_x^2)*exp(-(RC(k)-profile(i0))^2/sig_z^2);
    end
end

% for the southern boundary
profile=squeeze(bath(:,1));
i0=Nx;
for i=(Nx-1):(-1):1
    if profile(i)<=Z0 && profile(i+1)>=Z0
        i0=i; break;
    end
end

for i=1:Nx
    for k=1:Nz
        V_south(i,k)=-V0*exp(-(X(i)-X(i0))^2/sig_x^2)*exp(-(RC(k)-profile(i0))^2/sig_z^2);
    end
end

% plot velocities
figure; clf; hold on;
contourf(X,RC,V_north',11,'edgecolor','None'); 
colormap(mycmap); colorbar; caxis([-V0,V0]);
plot(X,squeeze(bath(:,end)),'ko-','linewidth',1.2,'markersize',6);
title('North boundary V')

figure; clf; hold on;
contourf(X,RC,V_south',11,'edgecolor','None'); 
colormap(mycmap); colorbar; caxis([-V0,V0]);
plot(X,squeeze(bath(:,1)),'ko-','linewidth',1.2,'markersize',6);
title('South boundary V')

% read western boundary temperature and salinity profiles
oldfile=fopen([datadir,'Temp_west_boundary.bin'],'r','b');
Temp=fread(oldfile,[Ny,Nz],'real*8');
fclose(oldfile); clear oldfile;

oldfile=fopen([datadir,'Salt_west_boundary.bin'],'r','b');
Salt=fread(oldfile,[Ny,Nz],'real*8');
fclose(oldfile); clear oldfile;

Temp=squeeze(mean(Temp,1)); Salt=squeeze(mean(Salt,1));

figure; clf; 
plot(Temp,RC,'bo-','linewidth',1.2,'markersize',6);
xlabel('Temp.'); ylabel('Depth'); title('Temperature profile');

figure; clf; 
plot(Salt,RC,'bo-','linewidth',1.2,'markersize',6);
xlabel('Salt.'); ylabel('Depth'); title('Salinity profile');

% calculate density profile
pres=zeros(1,Nz); rho=zeros(1,Nz);
pres1=zeros(1,Nz+1); Temp1=zeros(1,Nz+1); Salt1=zeros(1,Nz+1);

Temp1(2:(end-1))=0.5*(Temp(1:(end-1))+Temp(2:end)); Temp1(1)=Temp1(2); Temp1(end)=Temp1(end-1);
Salt1(2:(end-1))=0.5*(Salt(1:(end-1))+Salt(2:end)); Salt1(1)=Salt1(2); Salt1(end)=Salt1(end-1);

pres(1)=rho0*g*(0-RC(1))/10000.0; rho(1)=gsw_rho(gsw_SR_from_SP(Salt(1)),Temp(1),pres(1));
pres1(1)=0.0; pres1(2)=pres1(1)+rho(1)*g*drF(1)/10000.0;

for k=2:length(Temp)
    r=gsw_rho(gsw_SR_from_SP(Salt1(k)),Temp1(k),pres1(k));
    pres(k)=pres(k-1)+r*g*drC(k)/10000.0;
    rho(k)=gsw_rho(gsw_SR_from_SP(Salt(k)),Temp(k),pres(k));
    pres1(k+1)=pres1(k)+rho(k)*g*drF(k)/10000.0;
end

figure; clf;
plot(rho,RC,'bo-','linewidth',1.2,'markersize',6);
xlabel('Density'); ylabel('Depth'); title('Density profile');

figure; clf;
plot(pres,RC,'bo-','linewidth',1.2,'markersize',6);
xlabel('Pressure'); ylabel('Depth'); title('Pressure profile');



% calculate temperature and salinity 
% north boundary
V=V_north; f=fCori(1,end); dX=dxC(1,end);
Vz=zeros(Nx,Nz+1);
for k=2:(Nz-1)
    Vz(:,k)=(V(:,k)-V(:,k-1))/drC(k);
end
Vz(:,1)=Vz(:,2); Vz(:,end)=Vz(:,end-1);
Vz=0.5*(Vz(:,1:(end-1))+Vz(:,2:end)); Vz=0.5*(Vz(1:(end-1),:)+Vz(2:end,:));

T=zeros(Nx,Nz); S=zeros(Nx,Nz);
T(1,:)=Temp; S(1,:)=Salt;

for i=2:Nx
    Tx=0.5*f*Vz(i-1,:)./(g*gsw_alpha(gsw_SR_from_SP(S(i-1,:)),T(i-1,:),pres));
    Sx=-0.5*f*Vz(i-1,:)./(g*gsw_beta(gsw_SR_from_SP(S(i-1,:)),T(i-1,:),pres));
    T(i,:)=T(i-1,:)+Tx*dX; S(i,:)=S(i-1,:)+Sx*dX;
end

Temp_north=T; Salt_north=S; clear T S;
rho_north=gsw_rho(gsw_SR_from_SP(Salt_north),Temp_north,repmat(pres,[Nx,1]));

figure; clf; hold on;
contourf(X,RC,V_north',11,'edgecolor','None');colormap(mycmap); colorbar; caxis([-V0,V0]);
plot(X,squeeze(bath(:,end)),'ko-','linewidth',1.2,'markersize',6);
contour(X,RC,Temp_north',20,'linewidth',1.2,'color','black');
xlabel('Longitude'); ylabel('Depth'); title('Temp north bry')

figure; clf; hold on;
contourf(X,RC,V_north',11,'edgecolor','None');colormap(mycmap); colorbar; caxis([-V0,V0]);
plot(X,squeeze(bath(:,end)),'ko-','linewidth',1.2,'markersize',6);
contour(X,RC,Salt_north',20,'linewidth',1.2,'color','black');
xlabel('Longitude'); ylabel('Depth'); title('Salt north bry')

figure; clf; hold on;
contourf(X,RC,V_north',11,'edgecolor','None');colormap(mycmap); colorbar; caxis([-V0,V0]);
plot(X,squeeze(bath(:,end)),'ko-','linewidth',1.2,'markersize',6);
contour(X,RC,rho_north',20,'linewidth',1.2,'color','black');
xlabel('Longitude'); ylabel('Depth'); title('rho north bry')


% south boundary
V=V_south; f=fCori(1,1); dX=dxC(1,1);
Vz=zeros(Nx,Nz+1);
for k=2:(Nz-1)
    Vz(:,k)=(V(:,k)-V(:,k-1))/drC(k);
end
Vz(:,1)=Vz(:,2); Vz(:,end)=Vz(:,end-1);
Vz=0.5*(Vz(:,1:(end-1))+Vz(:,2:end)); Vz=0.5*(Vz(1:(end-1),:)+Vz(2:end,:));

T=zeros(Nx,Nz); S=zeros(Nx,Nz);
T(1,:)=Temp; S(1,:)=Salt;

for i=2:Nx
    Tx=0.5*f*Vz(i-1,:)./(g*gsw_alpha(gsw_SR_from_SP(S(i-1,:)),T(i-1,:),pres));
    Sx=-0.5*f*Vz(i-1,:)./(g*gsw_beta(gsw_SR_from_SP(S(i-1,:)),T(i-1,:),pres));
    T(i,:)=T(i-1,:)+Tx*dX; S(i,:)=S(i-1,:)+Sx*dX;
end

Temp_south=T; Salt_south=S; clear T S;
rho_south=gsw_rho(gsw_SR_from_SP(Salt_south),Temp_south,repmat(pres,[Nx,1]));

figure; clf; hold on;
contourf(X,RC,V_south',11,'edgecolor','None');colormap(mycmap); colorbar; caxis([-V0,V0]);
plot(X,squeeze(bath(:,1)),'ko-','linewidth',1.2,'markersize',6);
contour(X,RC,Temp_south',20,'linewidth',1.2,'color','black');
xlabel('Longitude'); ylabel('Depth'); title('Temp south bry')

figure; clf; hold on;
contourf(X,RC,V_south',11,'edgecolor','None');colormap(mycmap); colorbar; caxis([-V0,V0]);
plot(X,squeeze(bath(:,1)),'ko-','linewidth',1.2,'markersize',6);
contour(X,RC,Salt_south',20,'linewidth',1.2,'color','black');
xlabel('Longitude'); ylabel('Depth'); title('Salt south bry')

figure; clf; hold on;
contourf(X,RC,V_south',11,'edgecolor','None');colormap(mycmap); colorbar; caxis([-V0,V0]);
plot(X,squeeze(bath(:,1)),'ko-','linewidth',1.2,'markersize',6);
contour(X,RC,rho_south',20,'linewidth',1.2,'color','black');
xlabel('Longitude'); ylabel('Depth'); title('rho north bry')

Temp_west=repmat(Temp,[Ny,1]); Salt_west=repmat(Salt,[Ny,1]);

newfile=fopen([datadir,'correct/bathymetry.bin'],'w','b');
fwrite(newfile,bath,'real*8');
fclose(newfile);

newfile=fopen([datadir,'correct/Temp_north_boundary.bin'],'w','b');
fwrite(newfile,Temp_north,'real*8');
fclose(newfile);

newfile=fopen([datadir,'correct/Temp_south_boundary.bin'],'w','b');
fwrite(newfile,Temp_south,'real*8');
fclose(newfile);

newfile=fopen([datadir,'correct/Temp_west_boundary.bin'],'w','b');
fwrite(newfile,Temp_west,'real*8');
fclose(newfile);

newfile=fopen([datadir,'correct/Salt_north_boundary.bin'],'w','b');
fwrite(newfile,Salt_north,'real*8');
fclose(newfile);

newfile=fopen([datadir,'correct/Salt_south_boundary.bin'],'w','b');
fwrite(newfile,Salt_south,'real*8');
fclose(newfile);

newfile=fopen([datadir,'correct/Salt_west_boundary.bin'],'w','b');
fwrite(newfile,Salt_west,'real*8');
fclose(newfile);

newfile=fopen([datadir,'correct/V_north_boundary.bin'],'w','b');
fwrite(newfile,V_north,'real*8');
fclose(newfile);

newfile=fopen([datadir,'correct/V_south_boundary.bin'],'w','b');
fwrite(newfile,V_south,'real*8');
fclose(newfile);

fields={'sst','sss','taux','tauy'};
for n=1:length(fields)
    fieldname=char(fields(n));
    oldfile=fopen([datadir,fieldname,'_frc.bin'],'r','b');
    data=fread(oldfile,[Nx,Ny*12],'real*8');
    fclose(oldfile); clear oldfile;
    
    data=reshape(data,[Nx,Ny,12]);
    data=squeeze(mean(data,3));
    
    figure;
    clf;
    contourf(X,Y,data',16,'edgecolor','None');
    colormap(mycmap2); colorbar; 
    xlabel('Longitude'); ylabel('Latitude'); title(fieldname);
    
    newfile=fopen([datadir,'correct/',fieldname,'_frc.bin'],'w','b');
    fwrite(newfile,data,'real*8');
    fclose(newfile); clear newfile;  
end

T=repmat(reshape(Temp,[1,1,Nz]),[Nx,Ny,1]);
S=repmat(reshape(Salt,[1,1,Nz]),[Nx,Ny,1]);

newfile=fopen([datadir,'correct/Temp_profile_init.bin'],'w','b');
fwrite(newfile,reshape(T,[Nx,Ny*Nz]),'real*8');
fclose(newfile); clear newfile;

newfile=fopen([datadir,'correct/Salt_profile_init.bin'],'w','b');
fwrite(newfile,reshape(S,[Nx,Ny*Nz]),'real*8');
fclose(newfile); clear newfile;


