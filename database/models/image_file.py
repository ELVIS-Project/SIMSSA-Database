from django.contrib.postgres.fields import ArrayField
from django.db import models

from database.models.file import File
from database.models.source_instantiation import SourceInstantiation


class ImageFile(File):
    """
    A manifestation of a SourceInstantiation as digital images

    Generated from a source by an Encoder and can be validate by a Validator
    """
    manifests = models.ForeignKey(SourceInstantiation,
                                  related_name='manifested_by_image_files',
                                  on_delete=models.CASCADE, null=False,
                                  help_text='The SourceInstantiation manifested by these '
                                            'images')

    files = ArrayField(models.ImageField(upload_to='images/'),
                       null=False, blank=False,
                       help_text='The actual set of image files')

    @property
    def pages(self):
        """Gets the number of images, which is equal to the number of pages"""
        return self.files.__len__()

    def __str__(self):
        return "Images of {0}".format(self.manifests)

    class Meta:
        db_table = 'image_file'
