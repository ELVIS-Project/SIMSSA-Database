from django.db import models
from database.models.custom_base_model import CustomBaseModel
from django.contrib.postgres.fields import ArrayField
from database.models.software import Software
from database.models.symbolic_music_file import SymbolicMusicFile


class ExtractedFeature(CustomBaseModel):
    """Content-based data extracted from a file"""
    name = models.CharField(max_length=200, blank=False,
                            help_text='The name of the Extracted Feature')
    value = ArrayField(models.FloatField(),
                       help_text='The value of the Feature. Encoded as an '
                                 'array but if the Feature is scalar it '
                                 'is an array of length = 1')
    extracted_with = models.ForeignKey(Software, on_delete=models.PROTECT,
                                       null=False, blank=False,
                                       help_text='The Software used to extract'
                                                 'this Feature')

    feature_of = models.ForeignKey(SymbolicMusicFile, on_delete=models.CASCADE,
                                   null=False, blank=False,
                                   help_text='The Symbolic File from which '
                                             'the feature was extracted')

    def __str__(self):
        return "{0}".format(self.name)

    class Meta(CustomBaseModel.Meta):
        db_table = 'extracted_feature'
