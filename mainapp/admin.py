import csv

from django.contrib import admin
from django.core.validators import EMPTY_VALUES
from django.http import HttpResponse
from mainapp.redis_queue import bulk_csv_upload_queue
from mainapp.csvimporter import import_inmate_file


from .models import Request, Volunteer, Contributor, DistrictNeed, DistrictCollection, DistrictManager, vol_categories, \
    RescueCamp, Person, NGO, Announcements, DataCollection , PrivateRescueCamp , CollectionCenter, CsvBulkUpload


def create_csv_response(csv_name, header_row, body_rows):
    """
    Helper function for creating a CSV download HTTPResponse.

    Args:
        csv_name (str): Name of the CSV to download
        header_row (list): List of CSV column names
        body_rows (list of lists): Lists of CSV column data
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(csv_name)

    writer = csv.writer(response)
    writer.writerow(header_row)
    for row in body_rows:
        writer.writerow(row)

    return response


class RequestAdmin(admin.ModelAdmin):
    actions = ['download_csv', 'mark_as_completed', 'mark_as_new', 'mark_as_ongoing']
    readonly_fields = ('dateadded',)
    ordering = ('district',)
    list_display = ('district', 'location', 'requestee_phone', 'status', 'summarise')
    list_filter = ('district', 'status',)

    def mark_as_completed(self, request, queryset):
        queryset.update(status='sup')
        return

    def mark_as_new(self, request, queryset):
        queryset.update(status='new')
        return

    def mark_as_ongoing(self, request, queryset):
        queryset.update(status='pro')
        return

    def download_csv(self, request, queryset):
        header_row = [f.name for f in Request._meta.get_fields()]
        body_rows = queryset.values_list()
        response = create_csv_response('Requests', header_row, body_rows)

        return response


class VolunteerAdmin(admin.ModelAdmin):
    actions = ['download_csv', 'mark_inactive', 'mark_active']
    readonly_fields = ('joined',)
    list_display = ('name', 'phone', 'organisation', 'joined', 'is_active')
    list_filter = ('district', 'joined', 'is_active', 'has_consented', 'area')

    def download_csv(self, request, queryset):
        header_row = [f.name for f in Volunteer._meta.get_fields()]
        body_rows = []
        for volunteer in Volunteer.objects.all():
            row = [
                getattr(volunteer, key) if key != 'area' else volunteer.get_area_display()
                for key in header_row
            ]
            body_rows.append(row)

        response = create_csv_response('Volunteers', header_row, body_rows)
        return response

    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)

    def mark_active(self, request, queryset):
        queryset.update(is_active=True)


class NGOAdmin(admin.ModelAdmin):
    actions = ['download_csv']
    readonly_fields = ('joined',)
    list_display = ('name', 'phone', 'organisation', 'joined')
    list_filter = ('district', 'joined',)

    def download_csv(self, request, queryset):
        header_row = [f.name for f in NGO._meta.get_fields()]
        body_rows = queryset.values_list()
        # for ngo in NGO.objects.all():
        #     row = [
        #         getattr(ngo, key) if key != 'district' else ngo.get_district_display()
        #         for key in header_row
        #     ]
        #     body_rows.append(row)
        response = create_csv_response('NGOs', header_row, body_rows)
        return response


class ContributorAdmin(admin.ModelAdmin):
    actions = ['download_csv', 'mark_as_fullfulled', 'mark_as_new']
    list_filter = ('district', 'status',)
    list_display = ('district', 'name', 'phone', 'address', 'commodities', 'status')

    def download_csv(self, request, queryset):
        header_row = [f.name for f in Contributor._meta.get_fields()]
        body_rows = queryset.values_list()

        response = create_csv_response('Contributors', header_row, body_rows)
        return response

    def mark_as_fullfulled(self, request, queryset):
        queryset.update(status='ful')
        return

    def mark_as_new(self, request, queryset):
        queryset.update(status='new')
        return


class RescueCampAdmin(admin.ModelAdmin):
    actions = ['download_csv', 'download_inmates' ,  'mark_as_closed', 'mark_as_active']
    list_display = ('district', 'name', 'location', 'status', 'contacts', 'facilities_available', 'total_people',
                    'total_males', 'total_females', 'total_infants', 'food_req',
                    'clothing_req', 'sanitary_req', 'medical_req', 'other_req')
    list_filter = ('district','status')
    search_fields = ['name']

    def download_inmates(self, request, queryset):
        header_row = ('name', 'phone', 'age', 'gender', 'district', 'camped_at')
        body_rows = []
        campid = queryset[0].id
        for person in Person.objects.all().filter(camped_at__id = campid):
            row = [getattr(person, field) for field in header_row]
            body_rows.append(row)

        response = create_csv_response('InmatesOf{}'.format(queryset[0].name), header_row, body_rows)
        return response

    def get_readonly_fields(self, request, obj=None):
        fields = []

        if obj not in EMPTY_VALUES and obj.status in ['closed', 'duplicate']:
                fields = [i.name for i in obj._meta.fields if i.name not in ['status', 'data_entry_user']]

        return fields

    def download_csv(self, request, queryset):
        header_row = ('district', 'name', 'location', 'taluk' , 'village' ,  'status', 'contacts', 'facilities_available', 'total_people',
                      'total_males', 'total_females', 'total_infants', 'food_req',
                      'clothing_req', 'sanitary_req', 'medical_req', 'other_req')
        body_rows = []
        rescue_camps = queryset.all()
        for rescue_camp in rescue_camps:
            row = [getattr(rescue_camp, field) for field in header_row]
            body_rows.append(row)

        response = create_csv_response('RescueCamp', header_row, body_rows)
        return response

    def mark_as_closed(self, request, queryset):
        queryset.update(status='closed')
        return

    def mark_as_active(self, request, queryset):
        queryset.update(status='active')
        return

    def get_form(self, request, obj=None, **kwargs):
        form = super(RescueCampAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['data_entry_user'].initial = request.user.id
        return form


class AnnouncementAdmin(admin.ModelAdmin):
    fields = ['is_pinned', 'priority', 'description', 'image', 'upload']


class PersonAdmin(admin.ModelAdmin):
    actions = ['download_csv']
    list_display = ('name', 'camped_at', 'added_at', 'phone', 'age', 'gender', 'camped_at_district', 'camped_at_taluk')
    ordering = ('-added_at',)
    list_filter = ('camped_at__district', 'camped_at__taluk')

    def camped_at_taluk(self, instance):
        return instance.camped_at.taluk

    def camped_at_district(self, instance):
        return instance.camped_at.district_name

    def download_csv(self, request, queryset):
        header_row = ('name', 'phone', 'age', 'sex', 'district_name', 'camped_at')
        body_rows = []
        persons = queryset.all()
        for person in persons:
            row = [getattr(person, field) for field in header_row]
            body_rows.append(row)

        response = create_csv_response('People in relief camps', header_row, body_rows)
        return response


class DataCollectionAdmin(admin.ModelAdmin):
    list_display = ['document_name', 'document', 'tag']

class CsvBulkUploadAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        bulk_csv_upload_queue.enqueue(
            import_inmate_file, obj.pk
        )
    autocomplete_fields = ['camp']
    readonly_fields = ['is_completed']

admin.site.register(Request, RequestAdmin)
admin.site.register(Volunteer, VolunteerAdmin)
admin.site.register(Contributor, ContributorAdmin)
admin.site.register(DistrictNeed)
admin.site.register(PrivateRescueCamp)
admin.site.register(DistrictCollection)
admin.site.register(DistrictManager)
admin.site.register(CollectionCenter)
admin.site.register(RescueCamp, RescueCampAdmin)
admin.site.register(NGO, NGOAdmin)
admin.site.register(Announcements, AnnouncementAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(DataCollection, DataCollectionAdmin)
admin.site.register(CsvBulkUpload, CsvBulkUploadAdmin)
