%% reconstruct topography from spheric harmonics
% U_coeff: spheric harmonics transformation coefficients
% x: cosine of co-latitude as in main_script
% lon: longitude in radiance
% N: resolution
function topo_recon=Spheric_Harmonics_Reconstruct_ver2(U_coeff,x,lon,N)
addpath /Users/xiaotingyang/Desktop/Spring2019/EPS261/MidTerm/
Nx=length(lon); Ny=length(x);
topo_recon=zeros(Ny,Nx);
I=sqrt(-1);
lon=reshape(lon,[1,Nx]);

for l=0:N  % for each degree
    %P_all=legendre(l,x);
    P_all=legendre(l,x,'norm')*sqrt(2); % all the associated Legendre Polynomials with degree l; times sqrt(2)to make it the same as in Jerry's notes
    ind_mid=l+1; % Where coefficient U_{l0} is put
    % deal with m=0 specially
    P=squeeze(P_all(1,:));
    P=reshape(P,[Ny,1]);
    %topo_recon=topo_recon+real(U_coeff(l+1,ind_mid)*P*exp(I*0*lon))*sqrt(2*l+1);
    topo_recon=topo_recon+real(U_coeff(l+1,ind_mid)*P*exp(I*0*lon)); % use matrix multiplication directly
    
    for m=1:l
        P=squeeze(P_all(m+1,:)); P=reshape(P,[Ny,1]);
        %topo_recon=topo_recon+2*real(U_coeff(l+1,ind_mid+m)*P*exp(I*m*lon)*(-1)^(m)*sqrt((2*l+1)*factorial(l-m)/factorial(l+m)));
        %topo_recon=topo_recon+2*real(U_coeff(l+1,ind_mid+m)*P*exp(I*m*lon));
        topo_recon=topo_recon+P*(U_coeff(l+1,ind_mid+m)*exp(I*m*lon)+U_coeff(l+1,ind_mid-m)*exp(-I*m*lon));
    end
    
end

topo_recon=real(topo_recon);

end