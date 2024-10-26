from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from .forms import CSVUploadForm
from .models import Table1, Table2, CombinedTable
import pandas as pd
from .summaryTableCreate import populate_combined_table

# def home(request):
#     return HttpResponse('homepage')

def about(request):
    return HttpResponse('about')

# Home page view
def home(request):
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
        'table2_data' : table2_data
        })

# CSV upload view
def upload_csv(request):
    # Fetch all data from Table1 and Table2
    Table1.objects.all().delete()
    Table2.objects.all().delete()

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
                    # Add more fields as necessary
                )                  

            # Process file2 and save to Table2
            df2 = pd.read_csv(file2, usecols=['Date', 'Description', 'Amount'])
            print(df2)
            for _, row in df2.iterrows():
                Table2.objects.create(
                    Date=row['Date'],
                    Description=row['Description'],
                    Amount=row['Amount'],
                    # Add more fields as necessary
                )            
            
            # Redirect to a success page or dashboard
            return redirect('dashboard')
    return JsonResponse({'error': 'Invalid form'}, status=400)

# CSV upload view
def summary(request):

    masterTable_data = CombinedTable.objects.all()

    return render(request, 'summary.html', {        
        'masterTable_data' : masterTable_data
        })

def summary_execute(request):
    # Call the function to populate CombinedTable
    populate_combined_table()
    
    # Redirect to the summary page to display the combined data
    return redirect('summary')