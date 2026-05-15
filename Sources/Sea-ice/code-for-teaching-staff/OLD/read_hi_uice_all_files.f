c Progrem to read sea ice thickness and velocity, can be used to read other scaler or vector fields

! Eli: Data and FORTRAN code downloaded from :
! http://psc.apl.uw.edu/research/projects/arctic-sea-ice-volume-anomaly/data/model_grid

! To compile and run this FORTRAN code:
! gfortran-9 read_hi_uice.f; a.out

      parameter(nx1=360,ny1=120,nx=nx1,ny=ny1,imt=nx1,jmt=ny1)
      parameter(nyear1=1979,nyear2=2024) ! Eli: changed year numbers to first and last in data

      real*4 heff(imt,jmt)
      !dimension heff(imt,jmt)
      dimension uice(imt,jmt),vice(imt,jmt)

      dimension clon(imt,jmt),clat(imt,jmt),kmt(imt,jmt)
      dimension ulat(imt,jmt),ulon(imt,jmt),HTN(imt,jmt),HTE(imt,jmt)
     &,HUS(imt,jmt),HUW(imt,jmt),angle(imt,jmt),dxt(imt,jmt)
     &,dyt(imt,jmt)

      character *80 fopen(5), f1,f2,f3
      character *80 data_folder ! Eli
      character *4 cyear(1900:2100),cyear1(1900:2100)
      character *12 char
      integer SLEN

      f2='heff.H'
!Eli: commented out:
!     f3='icevel.H'


c     read lon and lat for scalar fields (like sea ice thickness and concentration)
      data_folder="../../../Data-for-teaching-staff/Sea-ice"//
     &     "/thickness/gridded-assimilation/"
      idf=slen(data_folder)
      open(20,file=data_folder(1:idf)//'grid.dat')
      read(20,'(10f8.2)') ((clon(i,j),i=1,nx1),j=1,ny1)
      read(20,'(10f8.2)') ((clat(i,j),i=1,nx1),j=1,ny1)
      close(20)

!     Eli: added this block of lines:
      open(92,file="Output/thickness_dat/sic_thickness_clon.dat"
     &     ,form="formatted",status="replace")
      do j=1,ny1
        write(92,*) (clon(i,j),i=1,nx1)
      end do
      close(92)
      open(92,file="Output/thickness_dat/sic_thickness_clat.dat"
     &     ,form="formatted",status="replace")
      do j=1,ny1
        write(92,*) (clat(i,j),i=1,nx1)
      end do
      close(92)

c read lon and lat for vector fields (like sea ice and ocean veclocities)
      open(24,file=data_folder(1:idf)//'grid.dat.pop')
      read(24,'(10f8.2)') ((ulat(i,j),i=1,nx),j=1,ny)
      read(24,'(10f8.2)') ((ulon(i,j),i=1,nx),j=1,ny)
c HTN, HTE, HUS, HUW are lengths of the 4 sides of a grid cell in km
c HTN, HTE are lengths of the northern and eastern sides of a scaler grid cell in km, HTN*HTE is the area of a scaler grid cell in km**2 and can be used to calculate sea ice volume and volumes of other variables
c HUS, HUW are lengths of the southern and western sides of a vector grid cell in km
      read(24,'(10f8.2)') ((HTN  (i,j),i=1,nx),j=1,ny)
      read(24,'(10f8.2)') ((HTE  (i,j),i=1,nx),j=1,ny)
      read(24,'(10f8.2)') ((HUS  (i,j),i=1,nx),j=1,ny)
      read(24,'(10f8.2)') ((HUW  (i,j),i=1,nx),j=1,ny)
c angle is the angle between latitude line and  grid cell x-coordinate line, needed for plotting vectors in spherical coordinate system
      read(24,'(10f8.2)') ((angle(i,j),i=1,nx),j=1,ny)
      close(24)

!     Eli: added this block of lines:
      open(92,file="Output/thickness_dat/sic_thickness_HTN.dat"
     &     ,form="formatted",status="replace")
      do j=1,ny1
        write(92,*) (HTN(i,j),i=1,nx1)
      end do
      close(92)
      open(92,file="Output/thickness_dat/sic_thickness_HTE.dat"
     &     ,form="formatted",status="replace")
      do j=1,ny1
        write(92,*) (HTE(i,j),i=1,nx1)
      end do
      close(92)

      
c     read model grid mask; ocean levels > 0, land <= 0
      open(20,file=data_folder(1:idf)//'io.dat_360_120.output')
      read(20,'(360i2)') kmt
      close(20)

!     Eli: write out mask:
      open(92,file="Output/thickness_dat/sic_thickness_mask.dat"
     &     ,form="formatted",status="replace")
      do j=1,ny1
        do i=1,nx1
          if (kmt(i,j)>0) then
            kmt(i,j)=1
          else
            kmt(i,j)=0
          end if
        end do
      end do
      do j=1,ny1
        write(92,*) (kmt(i,j),i=1,nx1)
      end do
      close(92)

      do 999 iyear=nyear1,nyear2,1 ! Eli: modify here to read only first and last years, if needed
        i=slen(f2)
        write(unit=cyear(iyear),fmt='(i4)') iyear
        write(*,*) " reading from file ",f2(1:i),cyear(iyear)
        open(2,file=data_folder(1:idf)//f2(1:i)//cyear(iyear)
     &       ,access='direct',form='unformatted',recl=nx1*ny1*4
     &       ,status='unknown')
!       Eli: added open 92:
        open(92,file="Output/thickness_dat/heff"//cyear(iyear)//".dat"
     &       ,form="formatted",status="replace")

!Eli: commented out:
!     i=slen(f3)
!      open(3,file=f3(1:i)//cyear(iyear)
!     &,access='direct',form='unformatted',recl=nx1*ny1*4
!     &,status='unknown')

!       Eli: added write into 92:
        do imon=1,12
          !write(*,*)" reading month:",imon
          read(2,rec=imon)((heff(i,j),i=1,nx1),j=1,ny1) ! Eli: added rec=imon option
          do j=1,ny1
            write(92,*) (heff(i,j),i=1,nx1)
          end do
!         Eli: added write out of thickness and commented reading of velocity
!         read(3)((uice(i,j),i=1,nx1),j=1,ny1)
!         read(3)((vice(i,j),i=1,nx1),j=1,ny1)
        end do

        close(2)
!       close(3) ! Eli: commented out
 999  continue

!     Eli:
      close(92)

      stop
      end


      INTEGER FUNCTION slen (string)
C ---
C --- this function computes the length of a character string less
C --- trailing blanks
C --- slen > 0, length of string less trailing blanks
C ---      = 0, character string is blank
C ---
      CHARACTER*(*) string
      CHARACTER*1 cblank
      INTEGER i
      DATA cblank/' '/
C ---
      DO 50 i = LEN(string), 1, -1
         IF (string(i:i) .NE. ' ')  GO TO 100
50    CONTINUE
      i = 0
100   CONTINUE
      slen = i
      RETURN
      END

