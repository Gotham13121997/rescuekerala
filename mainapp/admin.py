import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import Request, Volunteer, Contributor, DistrictNeed, DistrictCollection, DistrictManager, vol_categories, \
    RescueCamp, Person, NGO, Announcements, ReliefCampData


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
    list_filter = ('district', 'joined',)

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
        body_rows = []
        for ngo in NGO.objects.all():
            row = [
                getattr(ngo, key) if key != 'area' else ngo.get_area_display()
                for key in header_row
            ]
            body_rows.append(row)

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
    actions = ['download_csv']
    list_display = ('district', 'name', 'location', 'contacts', 'facilities_available', 'total_people',
                    'total_males', 'total_females', 'total_infants', 'food_req',
                    'clothing_req', 'sanitary_req', 'medical_req', 'other_req')
    list_filter = ('district',)

    def download_csv(self, request, queryset):
        header_row = ('district', 'name', 'location', 'contacts', 'facilities_available', 'total_people',
                      'total_males', 'total_females', 'total_infants', 'food_req',
                      'clothing_req', 'sanitary_req', 'medical_req', 'other_req')
        body_rows = []
        rescue_camps = queryset.all()
        for rescue_camp in rescue_camps:
            row = [getattr(rescue_camp, field) for field in header_row]
            body_rows.append(row)

        response = create_csv_response('RescueCamp', header_row, body_rows)
        return response

    def get_form(self, request, obj=None, **kwargs):
        form = super(RescueCampAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['data_entry_user'].initial = request.user.id
        return form


class AnnouncementAdmin(admin.ModelAdmin):
    fields = ['is_pinned', 'priority', 'description', 'image', 'upload']


class PersonAdmin(admin.ModelAdmin):
    actions = ['download_csv']
    list_display = ('name', 'phone', 'age', 'gender', 'district', 'camped_at')

    def download_csv(self, request, queryset):
        header_row = ('name', 'phone', 'age', 'sex', 'district_name', 'camped_at')
        body_rows = []
        persons = queryset.all()
        for person in persons:
            row = [getattr(person, field) for field in header_row]
            body_rows.append(row)

        response = create_csv_response('People in relief camps', header_row, body_rows)
        return response


class ReliefCampDataAdmin(admin.ModelAdmin):
    list_display = ['description', 'file', 'district', 'tag', 'phone']
    list_filter = ('district',)
    actions = ['mark_completed']

    def mark_completed(self, request, queryset):
        queryset.update(tag="completed")


admin.site.register(Request, RequestAdmin)
admin.site.register(Volunteer, VolunteerAdmin)
admin.site.register(Contributor, ContributorAdmin)
admin.site.register(DistrictNeed)
admin.site.register(DistrictCollection)
admin.site.register(DistrictManager)
admin.site.register(RescueCamp, RescueCampAdmin)
admin.site.register(NGO, NGOAdmin)
admin.site.register(Announcements, AnnouncementAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(ReliefCampData, ReliefCampDataAdmin)
