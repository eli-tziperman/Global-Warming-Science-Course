import sys
from PIL import Image

dir='../../../Data-for-teaching-staff/Introduction/NASA-sea-ice-images/'
images = [Image.open(x) for x in [dir+'ice_area_by_year_2019.1979.tif', dir+'ice_area_by_year_2019.2012.tif']]
widths, heights = zip(*(i.size for i in images))

total_width = sum(widths)
max_height = max(heights)

new_im = Image.new('RGB', (total_width, max_height))

x_offset = 0
for im in images:
  new_im.paste(im, (x_offset,0))
  x_offset += im.size[0]

new_im.save('/Users/eli/Courses/EPS101/Data-for-teaching-staff/Introduction/NASA-sea-ice-images/sea-ice-background.tif')
