function F=SMB(b,H)
  % surface mass balance:
  F=min(1.0,0.01*(b+H-900));
  F=max(-4.0,F);
  F=F*0;
end

