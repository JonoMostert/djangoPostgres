# postgresDB/categoryCreation.py

from .models import Table2

# Define category mapping
CATEGORY_MAPPING = {
    "Sainsbury's": 'Groceries',
    'Tesco': 'Groceries',
    'Deliveroo': 'Eating out',
    'Bar': 'Eating out',
    'Netflix': 'Entertainment',
    'Amazon': 'Shopping',
    'TFL': 'Transport',
    'Human Forest': 'Transport',
    'Lime': 'Transport',
    # Add more mappings as needed
}

def assign_categories():
    # Retrieve all rows in Table2 without a Category
    table2_rows = Table2.objects.filter(Category='')

    for row in table2_rows:
        # Check each keyword in CATEGORY_MAPPING to see if it matches the Description
        for keyword, category in CATEGORY_MAPPING.items():
            if keyword.lower() in row.Description.lower():
                row.Category = category
                row.save()
                break
