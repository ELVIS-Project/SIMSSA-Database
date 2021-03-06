import os
import random
import uuid
from pprint import pprint
from typing import List

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File as PythonFile
from django.test import TestCase
from django.db.models import QuerySet
from model_bakery import baker
from psycopg2.extras import NumericRange

from database.models import *


def gen_int_range() -> NumericRange:
    lower: int = random.randint(1400, 2001)
    upper: int = random.randint(lower + 1, (lower + 20))
    num_range = NumericRange(lower, upper, bounds="[)")
    return num_range


baker.generators.add(
    "django.contrib.postgres.fields.ranges.IntegerRangeField", gen_int_range
)


def random_str(length: int = 10) -> str:
    return uuid.uuid4().hex.upper()[0:length]


def test_queryset_equal_to_list(
    queryset: QuerySet, list_of_objects: List[CustomBaseModel]
) -> None:
    testcase = TestCase()
    testcase.assertQuerysetEqual(
        qs=queryset,
        values=list_of_objects,
        ordered=False,
        # The transform argument having the identity function is so the members of
        # the second QuerySet don't go through the repr() method, then we can
        # compare objects to objects
        transform=lambda x: x,
    )


class ArchiveModelTest(TestCase):
    def setUp(self) -> None:
        sources = baker.make("Source", make_m2m=True, _quantity=5, _fill_optional=True)
        self.archive = baker.make("Archive", _fill_optional=True, sources=sources)

    def test_str(self) -> None:
        self.assertEqual(str(self.archive), self.archive.name)

    def test_get_absolute_url(self) -> None:
        self.assertEquals(
            self.archive.get_absolute_url(), f"/archives/{self.archive.id}"
        )


class ContributionMusicalWorkTest(TestCase):
    def setUp(self) -> None:
        person_birth_date = gen_int_range()
        person_death_date = NumericRange(
            person_birth_date.upper + 80, person_birth_date.upper + 85
        )
        contrib_date = NumericRange(
            person_birth_date.upper + 40, person_death_date.lower - 20
        )
        self.work = baker.make("MusicalWork", variant_titles=[random_str()])
        self.person = baker.make(
            "Person",
            _fill_optional=True,
            birth_date_range_year_only=person_birth_date,
            death_date_range_year_only=person_death_date,
        )
        self.contrib = baker.make(
            "ContributionMusicalWork",
            _fill_optional=True,
            person=self.person,
            date_range_year_only=contrib_date,
            contributed_to_work=self.work,
        )
        self.contrib_no_date = baker.make(
            "ContributionMusicalWork",
            date_range_year_only=None,
            contributed_to_work=self.work,
            person=self.person,
        )

    def test_str(self) -> None:
        person = str(self.contrib.person)
        role = self.contrib.role.lower()
        work = str(self.work)
        self.assertEquals(str(self.contrib), f"{person}, {role} of {work}")

    def test_date_property(self) -> None:
        lower: int = self.contrib.date_range_year_only.lower
        upper: int = self.contrib.date_range_year_only.upper
        self.assertEquals(self.contrib.date, f"({lower}-{upper-1})")
        self.assertEquals(self.contrib_no_date.date, "")

    def test_clean(self) -> None:
        person_birth_date = gen_int_range()
        person_death_date = NumericRange(
            person_birth_date.upper + 80, person_birth_date.upper + 85
        )
        contrib_date = NumericRange(
            person_birth_date.lower - 1, person_death_date.upper + 1
        )
        with self.assertRaisesMessage(
            ValidationError, "Date range is outside of contributor's life span"
        ):
            person = baker.make(
                "Person",
                _fill_optional=True,
                birth_date_range_year_only=person_birth_date,
                death_date_range_year_only=person_death_date,
            )
            baker.make(
                "ContributionMusicalWork",
                _fill_optional=True,
                person=person,
                date_range_year_only=contrib_date,
                contributed_to_work=self.work,
            )

    def test_get_absolute_url(self) -> None:
        self.assertEquals(
            self.contrib.get_absolute_url(), f"/contributions/{self.contrib.id}"
        )


class EncodingWorkflowModelTest(TestCase):
    def setUp(self) -> None:
        self.workflow = baker.make(
            "EncodingWorkflow",
            _create_files=True,
            _fill_optional=["encoder_names", "workflow_text", "workflow_file", "notes"],
        )
        self.workflow_w_sw = baker.make(
            "EncodingWorkflow",
            make_m2m=True,
            _fill_optional=["encoder_names", "encoding_software"],
        )

    def test_str(self) -> None:
        self.assertEquals(
            str(self.workflow), f"Encoded by: {self.workflow.encoder_names}"
        )
        # Test the __str__() method when the workflow has a software
        self.assertEquals(
            str(self.workflow_w_sw),
            f"Encoded by: {self.workflow_w_sw.encoder_names} with "
            f"{self.workflow_w_sw.encoding_software}",
        )

    def test_workflow_file_uploaded_correctly(self) -> None:
        self.assertTrue(os.path.exists(self.workflow.workflow_file.path))

    def test_get_absolute_url(self) -> None:
        self.assertEquals(
            self.workflow.get_absolute_url(), f"/encodingworkflows/{self.workflow.id}"
        )

    def tearDown(self) -> None:
        """Delete the file that was uploaded when creating the test object"""
        os.remove(self.workflow.workflow_file.path)


class ExperimentalStudyModelTest(TestCase):
    def setUp(self) -> None:
        self.study = baker.make("ExperimentalStudy", _fill_optional=True)

    def test_str(self) -> None:
        self.assertEqual(str(self.study), self.study.title)

    def test_get_absolute_url(self) -> None:
        self.assertEquals(
            self.study.get_absolute_url(), f"/experimentalstudies/{self.study.id}"
        )


class ExtractedFeatureModelTest(TestCase):
    def setUp(self) -> None:
        self.value = [random.uniform(0, 100)]
        self.dimensions = random.randint(2, 101)
        self.values_array = [random.uniform(0, 101) for x in range(self.dimensions)]
        self.software = baker.make("Software")
        self.file = baker.make("File", _create_files=True)
        self.feature_type = baker.make(
            "FeatureType", software=self.software, dimensions=1
        )
        self.feature_type_histogram = baker.make(
            "FeatureType", software=self.software, dimensions=self.dimensions
        )
        self.extracted_feature = baker.make(
            "ExtractedFeature",
            value=self.value,
            instance_of_feature=self.feature_type,
            extracted_with=self.software,
            feature_of=self.file,
        )
        self.extracted_feature_histogram = baker.make(
            "ExtractedFeature",
            value=self.values_array,
            instance_of_feature=self.feature_type_histogram,
            extracted_with=self.software,
            feature_of=self.file,
        )

    def test_str(self) -> None:
        self.assertEquals(
            str(self.extracted_feature),
            f"{self.extracted_feature.name}: {self.extracted_feature.value[0]}",
        )
        self.assertEquals(
            str(self.extracted_feature_histogram), self.extracted_feature_histogram.name
        )

    def test_name(self) -> None:
        self.assertEquals(self.extracted_feature.name, self.feature_type.name)
        self.assertEquals(
            self.extracted_feature_histogram.name, self.feature_type_histogram.name
        )

    def test_histogram_property(self) -> None:
        self.assertFalse(self.extracted_feature.is_histogram)
        self.assertTrue(self.extracted_feature_histogram.is_histogram)

    def test_description_property(self) -> None:
        self.assertEquals(
            self.extracted_feature.description, self.feature_type.description
        )
        self.assertEquals(
            self.extracted_feature_histogram.description,
            self.feature_type_histogram.description,
        )

    def test_code_property(self) -> None:
        self.assertEquals(self.extracted_feature.code, self.feature_type.code)
        self.assertEquals(
            self.extracted_feature_histogram.code, self.feature_type_histogram.code
        )

    def test_group_property(self) -> None:
        self.assertEquals(self.extracted_feature.group, self.feature_type.group)
        self.assertEquals(
            self.extracted_feature_histogram.group, self.feature_type_histogram.group
        )

    def test_clean(self) -> None:
        with self.assertRaisesMessage(
            ValidationError,
            "The length of the value array must be the same as "
            "the dimension of the FeatureType",
        ):
            baker.make(
                "ExtractedFeature",
                value=self.values_array,
                instance_of_feature=self.feature_type,
                extracted_with=self.software,
                feature_of=self.file,
            )

    def test_get_absolute_url(self) -> None:
        self.assertEquals(
            self.extracted_feature.get_absolute_url(),
            f"/extractedfeatures/{self.extracted_feature.id}",
        )

    def tearDown(self) -> None:
        """Delete the file that was uploaded when creating the test objects"""
        os.remove(self.file.file.path)


class FeatureFileModelTest(TestCase):
    def setUp(self) -> None:
        self.file = baker.make("File", _create_files=True)
        self.feature_file = baker.make(
            "FeatureFile",
            _fill_optional=True,
            make_m2m=True,
            _create_files=True,
            features_from_file=self.file,
        )

    def test_str(self) -> None:
        self.assertEqual(
            str(self.feature_file), os.path.basename(self.feature_file.file.path)
        )

    def test_file_uploaded_correctly(self) -> None:
        self.assertTrue(os.path.exists(self.feature_file.file.path))
        self.assertTrue(os.path.exists(self.feature_file.config_file.path))
        self.assertTrue(os.path.exists(self.feature_file.feature_definition_file.path))
        self.assertTrue(os.path.exists(self.file.file.path))

    def test_get_absolute_url(self) -> None:
        self.assertEquals(
            self.feature_file.get_absolute_url(),
            f"/featurefiles/{self.feature_file.id}",
        )

    def tearDown(self) -> None:
        """Delete the files that were uploaded when creating the test objects"""
        os.remove(self.file.file.path)
        os.remove(self.feature_file.file.path)
        os.remove(self.feature_file.config_file.path)
        os.remove(self.feature_file.feature_definition_file.path)


class FeatureTypeModelTest(TestCase):
    def setUp(self) -> None:
        # Feature codes based on the jSymbolic manual. The number for each is simply
        # the highest number available for that feature category (we don't need to make
        # all the codes to test, just one of each category), plus one feature not in
        # the manual (A-3) to test the case when we don't know the feature group in the
        # group property of the FeatureType model
        codes = ["P-41", "M-25", "C-35", "R-66", "RT-29", "I-20", "T-24", "D-4", "A-3"]
        self.software = baker.make("Software")
        self.file = baker.make("File", _create_files=True)
        self.feature_types = [
            baker.make(
                "FeatureType",
                code=code,
                _fill_optional=True,
                software=self.software,
                dimensions=1,
            )
            for code in codes
        ]

    def test_str(self) -> None:
        for feature_type in self.feature_types:
            self.assertEquals(str(feature_type), feature_type.name)

    def test_max_and_min(self) -> None:
        for feature_type in self.feature_types:
            num_extracted_features = random.randint(2, 10)
            values: List[float] = []
            for i in range(0, num_extracted_features):
                value = random.uniform(0, 101)
                values.append(value)
                extracted_feature = baker.make(
                    "ExtractedFeature",
                    value=[value],
                    instance_of_feature=feature_type,
                    extracted_with=self.software,
                    feature_of=self.file,
                )
                # Test max and min with every new value to make sure
                # the signal is being sent when we save a new
                # extracted feature and the max and min of the feature type
                # update correctly
                self.assertEquals(max(values), feature_type.max_val)
                self.assertEquals(min(values), feature_type.min_val)

    def test_group_property(self) -> None:
        for feature_type in self.feature_types:
            if feature_type.code == "P-41":
                self.assertEquals(feature_type.group, "Pitch Statistics Features")
            elif feature_type.code == "M-25":
                self.assertEquals(feature_type.group, "Melodic Interval Features")
            elif feature_type.code == "C-35":
                self.assertEquals(
                    feature_type.group, "Chords and Vertical Interval Features"
                )
            elif feature_type.code == "R-66":
                self.assertEquals(feature_type.group, "Rhythm Features")
            elif feature_type.code == "RT-29":
                self.assertEquals(feature_type.group, "Rhythm and Tempo Features")
            elif feature_type.code == "I-20":
                self.assertEquals(feature_type.group, "Instrumentation Features")
            elif feature_type.code == "T-24":
                self.assertEquals(feature_type.group, "Musical Texture Features")
            elif feature_type.code == "D-4":
                self.assertEquals(feature_type.group, "Dynamics Features")
            elif feature_type.code == "A-3":
                self.assertEquals(feature_type.group, "A")

    def test_get_absolute_url(self) -> None:
        for feature_type in self.feature_types:
            self.assertEquals(
                feature_type.get_absolute_url(), f"/featuretypes/{feature_type.id}"
            )

    def tear_down(self) -> None:
        """Delete the file that was uploaded when creating the test objects"""
        os.remove(self.file.file.path)


class FileModelTest(TestCase):
    def setUp(self) -> None:
        self.file = baker.make("File", _create_files=True)
        self.software = baker.make("Software")
        self.histogram_features: List[ExtractedFeature] = []
        self.scalar_features: List[ExtractedFeature] = []

        # Create 10 histogram features with a random dimension between 2 and 100
        # and random values and then add these features to the histogram_features list
        for i in range(0, 10):
            dimensions = random.randint(2, 101)
            values_array = [random.uniform(0, 101) for x in range(dimensions)]
            feature_type = baker.make(
                "FeatureType", software=self.software, dimensions=dimensions
            )
            extracted_feature = baker.make(
                "ExtractedFeature",
                instance_of_feature=feature_type,
                value=values_array,
                extracted_with=self.software,
                feature_of=self.file,
            )
            self.histogram_features.append(extracted_feature)

        # Same idea as above but for scalar features
        for i in range(0, 10):
            value = [random.uniform(0, 101)]
            feature_type = baker.make(
                "FeatureType", software=self.software, dimensions=1
            )
            extracted_feature = baker.make(
                "ExtractedFeature",
                instance_of_feature=feature_type,
                value=value,
                extracted_with=self.software,
                feature_of=self.file,
            )
            self.scalar_features.append(extracted_feature)

    def test_str(self) -> None:
        self.assertEquals(os.path.basename(self.file.file.name), str(self.file))

    def test_file_uploaded_correctly(self) -> None:
        self.assertTrue(os.path.exists(self.file.file.path))

    def test_histograms_property(self) -> None:
        test_queryset_equal_to_list(self.file.histograms, self.histogram_features)

    def test_scalar_features_property(self) -> None:
        test_queryset_equal_to_list(self.file.scalar_features, self.scalar_features)

    def test_get_absolute_url(self) -> None:
        self.assertEquals(self.file.get_absolute_url(), f"/files/{self.file.id}")

    def _test_rename_file_work_no_composer(self) -> None:
        work = baker.make("MusicalWork", variant_titles=["Test Work"])
        source = baker.make("Source", title="Test Source")
        source_instantiation = baker.make(
            "SourceInstantiation", source=source, work=work,
        )
        file = baker.make("File", _create_files=True, instantiates=source_instantiation)

    def _test_rename_file_work_composer(self) -> None:
        work = baker.make("MusicalWork", variant_titles=["Test Work"])
        source = baker.make("Source", title="Test Source")
        person = baker.make("Person", surname="McTester", given_name="Tester")
        contrib = baker.make(
            "ContributionMusicalWork",
            _fill_optional=True,
            person=person,
            contributed_to_work=work,
            role="COMPOSER",
        )
        source_instantiation = baker.make(
            "SourceInstantiation", source=source, work=work,
        )
        file_with_more_data = baker.make(
            "File", _create_files=True, instantiates=source_instantiation
        )

    def _test_rename_file_section_composer(self) -> None:
        work = baker.make("MusicalWork", variant_titles=["Test Work"])
        section = baker.make("Section", musical_work=work, title="Test Section")
        source = baker.make("Source", title="Test Source")
        person = baker.make("Person", surname="McTester", given_name="Tester")
        contrib = baker.make(
            "ContributionMusicalWork",
            _fill_optional=True,
            person=person,
            contributed_to_work=work,
            role="COMPOSER",
        )
        source_instantiation = baker.make(
            "SourceInstantiation", source=source, sections=[section],
        )
        file_with_more_data = baker.make(
            "File", _create_files=True, instantiates=source_instantiation
        )

    def _test_rename_file_section_no_composer(self) -> None:
        work = baker.make("MusicalWork", variant_titles=["Test Work"])
        section = baker.make("Section", musical_work=work, title="Test Section")
        source = baker.make("Source", title="Test Source")
        source_instantiation = baker.make(
            "SourceInstantiation", source=source, sections=[section],
        )
        file_with_more_data = baker.make(
            "File", _create_files=True, instantiates=source_instantiation
        )

    def _test_rename_file_part_from_section_no_composer(self) -> None:
        work = baker.make("MusicalWork", variant_titles=["Test Work"])
        section = baker.make("Section", musical_work=work, title="Test Section")
        part = baker.make("Part", name="Test Part II", section=section)
        source = baker.make("Source", title="Test Source")
        source_instantiation = baker.make(
            "SourceInstantiation", source=source, parts=[part],
        )
        file_with_more_data = baker.make(
            "File", _create_files=True, instantiates=source_instantiation
        )

    def _test_rename_file_part_from_section_composer(self) -> None:
        work = baker.make("MusicalWork", variant_titles=["Test Work"])
        section = baker.make("Section", musical_work=work, title="Test Section")
        part = baker.make("Part", name="Test Part", section=section)
        person = baker.make("Person", surname="McTester", given_name="Tester")
        contrib = baker.make(
            "ContributionMusicalWork",
            _fill_optional=True,
            person=person,
            contributed_to_work=work,
            role="COMPOSER",
        )
        source = baker.make("Source", title="Test Source")
        source_instantiation = baker.make(
            "SourceInstantiation", source=source, parts=[part],
        )
        file_with_more_data = baker.make(
            "File", _create_files=True, instantiates=source_instantiation
        )

    def _test_rename_file_part_from_work_no_composer(self) -> None:
        work = baker.make("MusicalWork", variant_titles=["Test Work"])
        part = baker.make("Part", name="Test Part", musical_work=work)
        source = baker.make("Source", title="Test Source")
        source_instantiation = baker.make(
            "SourceInstantiation", source=source, parts=[part],
        )
        file_with_more_data = baker.make(
            "File", _create_files=True, instantiates=source_instantiation
        )

    def _test_rename_file_part_from_work_composer(self) -> None:
        work = baker.make("MusicalWork", variant_titles=["Test Work"])
        part = baker.make("Part", name="Test Part", musical_work=work)
        person = baker.make("Person", surname="McTester", given_name="Tester")
        contrib = baker.make(
            "ContributionMusicalWork",
            _fill_optional=True,
            person=person,
            contributed_to_work=work,
            role="COMPOSER",
        )
        source = baker.make("Source", title="Test Source")
        source_instantiation = baker.make(
            "SourceInstantiation", source=source, parts=[part],
        )
        file_with_more_data = baker.make(
            "File", _create_files=True, instantiates=source_instantiation
        )

    def test_rename_file(self) -> None:
        self._test_rename_file_work_no_composer()
        self._test_rename_file_work_composer()
        self._test_rename_file_section_composer()
        self._test_rename_file_section_no_composer()
        self._test_rename_file_part_from_section_no_composer()
        self._test_rename_file_part_from_section_composer()
        self._test_rename_file_part_from_work_no_composer()
        self._test_rename_file_part_from_work_composer()

    def tearDown(self) -> None:
        os.remove(self.file.file.path)


class GenreAsInStyleModelTest(TestCase):
    def setUp(self) -> None:
        self.style = baker.make("GenreAsInStyle", _fill_optional=True)

    def test_str(self) -> None:
        self.assertEqual(str(self.style), self.style.name)

    def test_get_absolute_url(self) -> None:
        self.assertEquals(self.style.get_absolute_url(), f"/styles/{self.style.id}")


class GenreAsInTypeModelTest(TestCase):
    def setUp(self) -> None:
        self.type = baker.make("GenreAsInType", _fill_optional=True)

    def test_str(self) -> None:
        self.assertEqual(str(self.type), self.type.name)

    def test_get_absolute_url(self) -> None:
        self.assertEquals(self.type.get_absolute_url(), f"/types/{self.type.id}")


class GeographicAreaModelTest(TestCase):
    def setUp(self) -> None:
        self.area = baker.make("GeographicArea", _fill_optional=True)
        self.works_list = [
            baker.make("MusicalWork", variant_titles=[random_str()]).id
            for x in range(5)
        ]
        self.works = MusicalWork.objects.filter(id__in=self.works_list)
        for i in range(5):
            baker.make(
                "ContributionMusicalWork",
                contributed_to_work=self.works[i],
                _fill_optional=True,
                location=self.area,
            )

    def test_str(self) -> None:
        self.assertEqual(str(self.area), self.area.name)

    def test_get_absolute_url(self) -> None:
        self.assertEquals(self.area.get_absolute_url(), f"/areas/{self.area.id}")

    def test_musical_works_property(self) -> None:
        test_queryset_equal_to_list(self.area.musical_works.all(), self.works)


class InstrumentModelTest(TestCase):
    def setUp(self) -> None:
        self.instrument = baker.make("Instrument", _fill_optional=True)
        self.works = [
            baker.make("MusicalWork", variant_titles=[random_str()]) for x in range(5)
        ]
        self.sections = [
            baker.make("Section", musical_work=self.works[x]) for x in range(5)
        ]
        self.parts_section = [
            baker.make("Part", section=self.sections[x], written_for=self.instrument)
            for x in range(5)
        ]
        self.parts_musical_work = [
            baker.make("Part", musical_work=self.works[x], written_for=self.instrument)
            for x in range(5)
        ]

    def test_str(self) -> None:
        self.assertEqual(str(self.instrument), self.instrument.name)

    def test_get_absolute_url(self) -> None:
        self.assertEquals(
            self.instrument.get_absolute_url(), f"/instruments/{self.instrument.id}"
        )

    def test_parts(self) -> None:
        parts = self.parts_musical_work + self.parts_section
        self.assertQuerysetEqual(
            self.instrument.parts.all(), parts, ordered=False, transform=lambda x: x,
        )

    def test_musical_works_property(self) -> None:
        test_queryset_equal_to_list(self.instrument.musical_works, self.works)

    def test_sections_property(self) -> None:
        test_queryset_equal_to_list(self.instrument.sections, self.sections)


class LanguageModelTest(TestCase):
    def setUp(self) -> None:
        self.language = baker.make("Language", _fill_optional=True)

    def test_str(self) -> None:
        self.assertEqual(str(self.language), self.language.name)

    def test_get_absolute_url(self) -> None:
        self.assertEquals(
            self.language.get_absolute_url(), f"/languages/{self.language.id}"
        )


class MusicalWorkModelTest(TestCase):
    # TODO: fill this in
    pass


class PartModelTest(TestCase):
    # TODO: fill this in
    pass


class PersonModelTest(TestCase):
    # TODO: fill this in
    pass


class ResearchCorpusModelTest(TestCase):
    def setUp(self) -> None:
        self.corpus = baker.make("ResearchCorpus", _fill_optional=True)

    def test_str(self) -> None:
        self.assertEqual(str(self.corpus), self.corpus.title)

    def test_get_absolute_url(self) -> None:
        self.assertEquals(
            self.corpus.get_absolute_url(), f"/researchcorpora/{self.corpus.id}",
        )


class SectionModelTest(TestCase):
    # TODO: fill this in
    pass


class SoftwareModelTest(TestCase):
    def setUp(self) -> None:
        self.software = baker.make("Software", _fill_optional=True)

    def test_str(self) -> None:
        self.assertEqual(str(self.software), self.software.name)

    def test_get_absolute_url(self) -> None:
        self.assertEquals(
            self.software.get_absolute_url(), f"/softwares/{self.software.id}",
        )


class SourceInstantiationModelTest(TestCase):
    # TODO: fill this in
    pass


class SourceModelTest(TestCase):
    # TODO: fill this in
    pass


class TypeOfSectionModelTest(TestCase):
    def setUp(self) -> None:
        self.type_of_section = baker.make("TypeOfSection", _fill_optional=True)

    def test_str(self) -> None:
        self.assertEqual(str(self.type_of_section), self.type_of_section.name)

    def test_get_absolute_url(self) -> None:
        self.assertEquals(
            self.type_of_section.get_absolute_url(),
            f"/typesofsection/{self.type_of_section.id}",
        )


class ValidationWorkflowModelTest(TestCase):
    def setUp(self) -> None:
        self.workflow = baker.make(
            "ValidationWorkflow",
            _create_files=True,
            _fill_optional=[
                "validator_names",
                "workflow_text",
                "workflow_file",
                "notes",
            ],
        )
        self.workflow_w_sw = baker.make(
            "ValidationWorkflow",
            make_m2m=True,
            _fill_optional=["validator_names", "validator_software"],
        )

    def test_str(self) -> None:
        self.assertEquals(
            str(self.workflow), f"Validated by: {self.workflow.validator_names}"
        )
        # Test the __str__() method when the workflow has a software
        self.assertEquals(
            str(self.workflow_w_sw),
            f"Validated by: {self.workflow_w_sw.validator_names} with "
            f"{self.workflow_w_sw.validator_software}",
        )

    def test_workflow_file_uploaded_correctly(self) -> None:
        self.assertTrue(os.path.exists(self.workflow.workflow_file.path))

    def test_get_absolute_url(self) -> None:
        self.assertEquals(
            self.workflow.get_absolute_url(), f"/validationworkflows/{self.workflow.id}"
        )

    def tearDown(self) -> None:
        """Delete the file that was uploaded when creating the test object"""
        os.remove(self.workflow.workflow_file.path)
