from django.contrib import admin

# Register your models here.
from .models import Table1, Table2, CombinedTable
admin.site.register([Table1, Table2,CombinedTable])