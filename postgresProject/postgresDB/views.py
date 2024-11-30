from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from .forms import CSVUploadForm
from .models import Table1, Table2, CombinedTable
import pandas as pd
from .summaryTableCreate import populate_combined_table
from .categoryCreation import assign_categories
from collections import defaultdict
import json
import random

# def home(request):
#     return HttpResponse('homepage')

category_choices = ['General','Transport','Bills','Entertainment','Gifts','Groceries','Personal care','Savings','Shopping','Eating out','Subscriptions']

def about(request):
    return HttpResponse('about')

# Home page view
def home(request):
    Table1.objects.all().delete()
    Table2.objects.all().delete()
    return render(request, 'home.html')

# Dashboard page view
def dashboard(request):
    form = CSVUploadForm()    

     # Fetch all data from Table1 and Table2
    table1_data = Table1.objects.all()  # Get all rows from Table1
    table2_data = Table2.objects.all()  # Get all rows from Table2


    return render(request, 'dashboard.html', {
        'form': form,
        'table1_data' : table1_data,
        'table2_data' : table2_data,
        'category_choices' : category_choices
        })

# CSV upload view
def upload_csv(request):
    # Delete all data from Table1 and Table2
    # Table1.objects.all().delete()
    # Table2.objects.all().delete()

    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file1 = request.FILES['csv_file1']
            file2 = request.FILES['csv_file2']
            
            # Process file1 and save to Table1
            df1 = pd.read_csv(file1, usecols=['Date', 'Name', 'Category', 'Amount'])             

            for _, row in df1.iterrows():
                Table1.objects.create(
                    Date=row['Date'],
                    Description=row['Name'],
                    Category=row['Category'],
                    Amount=row['Amount'],
                    
                )                  

            # Process file2 and save to Table2
            df2 = pd.read_csv(file2, usecols=['Date', 'Description', 'Amount'])
            print(df2)
            for _, row in df2.iterrows():
                Table2.objects.create(
                    Date=row['Date'],
                    Description=row['Description'],
                    Amount=row['Amount'],
                    
                )  

            assign_categories()          
            
            # Redirect to dashboard
            return redirect('dashboard')
    return JsonResponse({'error': 'Invalid form'}, status=400)

# CSV upload view
def summary(request):

    masterTable_data = CombinedTable.objects.all()

    # Categories to exclude
    excluded_categories = {"Income", "Transfers", "Savings"}

    # Process data for the chart
    monthly_data = defaultdict(lambda: defaultdict(float))  # Nested default dict for category sums per month
    for entry in masterTable_data:
         if entry.Category not in excluded_categories:
            month = entry.Date
            monthly_data[month][entry.Category] += float(entry.Amount)

    # Format data for Chart.js
    months = list(monthly_data.keys())
    categories = {category for data in monthly_data.values() for category in data.keys()}

     # Generate random colors for each category
    def generate_color():
        return f'rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.7)'
    
    category_colors = {category: generate_color() for category in categories}
    
    # Create dataset for each category
    datasets = []
    for category in categories:
        datasets.append({
            'label': category,
            'data': [monthly_data[month].get(category, 0) for month in months],
            'backgroundColor': category_colors[category],
            'borderColor': category_colors[category].replace('0.7', '1'),
            'borderWidth': 1
        })

    return render(request, 'summary.html', {        
        'masterTable_data' : masterTable_data,
        'months' : json.dumps(months),
        'datasets' : json.dumps(datasets),
        })

def summary_execute(request):
    # Call the function to populate CombinedTable
    populate_combined_table()
    
    # Redirect to the summary page to display the combined data
    return redirect('summary')

def update_categories(request):
    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("category_"):
                row_id = key.split("_")[1]
                category = value
                # Update the category in the database
                Table2.objects.filter(id=row_id).update(Category=category)
    return redirect('dashboard')