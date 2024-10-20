from django.db import models

# Model for the first CSV file
class Table1(models.Model):
    Date = models.CharField(max_length=100)
    Description = models.CharField(max_length=100)
    Category = models.CharField(max_length=100)
    Amount = models.IntegerField()
    # Add more fields matching the CSV columns

# Model for the second CSV file
class Table2(models.Model):
    Date = models.CharField(max_length=100)
    Description = models.CharField(max_length=100)
    Amount = models.IntegerField()
    # Add more fields matching the CSV columns

# Model for the combined table
class CombinedTable(models.Model):
    combined_column1 = models.CharField(max_length=100)
    combined_column2 = models.IntegerField()
    # Define the combined table's structure
