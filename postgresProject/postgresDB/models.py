from django.db import models

# Model for the first CSV file
class Table1(models.Model):
    Date = models.CharField(max_length=100)
    Description = models.CharField(max_length=100)
    Category = models.CharField(max_length=100)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Add more fields matching the CSV columns

# Model for the second CSV file
class Table2(models.Model):
    Date = models.CharField(max_length=100)
    Description = models.CharField(max_length=100)
    Category = models.CharField(max_length=100,blank=True)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)    
    # Add more fields matching the CSV columns

# Model for the combined table
class CombinedTable(models.Model):
    Date = models.CharField(max_length=100)
    Category = models.CharField(max_length=100)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Define the combined table's structure
