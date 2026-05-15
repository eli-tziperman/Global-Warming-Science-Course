Lx=5000;
Ly=500;
J=100;
K=50;
H0=zeros(J+1,K+1)+500;
for j=1:J
  for k=1:K
    H0(j,k)=H0(j,k)+500*exp(-(j-J/2)^2/10^2-(k-K/2)^2/10^2);
  end
end
deltat=0.00001; % it seems that this is in years...?
tf=deltat*20;
b=zeros(J+1,K+1);
M=zeros(J+1,K+1);
A=1.e-15;

figure(1); clf
contourf(H0)
pause

[H,h,dtlist] = SIA_siageneral(Lx,Ly,J,K,H0,deltat,tf,b,M,A);

figure(2); clf
contourf(H)
