import os, sys, csv

proj_path = "../"

# This is so mpythoy local_settings.py gets loaded.
os.chdir(proj_path)

# This is so Django knows where to find stuff.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "simssadb.settings")

sys.path.append(os.getcwd())

# This is so models get loaded.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from database.models.institution import Institution

with open(os.getcwd() + '/sample_data/institutions.csv')\
        as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        i = Institution(name=row[0], website=row[1])
        i.save()

    institutions = Institution.objects.all()

    for i in institutions:
        print(i.id, i.name, i.website)
