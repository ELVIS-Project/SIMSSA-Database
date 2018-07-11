from haystack.generic_views import SearchView
from haystack.generic_views import FacetedSearchView
from database.forms import FuzzySearchForm, FacetedWorkSearchForm


class GeneralSearch(SearchView):
    template_name = 'search/general-search.html'
    form_class = FuzzySearchForm


class FacetedSearch(FacetedSearchView):
    facet_fields = ['places', 'dates', 'sym_formats', 'audio_formats',
                    'text_formats', 'image_formats', 'certainty',
                    'languages', 'religiosity', 'instruments',
                    'composers', 'types', 'styles']
    context_object_name = 'object_list'
    template_name = 'search/faceted_search.html'
    form_class = FacetedWorkSearchForm
