from django.test import TestCase, Client

# Create your tests here.

from .models import Table2, CombinedTable
from django.urls import reverse
import json

class AppFunctionalityTests(TestCase):
    def setUp(self):
        """
        Set up test data for the database.
        """
        # Create test entries in Table2
        Table2.objects.create(
            Description="Sainsbury's groceries",
            Amount=50.0,
            Date="2024-10-01",
            Category=""
        )
        Table2.objects.create(
            Description="Netflix subscription",
            Amount=15.0,
            Date="2024-10-05",
            Category=""
        )
        
        # Create test entries in CombinedTable
        CombinedTable.objects.create(
            Date="2024-10-01",
            Category="Groceries",
            Amount=50.0
        )
        CombinedTable.objects.create(
            Date="2024-10-05",
            Category="Entertainment",
            Amount=15.0
        )

    def test_category_assignment(self):
        """
        Test if the category assignment script assigns correct categories.
        """
        from .categoryCreation import assign_categories

        # Run the category assignment script
        assign_categories()

        # Verify the assigned categories
        self.assertEqual(Table2.objects.get(Description__icontains="Sainsbury").Category, "Groceries")
        self.assertEqual(Table2.objects.get(Description__icontains="Netflix").Category, "Entertainment")

    def test_summary_view(self):
        """
        Test if the summary view returns the correct data.
        """
        client = Client()
        response = client.get(reverse('summary'))  # Adjust 'summary' to your URL name if different
        self.assertEqual(response.status_code, 200)

        # Check if the data passed to the template matches expected results
        context = response.context
        self.assertIn('masterTable_data', context)
        self.assertIn('months', context)
        self.assertIn('datasets', context)

        # Verify chart data integrity
        datasets = json.loads(context['datasets'])
        labels = [dataset['label'] for dataset in datasets]
        self.assertIn("Groceries", labels)
        self.assertIn("Entertainment", labels)

    def test_combined_table_entry(self):
        """
        Test if the CombinedTable model handles data correctly.
        """
        # Verify the data in CombinedTable
        entry = CombinedTable.objects.get(Category="Groceries")
        self.assertEqual(entry.Amount, 50.0)
        self.assertEqual(entry.Date, "2024-10-01")
        
        entry = CombinedTable.objects.get(Category="Entertainment")
        self.assertEqual(entry.Amount, 15.0)
        self.assertEqual(entry.Date, "2024-10-05")