from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from mainapp.redis_queue import sms_queue
from mainapp.sms_handler import send_confirmation_sms
from .models import Request, Volunteer, DistrictManager, Contributor, DistrictNeed, Person, RescueCamp, NGO, \
    Announcements , districts, RequestUpdate, PrivateRescueCamp, CsvBulkUpload
import django_filters
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import logout
from django.contrib import admin
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Count, QuerySet
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.http import Http404

from mainapp.admin import create_csv_response
import csv
from dateutil import parser
import calendar
from mainapp.models import CollectionCenter


class CustomForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CustomForm, self).__init__(*args, **kwargs)
        # for field_name, field in self.fields.items():
        #     field.widget.attrs['class'] = 'form-control'

PER_PAGE = 100
PAGE_LEFT = 5
PAGE_RIGHT = 5
PAGE_INTERMEDIATE = "50"

class CreateRequest(CreateView):
    model = Request
    template_name='mainapp/request_form.html'
    fields = [
        'district',
        'location',
        'requestee',
        'requestee_phone',
        'is_request_for_others',
        'latlng',
        'latlng_accuracy',
        'needrescue',
        'detailrescue',
        'needwater',
        'detailwater',
        'needfood',
        'detailfood',
        'needcloth',
        'detailcloth',
        'needmed',
        'detailmed',
        'needkit_util',
        'detailkit_util',
        'needtoilet',
        'detailtoilet',
        'needothers'
    ]
    success_url = '/req_sucess/'

    def form_valid(self, form):
        self.object = form.save()
        sms_queue.enqueue(
            send_confirmation_sms, self.object.requestee_phone
        )
        return HttpResponseRedirect(self.get_success_url())

class RegisterVolunteer(CreateView):
    model = Volunteer
    fields = ['name', 'district', 'phone', 'organisation', 'area', 'address']
    success_url = '/reg_success/'

def volunteerdata(request):
    filter = VolunteerFilter( request.GET, queryset=Volunteer.objects.all() )
    req_data = filter.qs.order_by('-id')
    paginator = Paginator(req_data, PER_PAGE)
    page = request.GET.get('page')
    req_data = paginator.get_page(page)
    req_data.min_page = req_data.number - PAGE_LEFT
    req_data.max_page = req_data.number + PAGE_RIGHT
    req_data.lim_page = PAGE_INTERMEDIATE
    return render(request, 'mainapp/volunteerview.html', {'filter': filter , "data" : req_data })

class RegisterNGO(CreateView):
    model = NGO
    fields = ['organisation', 'organisation_type','organisation_address', 'name', 'phone', 'description', 'area',
              'location']
    success_url = '/reg_success'

class RegisterPrivateReliefCamp(CreateView):
    model = PrivateRescueCamp
    fields = '__all__'
    success_url = '/pcamp'

def privatecc(request):
    return render(request,"privatecc.html")


def pcamplist(request):
    filter = PrivateCampFilter(request.GET, queryset=PrivateRescueCamp.objects.all())
    data = filter.qs.order_by('-id')
    paginator = Paginator(data, 50)
    page = request.GET.get('page')
    data = paginator.get_page(page)

    return render(request, "mainapp/pcamplist.html", {'filter': filter , 'data' : data})

def pcampdetails(request):
    if('id' not in request.GET.keys() ):return HttpResponseRedirect('/pcamp')
    id = request.GET.get('id')
    try:
        req_data = PrivateRescueCamp.objects.get(id=id)
    except:
        return HttpResponseRedirect("/error?error_text={}".format('Sorry, we couldnt fetch details for that Camp'))
    return render(request, 'mainapp/p_camp_details.html', {'req': req_data })

def download_ngo_list(request):
    district = request.GET.get('district', None)
    filename = 'ngo_list.csv'
    if district is not None:
        filename = 'ngo_list_{0}.csv'.format(district)
        qs = NGO.objects.filter(district=district).order_by('district','name')
    else:
        qs = NGO.objects.all().order_by('district','name')
    header_row = ['Organisation',
                  'Type',
                  'Address',
                  'Name',
                  'Phone',
                  'Description',
                  'District',
                  'Area',
                  'Location',
                  ]
    body_rows = qs.values_list(
        'organisation',
        'organisation_type',
        'organisation_address',
        'name',
        'phone',
        'description',
        'district',
        'area',
        'location',
    )
    return create_csv_response(filename, header_row, body_rows)


class RegisterContributor(CreateView):
    model = Contributor
    fields = ['name', 'district', 'phone', 'address',  'commodities']
    success_url = '/contrib_success/'


class HomePageView(TemplateView):
    template_name = "home.html"


class NgoVolunteerView(TemplateView):
    template_name = "ngo_volunteer.html"


class MapView(TemplateView):
    template_name = "mapview.html"


class ReqSuccess(TemplateView):
    template_name = "mainapp/req_success.html"


class RegSuccess(TemplateView):
    template_name = "mainapp/reg_success.html"


class SubmissionSuccess(TemplateView):
    template_name = "mainapp/submission_success.html"


class ContribSuccess(TemplateView):
    template_name = "mainapp/contrib_success.html"


class DisclaimerPage(TemplateView):
    template_name = "mainapp/disclaimer.html"


class AboutIEEE(TemplateView):
    template_name = "mainapp/aboutieee.html"


class DistNeeds(TemplateView):
    template_name = "mainapp/district_needs.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['district_data'] = DistrictNeed.objects.all()
        return context


class RescueCampFilter(django_filters.FilterSet):
    class Meta:
        model = RescueCamp
        fields = ['district']

    def __init__(self, *args, **kwargs):
        super(RescueCampFilter, self).__init__(*args, **kwargs)
        # at startup user doen't push Submit button, and QueryDict (in data) is empty
        if self.data == {}:
            self.queryset = self.queryset.none()


def relief_camps(request):
    return render(request,"mainapp/relief_camps.html")


def relief_camps_list(request):
    filter = RescueCampFilter(request.GET, queryset=RescueCamp.objects.filter(status='active'))
    relief_camps = filter.qs.annotate(count=Count('person')).order_by('district','name').all()

    return render(request, 'mainapp/relief_camps_list.html', {'filter': filter , 'relief_camps' : relief_camps, 'district_chosen' : len(request.GET.get('district') or '')>0 })


class RequestFilter(django_filters.FilterSet):
    class Meta:
        model = Request
        # fields = ['district', 'status', 'needwater', 'needfood', 'needcloth', 'needmed', 'needkit_util', 'needtoilet', 'needothers',]

        fields = {
                    'district' : ['exact'],
                    'requestee' : ['icontains'],
                    'requestee_phone' : ['exact'],
                    'location' : ['icontains'],
                    'needrescue': ['exact'],
                    'needwater' : ['exact'],
                    'needfood' : ['exact'],
                    'needcloth' : ['exact'],
                    'needmed' : ['exact'],
                    'needkit_util' : ['exact'],
                    'needtoilet' : ['exact'],
                    'needothers' : ['exact']
                 }

    def __init__(self, *args, **kwargs):
        super(RequestFilter, self).__init__(*args, **kwargs)
        # at startup user doen't push Submit button, and QueryDict (in data) is empty
        if self.data == {}:
            self.queryset = self.queryset.none()

class VolunteerFilter(django_filters.FilterSet):
    class Meta:
        model = Volunteer
        fields = {
                    'district' : ['exact'],
                    'area' : ['exact'],
                 }

    def __init__(self, *args, **kwargs):
        super(VolunteerFilter, self).__init__(*args, **kwargs)
        # at startup user doen't push Submit button, and QueryDict (in data) is empty
        if self.data == {}:
            self.queryset = self.queryset.none()


class NGOFilter(django_filters.FilterSet):
    class Meta:
        model = NGO
        fields = {
                    'district' : ['exact'],
                    'area' : ['icontains']
                 }

    def __init__(self, *args, **kwargs):
        super(NGOFilter, self).__init__(*args, **kwargs)
        # at startup user doen't push Submit button, and QueryDict (in data) is empty
        if self.data == {}:
            self.queryset = self.queryset.none()


class ContribFilter(django_filters.FilterSet):
    class Meta:
        model = Contributor
        fields = {
                    'district' : ['exact'],
                    'name' : ['icontains'],
                    'phone' : ['exact'],
                    'address' : ['icontains'],
                    'commodities' : ['icontains'],
                    'status' : ['icontains'],
                 }

    def __init__(self, *args, **kwargs):
        super(ContribFilter, self).__init__(*args, **kwargs)
        # at startup user doen't push Submit button, and QueryDict (in data) is empty
        if self.data == {}:
            self.queryset = self.queryset.none()


def contributors(request):
    filter = ContribFilter(request.GET, queryset=Contributor.objects.all() )
    contrib_data = filter.qs.order_by('-id')
    paginator = Paginator(contrib_data, PER_PAGE)
    page = request.GET.get('page')
    contrib_data = paginator.get_page(page)
    contrib_data.min_page = contrib_data.number - PAGE_LEFT
    contrib_data.max_page = contrib_data.number + PAGE_RIGHT
    contrib_data.lim_page = PAGE_INTERMEDIATE
    return render(request, 'mainapp/contrib_list.html', {'filter': filter , "data" : contrib_data })


def request_list(request):
    filter = RequestFilter(request.GET, queryset=Request.objects.all() )
    req_data = filter.qs.order_by('-id')
    paginator = Paginator(req_data, PER_PAGE)
    page = request.GET.get('page')
    req_data = paginator.get_page(page)
    req_data.min_page = req_data.number - PAGE_LEFT
    req_data.max_page = req_data.number + PAGE_RIGHT
    req_data.lim_page = PAGE_INTERMEDIATE
    return render(request, 'mainapp/request_list.html', {'filter': filter , "data" : req_data })


def ngo_list(request):
    filter = NGOFilter(request.GET, queryset=NGO.objects.all() )
    ngo_data = filter.qs.order_by('-id')
    paginator = Paginator(ngo_data, PER_PAGE)
    page = request.GET.get('page')
    ngo_data = paginator.get_page(page)
    ngo_data.min_page = ngo_data.number - PAGE_LEFT
    ngo_data.max_page = ngo_data.number + PAGE_RIGHT
    ngo_data.lim_page = PAGE_INTERMEDIATE
    return render(request, 'mainapp/ngo_list.html', {'filter': filter , "data" : ngo_data })

def request_details(request, request_id=None):
    if not request_id:
        return HttpResponseRedirect("/error?error_text={}".format('Page not found!'))
    filter = RequestFilter(None)
    try:
        req_data = Request.objects.get(id=request_id)
        updates = RequestUpdate.objects.all().filter(request_id=request_id).order_by('-update_ts')
    except:
        return HttpResponseRedirect("/error?error_text={}".format('Sorry, we couldnt fetch details for that request'))
    return render(request, 'mainapp/request_details.html', {'filter' : filter, 'req': req_data, 'updates': updates })

class DistrictManagerFilter(django_filters.FilterSet):
    class Meta:
        model = DistrictManager
        fields = ['district']

    def __init__(self, *args, **kwargs):
        super(DistrictManagerFilter, self).__init__(*args, **kwargs)
        # at startup user doen't push Submit button, and QueryDict (in data) is empty
        if self.data == {}:
            self.queryset = self.queryset.none()

def districtmanager_list(request):
    filter = DistrictManagerFilter(request.GET, queryset=DistrictManager.objects.all())
    return render(request, 'mainapp/districtmanager_list.html', {'filter': filter})

class Maintenance(TemplateView):
    template_name = "mainapp/maintenance.html"

def relief_camps_data(request):
    try:
        offset = int(request.GET.get('offset'))
    except:
        offset = 0
    last_record = RescueCamp.objects.latest('id')
    relief_camp_data = (RescueCamp.objects.filter(id__gt=offset).order_by('id')[:300]).values()
    description = 'select * from mainapp_rescuecamp where id > offset order by id limit 300'
    response = {'data': list(relief_camp_data), 'meta': {'offset': offset, 'limit': 300, 'description': description,'last_record_id': last_record.id}}
    return JsonResponse(response, safe=False)

def data(request):
    try:
        offset = int(request.GET.get('offset'))
    except:
        offset = 0
    last_record = Request.objects.latest('id')
    request_data = (Request.objects.filter(id__gt=offset).order_by('id')[:300]).values()
    description = 'select * from mainapp_requests where id > offset order by id limit 300'
    response = {'data': list(request_data), 'meta': {'offset': offset, 'limit': 300, 'description': description,'last_record_id': last_record.id}}
    return JsonResponse(response, safe=False)

def mapdata(request):
    district = request.GET.get("district", "all")
    data = cache.get("mapdata:" + district)
    if data:
        return JsonResponse(list(data) , safe=False)
    if district != "all":
        data = Request.objects.exclude(latlng__exact="").filter(district=district).values()
    else:
        data = Request.objects.exclude(latlng__exact="").values()
    cache.set("mapdata:" + district, data, settings.CACHE_TIMEOUT)
    return JsonResponse(list(data) , safe=False)

def mapview(request):
    return render(request,"map.html")

def dmodash(request):
    camps = 0 ;total_people = 0 ;total_male = 0 ; total_female = 0 ; total_infant = 0 ; total_medical = 0

    for i in RescueCamp.objects.all().filter(status="active"):
        camps+=1
        total_people += ifnonezero(i.total_people)
        total_male  += ifnonezero(i.total_males)
        total_female += ifnonezero(i.total_females)
        total_infant += ifnonezero(i.total_infants)
        if(i.medical_req.strip() != ""):total_medical+=1

    return render(request , "dmodash.html",{"camp" :camps , "people" : total_people , "male" : total_male , "female" : total_female , "infant" : total_infant , "medicine" : total_medical})

def dmodist(request):
    d = []
    for district in districts:
        camps = 0 ;total_people = 0 ;total_male = 0 ; total_female = 0 ; total_infant = 0 ; total_medical = 0

        for i in RescueCamp.objects.all().filter(district = district[0] , status="active"):
            camps+=1
            total_people += ifnonezero(i.total_people)
            total_male  += ifnonezero(i.total_males)
            total_female += ifnonezero(i.total_females)
            total_infant += ifnonezero(i.total_infants)
            if(i.medical_req.strip() != ""):total_medical+=1

        d.append( { "district" : district[1] , "total_camp" : camps , "total_people" : total_people , "total_male" : total_male , "total_female" : total_female , "total_infant" : total_infant , "total_medical" : total_medical   } )
    return render(request , "dmodist.html" , {"camps" : d }  )

def dmotal(request):
    if(request.GET.get("district",-1) == -1):return render(request , "dmotal.html"  )
    dist = request.GET.get("district",-1)
    if(dist == "all"): data = RescueCamp.objects.filter(status='active').values('taluk').distinct()
    else:data = RescueCamp.objects.filter(district = dist , status='active').values('taluk').distinct()
    distmapper = {}
    for i in districts:
        distmapper[i[0]] = i[1]
    d = []
    for taluk in data :
        camps = 0 ;total_people = 0 ;total_male = 0 ; total_female = 0 ; total_infant = 0 ; total_medical = 0;district = ""
        if(dist == "all"):RCdata = RescueCamp.objects.all().filter( taluk = taluk["taluk"] , status="active")
        else:RCdata = RescueCamp.objects.all().filter( district = dist , taluk = taluk["taluk"] , status="active")
        for i in RCdata:
            camps+=1
            district = i.district
            total_people += ifnonezero(i.total_people)
            total_male  += ifnonezero(i.total_males)
            total_female += ifnonezero(i.total_females)
            total_infant += ifnonezero(i.total_infants)
            if(i.medical_req.strip() != ""):total_medical+=1

        d.append( { "district" : distmapper[district] , "taluk" : taluk["taluk"] ,"total_camp" : camps , "total_people" : total_people , "total_male" : total_male , "total_female" : total_female , "total_infant" : total_infant , "total_medical" : total_medical   } )
    return render(request , "dmotal.html" , {"camps" : d }  )


def dmocsv(request):
    if("district" not in request.GET.keys()):return HttpResponseRedirect("/")
    dist = request.GET.get("district")
    header_row = [i.name for i in RescueCamp._meta.get_fields() ][1:]  # There is a person field in the begining , to remove that
    body_rows = []
    csv_name = "{}-data".format(dist)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(csv_name)
    writer = csv.writer(response)
    writer.writerow(header_row)
    for camp in RescueCamp.objects.all().filter(district = dist , status="active"):
        row = [
            getattr(camp , key)  for key in header_row
        ]
        writer.writerow(row)


    return response

def ifnonezero(val):
    if(val == None):return 0
    return val

def dmoinfo(request):

    data = []
    for i in districts:
        req = 0 ; reqo = 0 ; reqd = 0 ; con = 0 ; cons = 0 ; vol = 0
        reqquery = Request.objects.all().filter(district = i[0])
        req = reqquery.count()
        reqo = reqquery.filter( status = "pro" ).count()
        reqd = reqquery.filter(status = "sup").count()
        contquery = Contributor.objects.all().filter(district = i[0])
        con = contquery.count()
        cons =contquery.filter(status = "ful").count()
        vol = Volunteer.objects.all().filter(district = i[0]).count()

        data.append({ "district" : i[1], "req" : req  , "reqo" : reqo , "reqd" : reqd , "con" : con , "cons" : cons , "vol" : vol})
    return render(request ,"dmoinfo.html",{"data" : data} )
def error(request):
    error_text = request.GET.get('error_text')
    return render(request , "mainapp/error.html", {"error_text" : error_text})

def logout_view(request):
    logout(request)
    # Redirect to camps page instead
    return redirect('/relief_camps')

class PersonForm(CustomForm):
    checkin_date = forms.DateField(    required=False,input_formats=["%d-%m-%Y"],help_text="Use dd-mm-yyyy format. Eg. 18-08-2018")
    checkout_date = forms.DateField(    required=False,input_formats=["%d-%m-%Y"],help_text="Use dd-mm-yyyy format. Eg. 21-08-2018")

    class Meta:
       model = Person
       fields = [
        'camped_at',
        'name',
        'phone',
        'age',
        'gender',
        'district',
        'address',
        'notes',
        'checkin_date',
        'checkout_date',
        'status'
        ]

       widgets = {
           'address': forms.Textarea(attrs={'rows':3}),
           'notes': forms.Textarea(attrs={'rows':3}),
           'gender': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
       camp_id = kwargs.pop('camp_id')
       super(PersonForm, self).__init__(*args, **kwargs)
       rescue_camp_qs = RescueCamp.objects.filter(id=camp_id)
       self.fields['camped_at'].queryset = rescue_camp_qs
       self.fields['camped_at'].initial = rescue_camp_qs.first()
       # for field_name, field in self.fields.items():
       #    print(field_name)
       #    field.widget.attrs['class'] = 'form-control'

class AddPerson(SuccessMessageMixin,LoginRequiredMixin,CreateView):
    login_url = '/login/'
    model = Person
    template_name='mainapp/add_person.html'
    form_class = PersonForm
    success_message = "'%(name)s' registered successfully"

    def get_success_url(self):
        return reverse('add_person', args=(self.camp_id,))

    def dispatch(self, request, *args, **kwargs):
        self.camp_id = kwargs.get('camp_id','')

        try:
            self.camp = RescueCamp.objects.get(id=int(self.camp_id))
        except ObjectDoesNotExist:
            raise Http404

        # Commented to allow all users to edit all camps
        # if request.user!=self.camp.data_entry_user:
        #     raise PermissionDenied

        return super(AddPerson, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(AddPerson, self).get_form_kwargs()
        kwargs['camp_id'] = self.camp_id
        return kwargs


class CampRequirementsForm(forms.ModelForm):


    class Meta:
       model = RescueCamp
       help_texts = {
            'food_req': 'Indicate the required items and approximate quantity',
            'clothing_req': 'Indicate the required items and approximate quantity',
            'medical_req': 'Indicate the required items and approximate quantity',
            'sanitary_req': 'Indicate the required items and approximate quantity',
            'other_req': 'Indicate the required items and approximate quantity',
        }
       fields = [
        'name',
        'total_people',
        'total_males',
        'total_females',
        'total_infants',
        'food_req',
        'clothing_req',
        'sanitary_req',
        'medical_req',
        'other_req'
        ]
       read_only = ('name',)
       widgets = {
           'name': forms.Textarea(attrs={'rows':1,'readonly':True}),
           'food_req': forms.Textarea(attrs={'rows':3}),
           'clothing_req': forms.Textarea(attrs={'rows':3}),
           'medical_req': forms.Textarea(attrs={'rows':3}),
           'sanitary_req': forms.Textarea(attrs={'rows':3}),
           'other_req': forms.Textarea(attrs={'rows':3}),
       }

class CampRequirements(SuccessMessageMixin,LoginRequiredMixin,UpdateView):
    login_url = '/login/'
    model = RescueCamp
    template_name='mainapp/camp_requirements.html'
    form_class = CampRequirementsForm
    success_url = '/coordinator_home/'
    success_message = "Updated requirements saved!"

    # Commented to allow all users to edit all camps
    # def dispatch(self, request, *args, **kwargs):
    #     if request.user!=self.get_object().data_entry_user:
    #         raise PermissionDenied
    #     return super(CampDetails, self).dispatch(
    #         request, *args, **kwargs)


class CampDetailsForm(forms.ModelForm):
    class Meta:
       model = RescueCamp
       fields = [
        'name',
        'location',
        'district',
        'taluk',
        'village',
        'contacts',
        'facilities_available',
        'map_link',
        'latlng',
        ]

class CampDetails(SuccessMessageMixin,LoginRequiredMixin,UpdateView):
    login_url = '/login/'
    model = RescueCamp
    template_name='mainapp/camp_details.html'
    form_class = CampDetailsForm
    success_url = '/coordinator_home/'
    success_message = "Details saved!"

    # Commented to allow all users to edit all camps
    # def dispatch(self, request, *args, **kwargs):
    #     if request.user!=self.get_object().data_entry_user:
    #         raise PermissionDenied
    #     return super(CampDetails, self).dispatch(
    #         request, *args, **kwargs)


class PeopleFilter(django_filters.FilterSet):
    fields = ['name', 'phone','address','district','notes','gender','camped_at']

    class Meta:
        model = Person
        fields = {
            'name' : ['icontains'],
            'phone' : ['icontains'],
            'address' : ['icontains'],
            'district' : ['exact'],
            'notes':['icontains'],
            'gender':['exact'],
            'camped_at':['exact']
        }

        # TODO - field order seems to not be working!
        # field_order = ['name', 'phone', 'address','district','notes','gender','camped_at']

    def __init__(self, *args, **kwargs):
        super(PeopleFilter, self).__init__(*args, **kwargs)
        if self.data == {}:
            self.queryset = self.queryset.all()

def find_people(request):
    filter = PeopleFilter(request.GET, queryset=Person.objects.all())
    people = filter.qs.order_by('name','-added_at')
    paginator = Paginator(people, PER_PAGE)
    page = request.GET.get('page')
    people = paginator.get_page(page)
    people.min_page = people.number - PAGE_LEFT
    people.max_page = people.number + PAGE_RIGHT
    people.lim_page = PAGE_INTERMEDIATE

    return render(request, 'mainapp/people.html', {'filter': filter , "data" : people })

def announcements(request):
    link_data = Announcements.objects.filter(is_pinned=False).order_by('-id').all()
    pinned_data = Announcements.objects.filter(is_pinned=True).order_by('-id').all()[:5]
    # As per the discussions orddering by id hoping they would be addded in order
    paginator = Paginator(link_data, 10)
    page = request.GET.get('page')
    link_data = paginator.get_page(page)
    return render(request, 'announcements.html', {'filter': filter, "data" : link_data,
                                                  'pinned_data': pinned_data})


class CoordinatorCampFilter(django_filters.FilterSet):
    class Meta:
        model = RescueCamp
        fields = {
            'district' : ['exact'],
            'name' : ['icontains']
        }

    def __init__(self, *args, **kwargs):
        super(CoordinatorCampFilter, self).__init__(*args, **kwargs)
        if self.data == {}:
            self.queryset = self.queryset.none()


class PrivateCampFilter(django_filters.FilterSet):
    class Meta:
        model = PrivateRescueCamp
        fields = {
            'district' : ['exact'],
            'name' : ['icontains']
        }

    def __init__(self, *args, **kwargs):
        super(PrivateCampFilter, self).__init__(*args, **kwargs)
        if self.data == {}:
            self.queryset = self.queryset.none()


@login_required(login_url='/login/')
def coordinator_home(request):
    filter = CoordinatorCampFilter(request.GET, queryset=RescueCamp.objects.all())
    data = filter.qs.annotate(count=Count('person')).order_by('district','name').all()
    paginator = Paginator(data, 50)
    page = request.GET.get('page')
    data = paginator.get_page(page)

    return render(request, "mainapp/coordinator_home.html", {'filter': filter , 'data' : data})

class CampRequirementsFilter(django_filters.FilterSet):
    class Meta:
        model = RescueCamp
        fields = {
            'district' : ['exact'],
            'name' : ['icontains'],
            'taluk' : ['icontains'],
            'village' : ['icontains']
        }

    def __init__(self, *args, **kwargs):
        super(CampRequirementsFilter, self).__init__(*args, **kwargs)
        if self.data == {}:
            self.queryset = self.queryset.none()

class VolunteerConsent(UpdateView):
    model = Volunteer
    fields = ['has_consented']
    success_url = '/consent_success/'

    def dispatch(self, request, *args, **kwargs):
        timestamp = parser.parse(self.get_object().joined.isoformat())
        timestamp = calendar.timegm(timestamp.utctimetuple())
        timestamp = str(timestamp)[-4:]
        request_ts = kwargs['ts']

        if request_ts != timestamp:
            return HttpResponseRedirect("/error?error_text={}".format('Sorry, we couldnt fetch volunteer info'))
        return super(VolunteerConsent, self).dispatch(request, *args, **kwargs)


class ConsentSuccess(TemplateView):
    template_name = "mainapp/volunteer_consent_success.html"

def camp_requirements_list(request):
    filter = CampRequirementsFilter(request.GET, queryset=RescueCamp.objects.all())
    camp_data = filter.qs.order_by('name')
    paginator = Paginator(camp_data, 50)
    page = request.GET.get('page')
    data = paginator.get_page(page)
    return render(request, "mainapp/camp_requirements_list.html", {'filter': filter , 'data' : data})

class RequestUpdateView(CreateView):
    model = RequestUpdate
    template_name='mainapp/request_update.html'
    fields = [
        'status',
        'other_status',
        'updater_name',
        'updater_phone',
        'notes'
    ]
    success_url = '/req_update_success/'

    def original_request(self):
        return self.original_request

    def updates(self):
        return self.updates

    #@method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        #could not use login_required decorator because it redirects to /accounts/login and we need /login
        #disable authentication
        # if not request.user.is_authenticated:
        #     return redirect('/login'+'?next=request_updates/'+kwargs['request_id']+'/')

        self.original_request = get_object_or_404(Request, pk=kwargs['request_id'])
        self.updates = RequestUpdate.objects.all().filter(request_id=kwargs['request_id']).order_by('-update_ts')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.request = self.original_request
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

class ReqUpdateSuccess(TemplateView):
    template_name = "mainapp/request_update_success.html"


class CollectionCenterFilter(django_filters.FilterSet):
    class Meta:
        model = CollectionCenter
        fields = {
            'name': ['icontains'],
            'address': ['icontains'],
            'contacts': ['icontains'],
            'district': ['icontains'],
            'lsg_name': ['icontains'],
            'ward_name': ['icontains'],
            'city': ['icontains'],
         }

    def __init__(self, *args, **kwargs):
        super(CollectionCenterFilter, self).__init__(*args, **kwargs)
        if self.data == {}:
            self.queryset = self.queryset.none()


class CollectionCenterListView(ListView):
    model = CollectionCenter
    paginate_by = PER_PAGE
    ordering = ['-id']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = CollectionCenterFilter(
            self.request.GET, queryset=CollectionCenter.objects.all().order_by('-id')
        )
        return context


class CollectionCenterForm(forms.ModelForm):
    class Meta:
        model = CollectionCenter
        fields = [
            'name',
            'address',
            'contacts',
            'type_of_materials_collecting',
            'is_inside_kerala',
            'district',
            'lsg_name',
            'ward_name',
            'city',
        ]
        widgets = {
            'lsg_name': forms.Select(),
            'ward_name': forms.Select(),
        }


class CollectionCenterView(CreateView):
    model = CollectionCenter
    form_class = CollectionCenterForm
