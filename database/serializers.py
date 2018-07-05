from rest_framework import serializers
from database.models import *
from rest_framework_recursive.fields import RecursiveField
from drf_haystack.serializers import HaystackSerializerMixin


class InstrumentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Instrument
        fields = ('url', 'name', 'id')


class GenreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Genre
        fields = ('url', 'name', 'id')


class PersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person
        fields = ('names', 'range_date_birth', 'range_date_death',
                  'birth_location', 'death_location',
                  'viaf_url', 'other_authority_control_url',
                  'works_contributed_to', 'sections_contributed_to',
                  'parts_contributed_to')


class PersonSearchSerializer(HaystackSerializerMixin, PersonSerializer):
    class Meta(PersonSerializer.Meta):
        search_fields = ('text', )


class GeographicAreaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GeographicArea
        fields = ('url', 'name', 'id', 'part_of')


class SectionSerializer(serializers.HyperlinkedModelSerializer):
    parents = RecursiveField(required=False, allow_null=True, many=True)
    children = RecursiveField(required=False, allow_null=True, many=True)

    class Meta:
        model = Section
        fields = ('url', 'title', 'id', 'parts', 'ordering',
                  'contributors', 'parents', 'children', 'in_works')


class MusicalWorkSerializer(serializers.HyperlinkedModelSerializer):
    composers = serializers.HyperlinkedRelatedField(
            many=True,
            read_only=True,
            view_name='person-detail'
    )

    class Meta:
        model = MusicalWork
        fields = ('url', 'variant_titles', 'genres_as_in_style',
                  'genres_as_in_form',
                  'sections', 'religiosity', 'viaf_url',
                  'other_authority_control_url', 'contributors',
                  'composers')


class PartSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Part
        fields = ('url', 'label', 'written_for', 'contributors')


class SourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        parent_sources = RecursiveField(required=False, allow_null=True, many=True)
        child_sources = RecursiveField(required=False, allow_null=True, many=True)
        model = Source
        fields = ('url', 'title', 'languages',
                  'work', 'section', 'part', 'part_of_collection')


class CollectionOfSourcesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CollectionOfSources
        fields = ('url', 'title', 'editorial_notes', 'publication_date',
                  'person_publisher', 'institution_publisher',
                  'physical_or_electronic')


class InstitutionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Institution
        fields = ('url', 'name', 'located_at', 'website')
