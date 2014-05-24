from django.views.generic import View
from django.views.generic.detail import BaseDetailView, DetailView
from django.views.generic.list import BaseListView
from django.views.generic.edit import BaseFormView, FormView
from django.views.generic import TemplateView
from django.utils.encoding import force_unicode
from django.db.models.base import ModelBase
from django.http import HttpResponseNotAllowed, HttpResponse
from django.shortcuts import render, render_to_response
from django.db.models import Q
from django.core.mail import mail_admins

import json
from rest_framework import generics, filters

from festivals.models import Festival, Artist
from festivals.serializers import ArtistSerializer, GenreTagSerializer
from taggit.models import Tag
from festivals.forms import FestivalReportErrorForm

# JSON serialization helpers
def dumps(content, json_opts={}):
    """
    Replaces json.dumps with our own custom encoder to deal
    with model serializing.
    """
    json_opts['ensure_ascii'] = json_opts.get('ensure_ascii', False)
    json_opts['cls'] = json_opts.get('cls', LazyJSONEncoder)

    return json.dumps(content, **json_opts)


class LazyJSONEncoder(json.JSONEncoder):
    """
    A JSONEncoder subclass that handles querysets and model objects.
    If the model object has a "serialize" method that returns a dictionary,
    then this method is used, else, it attempts to serialize fields.
    """

    def default(self, obj):
        # This handles querysets and other iterable types
        try:
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)

        # This handles Models
        if isinstance(obj.__class__, ModelBase):
            if hasattr(obj, 'serialize') and \
               callable(getattr(obj, 'serialize')):
                return obj.serialize()
            return self.serialize_model(obj)

        # Other Python Types:
        try:
            return force_unicode(obj)
        except Exception:
            pass

        # Last resort:
        return super(LazyJSONEncoder, self).default(obj)

    def serialize_model(self, obj):
        """
        If you didn't write a serialize for your model.
        """
        tmp = {}

        many = [f.name for f in obj._meta.many_to_many]
        for field in obj._meta.get_all_field_names():
            if len(many) > 0 and field in many:
                many.remove(field)
                tmp[field] = getattr(obj, field).all()
            else:
                tmp[field] = getattr(obj, field, None)
        return tmp


# Custom response and views

class JSONResponse(HttpResponse):

    def __init__(self, content='', json_opts={},
                 mimetype="application/json", *args, **kwargs):

        if content:
            content = dumps(content, json_opts)
        else:
            content = dumps([], json_opts)

        super(JSONResponse, self).__init__(content, mimetype,
                                           *args, **kwargs)
        self['Cache-Control'] = 'max-age=0,no-cache,no-store'

    @property
    def json(self):
        return json.loads(self.content)

class JSONResponseMixin(object):
    def render_to_response(self, context, *args, **kwargs):
        return JSONResponse(context, *args, **kwargs)


class AjaxResponseMixin(object):
    def get_context_data(self, **kwargs):
        context = super(AjaxResponseMixin, self).get_context_data(**kwargs)
        if self.request.is_ajax():
            context["ajax"] = True
        return context


# class JSONListView(JSONResponseMixin, BaseListView):
#     def get_context_data(self, **kwargs):
#         context = super(JSONListView, self).get_context_data(**kwargs)
#         return context


# Actual views for the app
# class FestivalMap(FormView):
class FestivalMap(TemplateView):
    """
    View for our on page app.
    """
    template_name="map.html"
    # form_class = FilterForm



class FestivalJSONList(JSONResponseMixin, BaseListView):
    model = Festival
    context_object_name = 'festivals'

    def get_queryset(self):
        all_festivals = super(FestivalJSONList, self).get_queryset()
        return all_festivals.filter(Q(latitude__isnull=False), 
                                    Q(longitude__isnull=False))


class FestivalDetail(AjaxResponseMixin, DetailView):
    model = Festival
    context_object_name = 'festival'

    def get_context_data(self, **kwargs):
        context = super(FestivalDetail, self).get_context_data(**kwargs)
        context['form'] = FestivalReportErrorForm()
        return context


class ArtistJSONList(JSONResponseMixin, BaseListView):
    model = Artist
    context_object_name = 'artists'
    """
    def get_queryset(self):
        all_festivals = super(ArtistJSONList, self).get_queryset()
        return all_festivals.filter(Q(latitude__isnull=False), 
                                    Q(longitude__isnull=False))
    """

class ArtistListView(generics.ListAPIView):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class GenreTagListView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = GenreTagSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class FestivalReportErrorView(FormView):
    form_class = FestivalReportErrorForm
    template_name = "festivals/report_error_form.html" # useless

    def form_valid(self, form):
        """
        If the form is valid, send emails and return user a thanks
        """
        info_type = form.cleaned_data['info_type']
        message = form.cleaned_data['message']
        festival_slug = self.kwargs["slug"]
        festival = Festival.objects.get(slug__exact=festival_slug)
        email_subject = "Someone spoted an error"
        email_msg = '''
Hi Metalmap Admin,

The following info type might not correct for festival %s [id: %s]:

%s

The user also said:

%s

--
Best,

metalmap bot 
''' % (festival.title, festival.id, info_type, message)
        
        print email_msg
        mail_admins(email_subject, email_msg)
        # return HttpResponseRedirect(self.get_success_url())
        return render_to_response('festivals/report_error_sent.html')