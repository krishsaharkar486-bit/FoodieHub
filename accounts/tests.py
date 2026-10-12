from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import Address

class AccountSecurityTests(TestCase):
    def test_profile_and_address_require_login(self):
        self.assertEqual(self.client.get('/accounts/profile/').status_code,302)
        self.assertEqual(self.client.get('/accounts/addresses/').status_code,302)
    def test_address_delete_is_user_scoped_and_post_only(self):
        User=get_user_model()
        a=User.objects.create_user(username='a',email='a@test.example',password='Testpass123!')
        b=User.objects.create_user(username='b',email='b@test.example',password='Testpass123!')
        address=Address.objects.create(user=a,recipient_name='A',phone='1234567890',line1='One',city='Pune',postal_code='1')
        self.client.force_login(b)
        self.assertEqual(self.client.get(f'/accounts/addresses/{address.pk}/delete/').status_code,405)
        self.assertEqual(self.client.post(f'/accounts/addresses/{address.pk}/delete/').status_code,404)
        self.assertTrue(Address.objects.filter(pk=address.pk).exists())
