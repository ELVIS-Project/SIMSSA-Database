from django.db import models
from database.models.file import File
from database.models.musical_instance import MusicalInstance
from database.models.page import Page
import os


class ImageFile(File):
    """A manifestation of a Musical Instance as a digital image

    An image file must be an image of one or more Pages from a Source
    """
    color_mode = models.CharField(max_length=20)
    compression_type = models.CharField(max_length=20)
    gama_correction = models.CharField(max_length=20)
    color_calibration = models.CharField(max_length=20)
    pixel_width = models.PositiveIntegerField()
    pixel_height = models.PositiveIntegerField()
    ppi = models.PositiveIntegerField()
    page_of = models.ManyToManyField(Page, related_name='has_images')

    manifests = models.ForeignKey(MusicalInstance,
                                  related_name='manifested_by_image_file',
                                  on_delete=models.CASCADE, null=False)

    # Should we change this to image field?

    file = models.FileField(upload_to='images/')


    def __str__(self):
        filename = os.path.basename(self.file.name)
        return "{0}".format(filename)

    class Meta:
        db_table = 'image_file'
