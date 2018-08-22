import datetime
from hashlib import md5
from redis import Redis
import csv
import codecs




def parsedate(str):
    try:
        if( len(str) > 1 ):
            splitted = str.split("/")
            if( len(splitted) == 3 ):
                if( len(splitted[-1]) == 2 ):
                    return datetime.datetime.strptime(str, "%d/%m/%y" )
                else:
                    return datetime.datetime.strptime(str, "%d/%m/%Y" )
        return None
    except :
        print(str)
        return None

def import_inmate_file(csvid):

    import django
    django.setup()

    from mainapp.models import Person, RescueCamp, CsvBulkUpload

    upload = CsvBulkUpload.objects.get(id = csvid)
    upload.csv_file.open(mode="rb")
    new_data = csv.DictReader(codecs.iterdecode(upload.csv_file.file, 'utf-8'))

    for datum in new_data:
        '''
        try:
            identifier_str = (datum.get("phone", "") + datum.get("name","") + datum.get("age",0)).encode('utf-8')
            identifier = md5(identifier_str).hexdigest()
            #this will fail. we should deal with the removed unique_identifier
            p = Person.objects.get(unique_identifier=identifier)
        except ValueError as e:
            print("Invalid camp ID. row = "+ str(datum))
        except RescueCamp.DoesNotExist as e:
            print("Camp does not exist. row = "+ str(datum))

        except Person.DoesNotExist:
        '''
        gender = 2
        if( len(datum.get("gender", "")) > 0 ):
            if(datum.get("gender", "")[0] == "m" or datum.get("gender", "")[0] == "M"):
                gender = 0
            elif(datum.get("gender", "")[0] == "f" or datum.get("gender", "")[0] == "F"):
                gender = 1
        age = '-1'
        if(datum.get("age", "").strip() != ""):
           age = datum.get("age", "").strip()


        Person(
            name = datum.get("name", ""),
            phone = datum.get("phone", ""),
            age = age,
            gender = gender,
            address = datum.get("address", ""),
            notes = datum.get("notes", ""),
            camped_at = upload.camp ,
            district = datum.get("district", "").lower(),
            status = "new",
            checkin_date = parsedate(datum.get("checkin_date", None)),
            checkout_date = parsedate(datum.get("checkout_date", None))
        ).save()
    CsvBulkUpload.objects.filter(id = csvid).update(is_completed = True)



#For Shell Testing
#exec(open('mainapp/csvimporter.py').read())
