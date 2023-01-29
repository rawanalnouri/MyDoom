from django.test import TestCase

class IndexViewTest(TestCase):
    def testIndexView(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')