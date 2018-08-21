import csv
import io
from django.test import TestCase, Client
from django.urls import reverse

from mainapp.models import Request, Volunteer, Contributor, NGO
from mainapp.models import DistrictNeed


class TemplateViewTests(TestCase):
    def check_template_view_response(self, url, template_name):
        client = Client()
        response = client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        return response

    def test_loading_homepage(self):
        self.check_template_view_response('/', 'home.html')

    def test_loading_req_success(self):
        self.check_template_view_response(
            '/req_sucess/', 'mainapp/req_success.html')

    def test_loading_reg_success(self):
        self.check_template_view_response(
            '/reg_success/', 'mainapp/reg_success.html')

    def test_loading_contrib_success(self):
        self.check_template_view_response(
            '/contrib_success/', 'mainapp/contrib_success.html')

    def test_loading_disclaimer_page(self):
        self.check_template_view_response(
            '/disclaimer/', 'mainapp/disclaimer.html')

    def test_loading_about_ieee(self):
        self.check_template_view_response('/ieee/', 'mainapp/aboutieee.html')

    def test_loading_dist_needs(self):
        _ = DistrictNeed.objects.create(
            district='ekm', needs='bedsheets', cnandpts='aluva uc college')
        response = self.check_template_view_response(
            '/district_needs/', 'mainapp/district_needs.html')
        self.assertIn('district_data', response.context)
        self.assertEqual(response.context['district_data'][0].district, 'ekm')
        self.assertEqual(
            response.context['district_data'][0].needs, 'bedsheets')
        self.assertEqual(
            response.context['district_data'][0].cnandpts, 'aluva uc college')

    def test_loading_mapview(self):
        self.check_template_view_response('/map/', 'map.html')

    def test_loading_dmodash(self):
        self.check_template_view_response('/dmodash/', 'dmodash.html')

    def test_loading_ngo_volunteer_view(self):
        self.check_template_view_response(
            '/ngo-volunteer/', 'ngo_volunteer.html')


class RequestViewTests(TestCase):
    def setUp(self):
        self.url = reverse('requestview')

    def test_loading_creation_form(self):
        client = Client()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertTemplateUsed(response, 'mainapp/request_form.html')

    def test_validation_errors_in_creating_request(self):
        client = Client()
        post_data = {
            'district': '',
            'location': '',
            'latlng': '',
            'latlng_accuracy': '',
        }
        response = client.post(self.url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainapp/request_form.html')
        self.assertFormError(response, 'form', 'district',
                             'This field is required.')
        self.assertFormError(response, 'form', 'location',
                             'This field is required.')
        self.assertFormError(
            response, 'form', 'requestee_phone', 'This field is required.')
        self.assertFormError(response, 'form', 'requestee',
                             'This field is required.')
        post_data = {
            'requestee_phone': '9562854604200',
        }
        response = client.post(self.url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainapp/request_form.html')
        self.assertFormError(response, 'form', 'requestee_phone', 'Please Enter 10/11 digit mobile number or landline as 0<std code><phone number>')

    def test_creating_request(self):
        client = Client()
        post_data = {
            'district': 'pkd',
            'requestee': 'Rag Sagar',
            'requestee_phone': '09562854642',
            'location': 'Kadankode',
            'latlng': '',
            'latlng_accuracy': ''
        }
        response = client.post(self.url, post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Request.objects.count(), 1)
        req_obj = Request.objects.last()
        self.assertEqual(req_obj.district, 'pkd')
        self.assertEqual(req_obj.requestee, 'Rag Sagar')
        self.assertEqual(req_obj.location, 'Kadankode')


class RegisterVolunteerViewTests(TestCase):
    def setUp(self):
        self.url = '/volunteer/'

    def test_loading_creation_form(self):
        client = Client()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainapp/volunteer_form.html')

    def test_validation_errors_in_creation(self):
        client = Client()
        post_data = {}
        response = client.post(self.url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainapp/volunteer_form.html')
        req_fields = ['name', 'district', 'phone',
                      'organisation', 'area', 'address']
        for field in req_fields:
            self.assertFormError(response, 'form', field,
                                 'This field is required.')
        post_data = {'area': 'asdasdasd'}
        response = client.post(self.url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainapp/volunteer_form.html')
        self.assertFormError(response, 'form', 'area',
                             'Select a valid choice. asdasdasd is not one of the available choices.')

    def test_creation(self):
        client = Client()
        post_data = {
            'name': 'Rag Sagar',
            'district': 'alp',
            'phone': '8893845901',
            'organisation': 'smc',
            'area': 'plw',
            'address': 'Near mosque'
        }
        response = client.post(self.url, post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Volunteer.objects.count(), 1)
        volunteer = Volunteer.objects.last()
        self.assertEqual(volunteer.name, 'Rag Sagar')
        self.assertEqual(volunteer.district, 'alp')
        self.assertEqual(volunteer.phone, '8893845901')
        self.assertEqual(volunteer.organisation, 'smc')
        self.assertEqual(volunteer.area, 'plw')
        self.assertEqual(volunteer.address, 'Near mosque')


class RegisterNGOViewTests(TestCase):
    def setUp(self):
        self.url = '/NGO/'

    def test_loading_creation_form(self):
        client = Client()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainapp/ngo_form.html')

    def test_validation_errors_in_creation(self):
        client = Client()
        post_data = {}
        response = client.post(self.url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainapp/ngo_form.html')
        req_fields = ['organisation', 'organisation_address',
                      'organisation_type', 'description', 'area', 'location', 'name']
        for field in req_fields:
            self.assertFormError(response, 'form', field,
                                 'This field is required.')
        # post_data = {'area': 'asdasdasd'}
        # response = client.post(self.url, post_data)
        # self.assertEqual(response.status_code, 200)
        # self.assertTemplateUsed(response, 'mainapp/ngo_form.html')
        # self.assertFormError(response, 'form', 'area', 'Select a valid choice. asdasdasd is not one of the available choices.')

    def test_creation(self):
        client = Client()
        post_data = {
            'name': 'Rag Sagar',
            'phone': '8893845901',
            'organisation': 'smc',
            'area': 'plw',
            'organisation_address': 'Near mosque',
            'organisation_type': 'NGO',
            'description': 'to help poor',
            'location': 'chalakudy'
        }
        response = client.post(self.url, post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(NGO.objects.count(), 1)
        ngo = NGO.objects.last()
        self.assertEqual(ngo.name, 'Rag Sagar')
        self.assertEqual(ngo.phone, '8893845901')
        self.assertEqual(ngo.organisation, 'smc')
        self.assertEqual(ngo.area, 'plw')
        self.assertEqual(ngo.organisation_address, 'Near mosque')
        self.assertEqual(ngo.organisation_type, 'NGO')
        self.assertEqual(ngo.description, 'to help poor')
        self.assertEqual(ngo.location, 'chalakudy')


class DownloadNGOListViewTests(TestCase):
    def setUp(self):
        self.url = '/NGO/download/'

    def test_csv_download(self):
        client = Client()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response['Content-Disposition'],
                         'attachment; filename="ngo_list.csv.csv"')

    def test_single_district_ngo_list_download(self):
        ngo_data_ekm = {
            'name': 'Rag Sagar',
            'phone': '8893845901',
            'organisation': 'smc',
            'area': 'plw',
            'organisation_address': 'Near mosque',
            'organisation_type': 'NGO',
            'description': 'to help poor',
            'location': 'chalakudy',
            'district': 'ekm',
        }
        _ = NGO.objects.create(**ngo_data_ekm)
        ngo_data_tcr = {
            'name': 'Rag Sagar',
            'phone': '8893845901',
            'organisation': 'smc',
            'area': 'plw',
            'organisation_address': 'Near mosque',
            'organisation_type': 'NGO',
            'description': 'to help poor',
            'location': 'chalakudy',
            'district': 'tcr',
        }
        _ = NGO.objects.create(**ngo_data_tcr)
        client = Client()
        response = client.get(self.url, data={'district': 'ekm'})
        content = response.content.decode('utf-8')
        cvs_reader = csv.reader(io.StringIO(content))
        body = list(cvs_reader)
        headers = body.pop(0)
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
        for header in headers:
            self.assertIn(header, header_row)
        self.assertEqual(len(body), 1)
        row = body[0]
        for column in row:
            self.assertIn(column, ngo_data_ekm.values())

    def test_ngo_list_download(self):
        ngo_data = {
            'name': 'Rag Sagar',
            'phone': '8893845901',
            'organisation': 'smc',
            'area': 'plw',
            'organisation_address': 'Near mosque',
            'organisation_type': 'NGO',
            'description': 'to help poor',
            'location': 'chalakudy',
            'district': 'ekm',
        }
        _ = NGO.objects.create(**ngo_data)
        client = Client()
        response = client.get(self.url)
        content = response.content.decode('utf-8')
        cvs_reader = csv.reader(io.StringIO(content))
        body = list(cvs_reader)
        _ = body.pop(0)
        self.assertEqual(len(body), 1)
        for row in body:
            for each_col in row:
                self.assertIn(each_col, ngo_data.values())


class RegisterContributorViewTests(TestCase):
    def setUp(self):
        self.url = '/reg_contrib/'

    def test_loading_creation_form(self):
        client = Client()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainapp/contributor_form.html')
        self.assertIn('form', response.context)

    def test_validation_errors_in_creation(self):
        client = Client()
        post_data = {}
        response = client.post(self.url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mainapp/contributor_form.html')
        req_fields = ['name', 'district', 'phone', 'address', 'commodities']
        for field in req_fields:
            self.assertFormError(response, 'form', field,
                                 'This field is required.')

    def test_creation(self):
        client = Client()
        post_data = {
            'name': 'Rag Sagar',
            'district': 'pkd',
            'phone': '8893845901',
            'address': 'Near Mosque',
            'commodities': 'Shirts, Torches'
        }
        response = client.post(self.url, post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Contributor.objects.count(), 1)
        contributor = Contributor.objects.last()
        self.assertEqual(contributor.name, 'Rag Sagar')
        self.assertEqual(contributor.district, 'pkd')
        self.assertEqual(contributor.phone, '8893845901')
        self.assertEqual(contributor.address, 'Near Mosque')
