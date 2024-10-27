from .models import Table1, Table2, CombinedTable
from django.db.models import Sum
import pandas as pd

def populate_combined_table():
    # Clear the existing data in CombinedTable if you want to avoid duplicates
    CombinedTable.objects.all().delete()

    # Retrieve data from Table1 and populate CombinedTable
    table1_data = Table1.objects.exclude(Description__icontains = "AMERICAN EXP").values('Date','Description', 'Category', 'Amount')
    df1 = pd.DataFrame(table1_data)

    if not df1.empty:
        df1['Date'] = pd.to_datetime(df1['Date'], format='%d/%m/%Y')
        df1['MonthYear'] = df1['Date'].dt.to_period('M')        

    # Create a DataFrame for Table2 and process date column (assuming no Category)
    table2_data = Table2.objects.exclude(Description = "PAYMENT RECEIVED - THANK YOU").values('Date', 'Description', 'Category', 'Amount')
    df2 = pd.DataFrame(table2_data)
    if not df2.empty:
        df2['Date'] = pd.to_datetime(df2['Date'], format='%d/%m/%Y')
        df2['MonthYear'] = df2['Date'].dt.to_period('M')
        # df2['Category'] = 'Uncategorized'  # Default category for Table2 entries
        df2['Amount'] = df2['Amount']*-1

    # Combine the dataframes
    combined_df = pd.concat([df1, df2])
    grouped_data = combined_df.groupby(['MonthYear', 'Category']).agg({'Amount' : 'sum'}).reset_index()

    # Sort by MonthYear to ensure chronological order
    grouped_data = grouped_data.sort_values(by='MonthYear')

    # Populate CombinedTable with aggregated data
    for _, row in grouped_data.iterrows():
        CombinedTable.objects.create(
            Date=row['MonthYear'].strftime('%B %Y'),  # Store month and year as the Date field
            Category=row['Category'],
            Amount=row['Amount']
        )
