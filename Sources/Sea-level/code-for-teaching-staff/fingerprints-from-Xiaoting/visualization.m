%% EPS261 final assignment: visualization
addpath /Users/xiaotingyang/Desktop/Spring2019/EPS261/Final/Matlab/
addpath /Users/xiaotingyang/Documents/MATLAB/MetToolbox/

datadir='/Users/xiaotingyang/Desktop/Spring2019/EPS261/Final/Data/';
plotdir='/Users/xiaotingyang/Desktop/Spring2019/EPS261/Final/figures/';

mycmap=nclcmap('CBR_coldhot',51);
mycmap2=[0.8,0.8,0.8;
    0.3,0.4,1.0];

myfile=load([datadir,'topo.mat']);
topo=myfile.('topo_pres'); clear myfile;

myfile=load([datadir,'Antarctic_melting.mat']);
C=myfile.('C'); lon=myfile.('lon_GL'); lat=myfile.('x_GL'); colat=90-lat;
Delta_Sa=myfile.('Delta_S'); Ia=myfile.('Ia'); clear myfile;

myfile=load([datadir,'Greenland_melting.mat']);
Delta_Sg=myfile.('Delta_S'); Ig=myfile.('Ig');

Delta_Sa(C==0.0)=NaN; Delta_Sg(C==0.0)=NaN;
 % scale the sea level change so gloabl mean is 1
avg=nanmean(Delta_Sa(:)); Delta_Sa=Delta_Sa/avg; clear avg;
avg=nanmean(Delta_Sg(:)); Delta_Sg=Delta_Sg/avg; clear avg;

pos={'Nantucket','Norfolk','Miami','Tahiti','Seychelles','Christchurch','Wakatabi','Maldives','Huon Peninsula'};
lons=[289.9,283.8,279.78,210.58,55.492,172.72,123.755,73.03,147.66];
Is=[];
colats=[48.72,53.083,64.212,107.670,104.680,13.528,95.594,84.720,96.160];
lats=90-colats;
Js=[];
S=[1.47,1.64,1.95,2.41,2.26,2.15,2.27,2.25,2.28]'; % measured sea level change on each site
N=length(S);
S_sep=zeros(N,2); % seperate contribution from two glaciers


for i=1:length(lons)
    [~,temp]=min(abs(lon-lons(i)));
    Is(end+1)=temp; clear temp;
end

for j=1:length(lats)
    [~,temp]=min(abs(lat-lats(j)));
    Js(end+1)=temp; clear temp;
end

for n=1:N
    S_sep(n,1)=Delta_Sg(Js(n),Is(n));
    S_sep(n,2)=Delta_Sa(Js(n),Is(n));
end

% solve for contirbution from each
x=(S_sep'*S_sep)\(S_sep'*S);

% make figures;
set(0,'defaulttextfontsize',28);
set(0,'defaultaxesfontsize',28);

% plot Ocean mask
fig=figure; fig.Renderer='Painters';
clf; hold on;
imagesc(lon,lat,C); set(gca,'Ydir','normal');
colormap(mycmap2); colorbar; caxis([0,1]);
for n=1:length(Is)
    plot(lons(n),lats(n),'ro','markersize',8,'MarkerFaceColor','r');
    if n<length(Is)
        text(lons(n)+1.0,lats(n)+5.0,char(pos(n)),'color','black','FontSize',20,'FontWeight','bold');
    else
        text(lons(n)+1.0,lats(n),char(pos(n)),'color','black','FontSize',20,'FontWeight','bold');
    end
end
xlabel('Longitude'); ylabel('Latitude'); title('Ocean function');
xlim([min(lon),max(lon)]); ylim([min(lat),max(lat)]);
set(gcf,'PaperUnit','inches'); set(gcf,'PaperSize',[10,8]);
set(gcf,'PaperPosition',[0,0,10,8]);
saveas(gcf,[plotdir,'Ocean_mask.pdf']);

% plot Greenland ice cover
fig=figure; fig.Renderer='Painters';
clf; hold on;
imagesc(lon,lat,Ig); set(gca,'Ydir','normal');
colormap(mycmap2(end:(-1):1,:)); colorbar; caxis([-1,0]);
xlabel('Longitude'); ylabel('Latitude'); title('Greenland ice change');
contour(lon,lat,topo,[0.0,0.0],'linewidth',1.2,'color','black');
xlim([min(lon),max(lon)]); ylim([min(lat),max(lat)]);
set(gcf,'PaperUnit','inches'); set(gcf,'PaperSize',[10,8]);
set(gcf,'PaperPosition',[0,0,10,8]);
saveas(gcf,[plotdir,'Greenland_ice_change.pdf']);

% plot Antarctica ice cover
fig=figure; fig.Renderer='Painters';
clf; hold on;
imagesc(lon,lat,Ia); set(gca,'Ydir','normal');
colormap(mycmap2(end:(-1):1,:)); colorbar; caxis([-1,0]);
xlabel('Longitude'); ylabel('Latitude'); title('Antarctica ice change');
contour(lon,lat,topo,[0.0,0.0],'linewidth',1.2,'color','black');
xlim([min(lon),max(lon)]); ylim([min(lat),max(lat)]);
set(gcf,'PaperUnit','inches'); set(gcf,'PaperSize',[10,8]);
set(gcf,'PaperPosition',[0,0,10,8]);
saveas(gcf,[plotdir,'Antarctica_ice_change.pdf']);

% plot Greenland fingerprint
fig=figure; fig.Renderer='Painters';
clf; hold on;
fill([min(lon),max(lon),max(lon),min(lon)],[min(lat),min(lat),max(lat),max(lat)],[0.8,0.8,0.8]);
h=imagesc(lon,lat,Delta_Sg); set(gca,'Ydir','normal');
set(h,'AlphaData',~isnan(Delta_Sg));
colormap(mycmap); caxis([-2.0,2.0]); colorbar;
contour(lon,lat,topo,[0.0,0.0],'linewidth',1.2,'color','black');
xlim([min(lon),max(lon)]); ylim([min(lat),max(lat)])
xlabel('Longitude'); ylabel('Latitude'); title('Greenland fingerprint');
set(gcf,'PaperUnit','inches'); set(gcf,'PaperSize',[10,8]);
set(gcf,'PaperPosition',[0,0,10,8]);
saveas(gcf,[plotdir,'Greenland_fingerprint.pdf']);

% plot Antarctica fingerprint
fig=figure; fig.Renderer='Painters';
clf; hold on;
fill([min(lon),max(lon),max(lon),min(lon)],[min(lat),min(lat),max(lat),max(lat)],[0.8,0.8,0.8]);
h=imagesc(lon,lat,Delta_Sa); set(gca,'Ydir','normal');
set(h,'AlphaData',~isnan(Delta_Sa));
colormap(mycmap); caxis([-2.0,2.0]); colorbar;
contour(lon,lat,topo,[0.0,0.0],'linewidth',1.2,'color','black');
xlim([min(lon),max(lon)]); ylim([min(lat),max(lat)])
xlabel('Longitude'); ylabel('Latitude'); title('Antarctica fingerprint');
set(gcf,'PaperUnit','inches'); set(gcf,'PaperSize',[10,8]);
set(gcf,'PaperPosition',[0,0,10,8]);
saveas(gcf,[plotdir,'Antarctica_fingerprint.pdf']);

% plot linear fitting
fig=figure; fig.Renderer='Painters'; clf; hold on;
plot(1:N,S,'bo-','linewidth',1.2,'markersize',6,'MarkerFaceColor','b');
plot(1:N,x(1)*S_sep(:,1)+x(2)*S_sep(:,2),'ko-','linewidth',1.2,'markersize',6,'MarkerFaceColor','k');
plot(1:N,x(1)*S_sep(:,1),'rx-','linewidth',1.2,'markersize',6);
plot(1:N,x(2)*S_sep(:,2),'m+-','linewidth',1.2,'markersize',6);
legend('measured','linear combination','Greenland','Antarctic','Location','southeast');
text(6.4,1.8,[num2str(round(x(1),2)),'Greenland+',num2str(x(2),2),'Antarctic'],'color','black','fontsize',20,'fontweight','bold');
set(gca,'xtick',[1:N],'xticklabel',pos);
ax=gca; ax.FontSize=15;
xlabel('Location'); ylabel('Sea level change');
set(gcf,'PaperUnit','inches'); set(gcf,'PaperSize',[12,6]);
set(gcf,'PaperPosition',[0,0,12,6]);
saveas(gcf,[plotdir,'linear_combination.pdf']);




