import os
import uuid
from enum import Enum

from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.urls import reverse


districts = (
    ('alp','Alappuzha - ആലപ്പുഴ'),
    ('ekm','Ernakulam - എറണാകുളം'),
    ('idk','Idukki - ഇടുക്കി'),
    ('knr','Kannur - കണ്ണൂർ'),
    ('ksr','Kasaragod - കാസർഗോഡ്'),
    ('kol','Kollam - കൊല്ലം'),
    ('ktm','Kottayam - കോട്ടയം'),
    ('koz','Kozhikode - കോഴിക്കോട്'),
    ('mpm','Malappuram - മലപ്പുറം'),
    ('pkd','Palakkad - പാലക്കാട്'),
    ('ptm','Pathanamthitta - പത്തനംതിട്ട'),
    ('tvm','Thiruvananthapuram - തിരുവനന്തപുരം'),
    ('tcr','Thrissur - തൃശ്ശൂർ'),
    ('wnd','Wayanad - വയനാട്'),
)

status_types =(
    ('new', 'New'),
    ('pro', 'In progess'),
    ('sup', 'Supplied')
)

volunteer_update_status_types = (
    ('hig', 'High priority'),
    ('med', 'Medium priority'),
    ('low', 'Low priority'),
    ('cls', 'Can be closed'),
    ('otr', 'Other')
)

contrib_status_types =(
    ('new', 'New'),
    ('ful', 'Fullfilled'),
)

relief_camp_status = (
    ('active', 'Active'),
    ('closed', 'Closed'),
    ('duplicate', 'Duplicate')
)

vol_categories = (
    ('dcr', 'Doctor'),
    ('hsv', 'Health Services'),
    ('elw', 'Electrical Works'),
    ('mew', 'Mechanical Work'),
    ('cvw', 'Civil Work'),
    ('plw', 'Plumbing work'),
    ('vls', 'Vehicle Support'),
    ('ckg', 'Cooking'),
    ('rlo', 'Relief operation'),
    ('cln', 'Cleaning'),
    ('bot', 'Boat Service'),
    ('rck', 'Rock Climbing'),
    ('oth', 'Other')
)

gender =(
    (0,'Male'),
    (1,'Female'),
    (2,'Others')
)

announcement_types =(
    (0,'General'),
    (1,'Food'),
    (2,'Camps'),
    (3,'Weather'),
    (4, 'All'),
)

announcement_priorities = [
    ('H', 'High'),
    ('M', 'Medium'),
    ('L', 'Low')]

person_status = (
    ('new', 'New'),
    ('checked_out', 'Checked Out'),
    ('closed', 'Closed')
)

class LSGTypes(Enum):
    CORPORATION = 0
    MUNICIPALITY = 1
    GRAMA_PANCHAYATH = 2


class Request(models.Model):
    district = models.CharField(
        max_length = 15,
        choices = districts,
        verbose_name='District - ജില്ല'
    )
    location = models.CharField(max_length=500,verbose_name='Location - സ്ഥലം')
    requestee = models.CharField(max_length=100,verbose_name='Requestee - അപേക്ഷകന്‍റെ പേര്')

    phone_number_regex = RegexValidator(regex='^((\+91|91|0)[\- ]{0,1})?[456789]\d{9}$', message='Please Enter 10/11 digit mobile number or landline as 0<std code><phone number>', code='invalid_mobile')
    requestee_phone = models.CharField(max_length=14,verbose_name='Requestee Phone - അപേക്ഷകന്‍റെ ഫോണ്‍ നമ്പര്‍', validators=[phone_number_regex])

    latlng = models.CharField(max_length=100, verbose_name='GPS Coordinates - GPS നിർദ്ദേശാങ്കങ്ങൾ ', blank=True)
    latlng_accuracy = models.CharField(max_length=100, verbose_name='GPS Accuracy - GPS കൃത്യത ', blank=True)
    #  If it is enabled no need to consider lat and lng
    is_request_for_others = models.BooleanField(
        verbose_name='Requesting for others - മറ്റൊരാൾക്ക് വേണ്ടി അപേക്ഷിക്കുന്നു  ', default=False,
        help_text="If it is enabled, no need to consider lat and lng")

    needwater = models.BooleanField(verbose_name='Water - വെള്ളം')
    needfood = models.BooleanField(verbose_name='Food - ഭക്ഷണം')
    needcloth = models.BooleanField(verbose_name='Clothing - വസ്ത്രം')
    needmed = models.BooleanField(verbose_name='Medicine - മരുന്നുകള്‍')
    needtoilet = models.BooleanField(verbose_name='Toiletries - ശുചീകരണ സാമഗ്രികള്‍ ')
    needkit_util = models.BooleanField(verbose_name='Kitchen utensil - അടുക്കള സാമഗ്രികള്‍')
    needrescue = models.BooleanField(verbose_name='Need rescue - രക്ഷാപ്രവർത്തനം ആവശ്യമുണ്ട്')

    detailwater = models.CharField(max_length=250, verbose_name='Details for required water - ആവശ്യമായ വെള്ളത്തിന്‍റെ വിവരങ്ങള്‍', blank=True)
    detailfood = models.CharField(max_length=250, verbose_name='Details for required food - ആവശ്യമായ ഭക്ഷണത്തിന്‍റെ വിവരങ്ങള്‍', blank=True)
    detailcloth = models.CharField(max_length=250, verbose_name='Details for required clothing - ആവശ്യമായ വസ്ത്രത്തിന്‍റെ വിവരങ്ങള്‍', blank=True)
    detailmed = models.CharField(max_length=250, verbose_name='Details for required medicine - ആവശ്യമായ മരുന്നിന്‍റെ  വിവരങ്ങള്‍', blank=True)
    detailtoilet = models.CharField(max_length=250, verbose_name='Details for required toiletries - ആവശ്യമായ  ശുചീകരണ സാമഗ്രികള്‍', blank=True)
    detailkit_util = models.CharField(max_length=250, verbose_name='Details for required kitchen utensil - ആവശ്യമായ അടുക്കള സാമഗ്രികള്‍', blank=True)
    detailrescue = models.CharField(max_length=250, verbose_name='Details for rescue action - രക്ഷാപ്രവർത്തനം വിവരങ്ങള്', blank=True)

    needothers = models.CharField(max_length=500, verbose_name="Other needs - മറ്റു ആവശ്യങ്ങള്‍", blank=True)
    status = models.CharField(
        max_length = 10,
        choices = status_types,
        default = 'new'
    )
    supply_details = models.CharField(max_length=100, blank=True)
    dateadded = models.DateTimeField(auto_now_add=True)

    def summarise(self):
        out = ""
        if(self.needwater):
            out += "Water Requirements :\n {}".format(self.detailwater)
        if(self.needfood):
            out += "\nFood Requirements :\n {}".format(self.detailfood)
        if(self.needcloth):
            out += "\nCloth Requirements :\n {}".format(self.detailcloth)
        if(self.needmed):
            out += "\nMedicine Requirements :\n {}".format(self.detailmed)
        if(self.needtoilet):
            out += "\nToilet Requirements :\n {}".format(self.detailtoilet)
        if(self.needkit_util):
            out += "\nKit Requirements :\n {}".format(self.detailkit_util)
        if(len(self.needothers.strip()) != 0):
            out += "\nOther Needs :\n {}".format(self.needothers)
        return out

    class Meta:
        verbose_name = 'Rescue: Request'
        verbose_name_plural = 'Rescue:Requests'

    def __str__(self):
        return self.get_district_display() + ' ' + self.location


class Volunteer(models.Model):
    district = models.CharField(
        max_length = 15,
        choices = districts,
        verbose_name="District - ജില്ല"
    )
    name = models.CharField(max_length=100, verbose_name="Name - പേര്")

    phone_number_regex = RegexValidator(regex='^((\+91|91|0)[\- ]{0,1})?[456789]\d{9}$', message='Please Enter 10 digit mobile number or landline as 0<std code><phone number>', code='invalid_mobile')
    phone = models.CharField(max_length=14, verbose_name="Phone - ഫോണ്‍ നമ്പര്‍", validators=[phone_number_regex])

    organisation = models.CharField(max_length=250, verbose_name="Organization (സംഘടന) / Institution")
    address = models.TextField(verbose_name="Address - വിലാസം")
    area = models.CharField(
        max_length = 15,
        choices = vol_categories,
        verbose_name = "Area of volunteering - സന്നദ്ധസേവനം"
    )
    is_spoc = models.BooleanField(default=False, verbose_name="Is point of contact")
    joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    has_consented = models.BooleanField(default=False, verbose_name="Available")

    class Meta:
        verbose_name = 'Volunteer: Individual'
        verbose_name_plural = 'Volunteers: Individuals'

    def __str__(self):
        return self.name


class NGO(models.Model):
    district = models.CharField(
        max_length = 15,
        choices = districts,
    )
    organisation = models.CharField(max_length=250, verbose_name="Name of Organization (സംഘടനയുടെ പേര്)")
    organisation_type = models.CharField(max_length=250, verbose_name="Type of Organization")
    organisation_address = models.TextField(default='', verbose_name="Address of Organization")
    name = models.CharField(max_length=100, verbose_name="Contact Person")
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True) # validators should be a list
    description = models.TextField(verbose_name="About Organisation")
    area = models.TextField(
        verbose_name = "Area of volunteering"
    )
    location = models.CharField(
        max_length=500,
        verbose_name="Preferred Location to Volunteer"
    )
    is_spoc = models.BooleanField(default=False, verbose_name="Is point of contact")
    joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Volunteer: NGO'
        verbose_name_plural = 'Volunteers: NGOs'

    def __str__(self):
        return self.name


class Contributor(models.Model):
    district = models.CharField(
        max_length = 15,
        choices = districts,
        verbose_name="District - ജില്ല"
    )
    name = models.CharField(max_length=100, verbose_name="Name - പേര്")

    phone_number_regex = RegexValidator(regex='^((\+91|91|0)[\- ]{0,1})?[456789]\d{9}$', message='Please Enter 10 digit mobile number or landline as 0<std code><phone number>', code='invalid_mobile')
    phone = models.CharField(max_length=14, verbose_name="Phone - ഫോണ്‍ നമ്പര്‍", validators=[phone_number_regex])

    address = models.TextField(verbose_name="Address - വിലാസം")
    commodities = models.TextField(verbose_name="What you can contribute. ( സംഭാവന ചെയ്യാന്‍ ഉദ്ദേശിക്കുന്ന സാധനങ്ങള്‍ ) -- Eg: Shirts, torches etc ")
    status = models.CharField(
        max_length = 10,
        choices = contrib_status_types,
        default = 'new'
    )

    class Meta:
        verbose_name = 'Contributor: Donation'
        verbose_name_plural = 'Contributors: Donations'

    def __str__(self):
        return self.name + ' ' + self.get_district_display()


class DistrictManager(models.Model):
    district = models.CharField(
        max_length = 15,
        choices = districts,
        verbose_name="District - ജില്ല"
    )
    name = models.CharField(max_length=100, verbose_name="Name - പേര്")
    phone = models.CharField(max_length=11, verbose_name="Phone - ഫോണ്‍ നമ്പര്‍")
    email = models.CharField(max_length=100, verbose_name="Email - ഇമെയിൽ")

    class Meta:
        verbose_name = 'District: Manager'
        verbose_name_plural = 'District: Managers'

    def __str__(self):
        return self.name + ' ' + self.get_district_display()


class DistrictNeed(models.Model):
    district = models.CharField(
        max_length = 15,
        choices = districts,
    )
    needs = models.TextField(verbose_name="Items required")
    cnandpts = models.TextField(verbose_name="Contacts and collection points") #contacts and collection points

    class Meta:
        verbose_name = 'District: Need'
        verbose_name_plural = 'District: Needs'

    def __str__(self):
        return self.get_district_display()


class DistrictCollection(models.Model):
    district = models.CharField(
        max_length=15,
        choices=districts
    )
    collection = models.TextField(
        verbose_name="Details of collected items"
    )

    class Meta:
        verbose_name = 'District: Collection'
        verbose_name_plural = 'District: Collections'


class RescueCamp(models.Model):
    name = models.CharField(max_length=50,verbose_name="Camp Name - ക്യാമ്പിന്റെ പേര്")
    location = models.TextField(verbose_name="Address - അഡ്രസ്",blank=True,null=True)
    district = models.CharField(
        max_length=15,
        choices=districts
    )
    taluk = models.CharField(max_length=50,verbose_name="Taluk - താലൂക്ക്")
    village = models.CharField(max_length=50,verbose_name="Village - വില്ലജ്")
    contacts = models.TextField(verbose_name="Phone Numbers - ഫോൺ നമ്പറുകൾ",blank=True,null=True)
    facilities_available = models.TextField(
        blank=True,
        null=True,
        verbose_name="Facilities Available (light, kitchen, toilets etc.) - ലഭ്യമായ സൗകര്യങ്ങൾ"
    )
    data_entry_user = models.ForeignKey(User,models.SET_NULL,blank=True,null=True,help_text="This camp's coordinator page will be visible only to this user")
    map_link = models.CharField(max_length=250, verbose_name='Map link',blank=True,null=True,help_text="Copy and paste the full Google Maps link")
    latlng = models.CharField(max_length=100, verbose_name='GPS Coordinates', blank=True,help_text="Comma separated latlng field. Leave blank if you don't know it")

    total_people = models.IntegerField(null=True,blank=True,verbose_name="Total Number of People")
    total_males = models.IntegerField(null=True,blank=True,verbose_name="Number of Males")
    total_females = models.IntegerField(null=True,blank=True,verbose_name="Number of Females")
    total_infants = models.IntegerField(null=True,blank=True,verbose_name="Number of Infants (<2y)")

    food_req = models.TextField(blank=True,null=True,verbose_name="Food - ഭക്ഷണം")
    clothing_req = models.TextField(blank=True,null=True,verbose_name="Clothing - വസ്ത്രം")
    sanitary_req = models.TextField(blank=True,null=True,verbose_name="Sanitary - സാനിറ്ററി")
    medical_req = models.TextField(blank=True,null=True,verbose_name="Medical - മെഡിക്കൽ")
    other_req = models.TextField(blank=True,null=True,verbose_name="Other - മറ്റുള്ളവ")

    status = models.CharField(
        max_length = 10,
        choices = relief_camp_status,
        default = 'active',
    )

    class Meta:
        verbose_name = 'Relief: Camp'
        verbose_name_plural = "Relief: Camps"


    def __str__(self):
        return self.name


class PrivateRescueCamp(models.Model):
    lsg_types = [
        (LSGTypes.CORPORATION.value, 'Corporation'),
        (LSGTypes.MUNICIPALITY.value, 'Municipality'),
        (LSGTypes.GRAMA_PANCHAYATH.value, 'Grama Panchayath')
    ]

    name = models.CharField(max_length=50,verbose_name="Camp Name - ക്യാമ്പിന്റെ പേര്")
    location = models.TextField(verbose_name="Address - അഡ്രസ്",blank=True,null=True)
    district = models.CharField(
        max_length=15,
        choices=districts
    )
    lsg_type = models.SmallIntegerField(
        choices=lsg_types,
        verbose_name='LSG Type - തദ്ദേശ സ്വയംഭരണ സ്ഥാപനം',
        null=True, blank=True
    )
    lsg_name = models.CharField(max_length=150, null=True, blank=True, verbose_name="LSG Name - സ്വയംഭരണ സ്ഥാപനത്തിന്റെ പേര്")
    ward_name = models.CharField(max_length=150, null=True, blank=True, verbose_name="Ward - വാർഡ്")
    is_inside_kerala = models.BooleanField(verbose_name="Center inside kerala? - കേന്ദ്രം കേരളത്തിലാണോ")
    city = models.CharField(max_length=150, verbose_name="City - നഗരം")
    contacts = models.TextField(verbose_name="Phone Numbers - ഫോൺ നമ്പറുകൾ",blank=True,null=True)
    facilities_available = models.TextField(
        blank=True,
        null=True,
        verbose_name="Facilities Available (light, kitchen, toilets etc.) - ലഭ്യമായ സൗകര്യങ്ങൾ"
    )
    map_link = models.CharField(max_length=250, verbose_name='Map link',blank=True,null=True,help_text="Copy and paste the full Google Maps link")
    latlng = models.CharField(max_length=100, verbose_name='GPS Coordinates', blank=True,help_text="Comma separated latlng field. Leave blank if you don't know it")

    total_people = models.IntegerField(null=True,blank=True,verbose_name="Total Number of People")
    total_males = models.IntegerField(null=True,blank=True,verbose_name="Number of Males")
    total_females = models.IntegerField(null=True,blank=True,verbose_name="Number of Females")
    total_infants = models.IntegerField(null=True,blank=True,verbose_name="Number of Infants (<2y)")

    food_req = models.TextField(blank=True,null=True,verbose_name="Food - ഭക്ഷണം")
    clothing_req = models.TextField(blank=True,null=True,verbose_name="Clothing - വസ്ത്രം")
    sanitary_req = models.TextField(blank=True,null=True,verbose_name="Sanitary - സാനിറ്ററി")
    medical_req = models.TextField(blank=True,null=True,verbose_name="Medical - മെഡിക്കൽ")
    other_req = models.TextField(blank=True,null=True,verbose_name="Other - മറ്റുള്ളവ")

    status = models.CharField(
        max_length = 10,
        choices = relief_camp_status,
        default = 'active',
    )

    class Meta:
        verbose_name = 'Private Relief: Camp'
        verbose_name_plural = "Private Relief: Camps"


    def __str__(self):
        return self.name


class Person(models.Model):
    name = models.CharField(max_length=30,blank=False,null=False,verbose_name="Name - പേര്")
    phone = models.CharField(max_length=11,null=True,blank=True,verbose_name='Mobile - മൊബൈൽ')
    age = models.IntegerField(null=True,blank=True,verbose_name="Age - പ്രായം")
    gender = models.IntegerField(
        choices = gender,
        verbose_name='Gender - ലിംഗം',
        null=True,blank=True
    )
    address = models.TextField(max_length=150,null=True,blank=True,verbose_name="Address - വിലാസം")
    district = models.CharField(
        max_length = 15,
        choices = districts,
        verbose_name='Residence District - താമസിക്കുന്ന ജില്ല',
        null=True,blank=True
    )
    notes = models.TextField(max_length=500,null=True,blank=True,verbose_name='Notes - കുറിപ്പുകൾ')
    camped_at = models.ForeignKey(RescueCamp,models.CASCADE,blank=False,null=False,verbose_name='Camp Name - ക്യാമ്പിന്റെ പേര്')
    added_at = models.DateTimeField(auto_now_add=True)

    checkin_date = models.DateTimeField(null=True,blank=True,verbose_name='Check-in Date - ചെക്ക്-ഇൻ തീയതി')
    checkout_date = models.DateTimeField(null=True,blank=True,verbose_name='Check-out Date - ചെക്ക്-ഔട്ട് തീയതി')

    status = models.CharField(
        blank=True,
        null=True,
        max_length = 15,
        choices = person_status,
        default = None,
    )

    @property
    def sex(self):
        return {
            0:'Male',
            1:'Female',
            2:'Others'
        }.get(self.gender, 'Unknown')

    @property
    def district_name(self):
        return {
                'alp':'Alappuzha - ആലപ്പുഴ',
                'ekm':'Ernakulam - എറണാകുളം',
                'idk':'Idukki - ഇടുക്കി',
                'knr':'Kannur - കണ്ണൂർ',
                'ksr':'Kasaragod - കാസർഗോഡ്',
                'kol':'Kollam - കൊല്ലം',
                'ktm':'Kottayam - കോട്ടയം',
                'koz':'Kozhikode - കോഴിക്കോട്',
                'mpm':'Malappuram - മലപ്പുറം',
                'pkd':'Palakkad - പാലക്കാട്',
                'ptm':'Pathanamthitta - പത്തനംതിട്ട',
                'tvm':'Thiruvananthapuram - തിരുവനന്തപുരം',
                'tcr':'Thrissur - തൃശ്ശൂർ',
                'wnd':'Wayanad - വയനാട്',
                }.get(self.district, 'Unknown')

    class Meta:
        verbose_name = 'Relief: Refugee'
        verbose_name_plural = "Relief: Refugees"

    def __str__(self):
        return self.name


def upload_to(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('media/', filename)


class Announcements(models.Model):
    dateadded = models.DateTimeField(auto_now_add=True)
    priority = models.CharField(
        max_length=20,
        choices = announcement_priorities,
        verbose_name='Priority',
        default='L')

    description = models.TextField(blank=True)
    image = models.ImageField(blank=True, upload_to=upload_to)
    upload = models.FileField(blank=True, upload_to=upload_to)
    is_pinned = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Announcement: News'
        verbose_name_plural = 'Announcements: News'

    def __str__(self):
        return self.description[:100]


class DataCollection(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    document_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Document name"
    )
    document = models.FileField(blank=True, upload_to='camp_data')
    tag = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = 'Data: Collection'
        verbose_name_plural = 'Data: Collections'

    def __str__(self):
        return self.document_name


class RequestUpdate(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    status = models.CharField(
            max_length = 10,
            choices = volunteer_update_status_types
        )

    other_status = models.CharField(max_length=255, verbose_name='Please specify other status', default='', blank=True)
    updater_name = models.CharField(max_length=100, verbose_name='Name of person or group updating', blank=False)

    phone_number_regex = RegexValidator(regex='^((\+91|91|0)[\- ]{0,1})?[456789]\d{9}$', message='Please Enter 10/11 digit mobile number or landline as 0<std code><phone number>', code='invalid_mobile')
    updater_phone = models.CharField(max_length=14,verbose_name='Phone number of person or group updating', validators=[phone_number_regex])

    notes = models.TextField(verbose_name='Volunteer comments', blank=True)

    update_ts = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.get_status_display()


class CollectionCenter(models.Model):

    lsg_types = [
        (LSGTypes.CORPORATION.value, 'Corporation'),
        (LSGTypes.MUNICIPALITY.value, 'Municipality'),
        (LSGTypes.GRAMA_PANCHAYATH.value, 'Grama Panchayath')
    ]

    name = models.CharField(max_length=100, blank=False, null=False, verbose_name="Name - പേര്")
    address = models.TextField(verbose_name="Address - വിലാസം")
    contacts = models.CharField(max_length=250, null=True, blank=True, verbose_name='Contacts - മൊബൈൽ')
    type_of_materials_collecting = models.TextField(
        verbose_name="Type of materials collecting - ശേഖരിക്കുന്ന വസ്തുക്കൾ ",
        null=True, blank=True
    )
    district = models.CharField(
        max_length=15,
        choices=districts,
        verbose_name='Ceter District - ജില്ല',
        null=True, blank=True
    )
    lsg_type = models.SmallIntegerField(
        choices=lsg_types,
        verbose_name='LSG Type - തദ്ദേശ സ്വയംഭരണ സ്ഥാപനം',
        null=True, blank=True
    )
    lsg_name = models.CharField(max_length=150, null=True, blank=True, verbose_name="LSG Name - സ്വയംഭരണ സ്ഥാപനത്തിന്റെ പേര്")
    ward_name = models.CharField(max_length=150, null=True, blank=True, verbose_name="Ward - വാർഡ്")
    is_inside_kerala = models.BooleanField(default=True, verbose_name="Center inside kerala? - കേന്ദ്രം കേരളത്തിലാണോ")
    city = models.CharField(null=True, blank=True, max_length=150, verbose_name="City - നഗരം")
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('collection_centers_list')


class CsvBulkUpload(models.Model):
    name = models.CharField(max_length=20)
    csv_file = models.FileField(upload_to=upload_to)

    def __str__(self):
        return self.name
