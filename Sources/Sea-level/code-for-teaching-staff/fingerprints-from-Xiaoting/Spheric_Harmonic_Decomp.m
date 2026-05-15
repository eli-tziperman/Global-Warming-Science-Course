%% decompose topography into spherical harmocnis
% U_coeff is the matrix containing all the coefficients; 
% data is the original 2D map;
% x is the cosine of co-latitude as output in main_script, 
% w: the Legendre-Gaussian weights
% lon is longitude in rad
%  N is the maximum degree
function U_coeff=Spheric_Harmonic_Decomp(data,x,w,lon,N)
% *Eli: addpath /Users/xiaotingyang/Desktop/Spring2019/EPS261/MidTerm/
U_coeff=NaN(N+1,2*N+1); % each row is the coefficients of each degree, and only tne first 2k+1 elements will be filled on (k+1)-th row, others being NaNs
I=sqrt(-1); 
dlon=lon(2)-lon(1); % zonal resolution, it is a constant, no changing with position
Nx=length(x); % how many grid point meridionally
w=reshape(w,[1,Nx]); lon=reshape(lon,[1,length(lon)]);

for l=0:N  % deal with each degree
    ind_mid=l+1; % where to put coefficient U_{l0}
    %P_all=legendre(l,x); % all the associated Legendre Polynomials with degree l
    P_all=legendre(l,x,'norm')*sqrt(2); % all the associated Legendre Polynomials with degree l; times sqrt(2)to make it the same as in Jerry's notes
    % deal with m=0 specially
    P=squeeze(P_all(1,:));
    temp=zeros(1,Nx);
    for j=1:Nx
        temp(j)=sum(squeeze(data(j,:))*dlon);  % zonal integral
    end
    U_coeff(l+1,ind_mid)=sum(temp.*P.*w)/(4*pi); % meridional integral
    
    % for higher order terms
    for m=1:l
        P=squeeze(P_all(m+1,:)); % legendre function corresponding to this order
        % first deal with positive m
        temp=zeros(1,Nx); % zonal integral
        for j=1:Nx
            temp(j)=sum(data(j,:).*dlon.*exp(-I*m*lon)); 
        end
        U_coeff(l+1,ind_mid+m)=sum(temp.*P.*w)/(4*pi); % meridional integral
        
        % and the corresponding nagative m, calculated indirectly
        U_coeff(l+1,ind_mid-m)=(-1)^(m)*conj(U_coeff(l+1,ind_mid+m));
        
        
    end
    
end


end