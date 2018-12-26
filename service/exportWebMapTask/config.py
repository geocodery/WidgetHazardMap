import os

BASE_DIR = os.path.dirname(__file__)
CONN = os.path.join(os.path.dirname(BASE_DIR), "config\\bdgeocat_publ_gis.sde")

# select * from a where sde.st_intersects(shape, sde.st_geometry('POINT (x, y)', SRC)) = 1
