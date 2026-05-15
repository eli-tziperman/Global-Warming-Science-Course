function [H,dtav] = SIA_diffusion1D(Lx,J,Dright,Dleft,H0,tf,F,b)
% DIFFUSION  Adaptive explicit method for diffusion equation
%   H_t = F + div (D grad (H + b))
% on rectangle (-Lx,Lx) x (-Ly,Ly) with initial condition H0 and
% functions F(x,y), D(x,y), b(x,y).  The boundary condition is that
% the T values at the edge of the domain (i.e. H(1,.), H(J+1,.), H(.,1),
% H(.,K+1)) are all held fixed at their initial values supplied in H0.
% That is, the boundary condition is a Dirichlet condition from the
% initial values.
% Usage:
%   H = diffusion(Lx,J,Dright,Dleft,H0,tf,F)
% where
%   H     = approximate solution at tf
%   Lx,Ly = half-widths of rectangular domain
%   J,K   = number of subintervals in x,y directions, resp.
%   D*    = (J-1) arrays with diffusivities for "staggered" grid
%   H0    = (J+1) array with initial values on regular grid
%   tf    = final time
%   F     <-- OPTIONAL ARGUMENT
%         = (J+1) x (K+1) array with heat source on regular grid
%   b     <-- OPTIONAL ARGUMENT
%         = (J+1) x (K+1) array with offset before gradient
% Note: There is no error checking on sizes of D*, H0, F, b arrays.
% Note: There is no text output.  Restore commented 'fprintf' if desired.
% Note: The input diffusivities could be time-dependent, but they are
%   time-independent in this simplified implementation.  Call-back could
%   implement time-dependent diffusivity D(t,x,y).
% Example: Compare this result to HEATADAPT:
%   >> J = 50;  K = 50;  D = ones(J-1,K-1);
%   >> [x,y] = ndgrid(-1:2/J:1,-1:2/K:1);
%   >> H0 = exp(-30*(x.*x + y.*y));
%   >> H = diffusion(1.0,1.0,J,K,D,D,D,D,H0,0.05);
%   >> surf(x,y,H), shading('interp'), xlabel x, ylabel y
% Called by: SIAFLAT, SIAGENERAL.

% spatial grid and initial condition
dx = 2 * Lx / J;
[x] = ndgrid(-Lx:dx:Lx); % (J+1)  grid in x plane
H = H0;
%if nargin < 11, F = zeros(size(H0)); end  % for heat source term
%if nargin < 12, b = zeros(size(H0)); end  % allows use for nonflat-bed SIA case

%fprintf('  doing explicit steps adaptively on 0.0 < t < %.3f\n',tf)
t = 0.0;    count = 0;
while t < tf
   % stability condition gives time-step restriction
   maxD = [max(Dleft) max(Dright)];
   maxD = max(maxD);  % scalar maximum of D
   if maxD <= 0.0  % e.g. happens with zero thickness ice sheets
     dt = tf - t;
   else
     dt0 = 0.25 * (dx)^2 / maxD;
     dt = min(dt0, tf - t);  % do not go past tf
   end
   mu_x = dt / (dx*dx);
   Hb = H + b;
   H(2:J) = H(2:J) + ...
       mu_x * Dright .* ( Hb(3:J+1) - Hb(2:J)   ) - ...
       mu_x * Dleft  .* ( Hb(2:J)   - Hb(1:J-1) );
   F1=SMB(b,H);
   H = H + F1 * dt;
   t = t + dt;    count = count + 1;
   %fprintf('.')
end
dtav = tf / count;
%fprintf('\n  completed N = %d steps, average dt = %.7f\n',count,tf/count)
%surf(x,y,H),  shading('interp'),  xlabel x,  ylabel y
