from django.db import models
from database.models.custom_base_model import CustomBaseModel
from database.models.extracted_feature import ExtractedFeature
from django.contrib.auth.models import User


class ResearchCorpus(CustomBaseModel):
    title = models.CharField(max_length=200, blank=False)
    contains = models.ManyToManyField(ExtractedFeature)
    creators = models.ManyToManyField(User)
    curators = models.ManyToManyField(User)
    

    class Meta(CustomBaseModel.Meta):
        db_table = 'research_corpus'
