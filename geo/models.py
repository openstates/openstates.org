from django.contrib.gis.db import models
from boundaries.models import Boundary
from opencivicdata.core.models import Division


class DivisionGeometry(models.Model):
    division = models.ForeignKey(Division, related_name='geometries', on_delete=models.CASCADE)
    boundary = models.ForeignKey(Boundary, related_name='geometries', on_delete=models.CASCADE)

    def __str__(self):
        return '{0} - {1}'.format(self.division, self.boundary)
