% Eli: I wrote this to run and plot Bueler's SIA model

Lx=5000;
J=1000;
b=1000*exp(-([1:J+1]'-J/2).^2/(J/3)^2);
H=zeros(J+1,1);
for j=1:J
  H(j)=H(j)+200*cos( pi*(j-J/2.0)/(J/3) );
end

H(H<10)=0; 
H(b<400)=0;
deltat=0.001; % it seems that this is in years...?
tf=deltat*1000;
M=b*0;

figure(1); clf
Z=[0:10:1300];
SMB_profile=SMB(Z*0,Z);
plot(SMB_profile,Z);
xlabel('SMB')
ylabel('height (m)')

A=1.e-14;

dx = 2 * Lx / J;
x = [-Lx:dx:Lx]; % (J+1)  grid in x dimension
x=x/1000;

figure(2); clf
plot(x,b+H,'b')
hold on
plot(x,b,'r')
pause(0.05)

for i=1:10
  H0=H;
  [H,h,dtlist] = SIA_siageneral1D(Lx,J,H0,deltat,tf,b,M,A);
  figure(2);
  plot(x,b+H,'g');
  pause(0.05);
end

figure(2);
plot(x,b+H,'b');
plot(x,b,'r')
