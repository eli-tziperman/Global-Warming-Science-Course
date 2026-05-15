Eli, 201909

mocsy 2.0 is a collection of Fortran 95 routines to model ocean carbonate system thermodynamics:
http://ocmip5.ipsl.jussieu.fr/mocsy/
https://github.com/jamesorr/mocsy

I compiled mocsy following their instructions and using the gfortran that comes with homebrew gcc (brew install gcc), and is linked from my ~/bin/gfortran

To use it in a notebook, I added a blank file __init__.py to the mocsy/ directory; imported mocsy.mocsy instead of mocsy and used it as mocsy.mocsy.mvars instead of mocsy.mvars in the original examples.
