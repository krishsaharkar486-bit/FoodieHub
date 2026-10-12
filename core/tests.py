from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import Address
from menu.models import Category, FoodItem
from restaurants.models import Restaurant
from orders.models import Order, OrderItem
from orders.services import change_status
from django.core.exceptions import ValidationError

User=get_user_model()

class FoodieHubFlowTests(TestCase):
    def setUp(self):
        self.manager=User.objects.create_user(username='manager',email='mgr@test.example',password='Testpass123!',role=User.Role.RESTAURANT_MANAGER)
        self.customer=User.objects.create_user(username='customer',email='cust@test.example',password='Testpass123!')
        self.restaurant=Restaurant.objects.create(manager=self.manager,name='Tasty House',address='1 Main Road',delivery_fee=Decimal('25.00'))
        self.category=Category.objects.create(restaurant=self.restaurant,name='Bowls',slug='bowls')
        self.food=FoodItem.objects.create(restaurant=self.restaurant,category=self.category,name='Paneer Bowl',description='Fresh bowl',price=Decimal('200.00'))
        Address.objects.create(user=self.customer,label='Home',recipient_name='Sam',phone='1234567890',line1='5 Lane',city='Pune',postal_code='411001',is_default=True)

    def test_home_and_menu_search(self):
        self.assertEqual(self.client.get('/').status_code,200)
        response=self.client.get('/menu/',{'q':'Paneer','category':self.category.pk,'min_price':'100','max_price':'250'})
        self.assertContains(response,'Paneer Bowl')
        self.assertNotContains(self.client.get('/menu/',{'q':'impossible'}),'Paneer Bowl')

    def test_registration_creates_customer(self):
        response=self.client.post('/accounts/register/',{'username':'newbie','first_name':'New','last_name':'User','email':'new@test.example','password1':'GreatPass123!','password2':'GreatPass123!'})
        self.assertEqual(response.status_code,302)
        self.assertTrue(User.objects.filter(username='newbie',role=User.Role.CUSTOMER).exists())

    def test_cart_uses_server_price_and_blocks_other_restaurant(self):
        response=self.client.post(f'/cart/add/{self.food.pk}/',{'next':'/cart/'})
        self.assertEqual(response.status_code,302)
        self.assertContains(self.client.get('/cart/'),'₹200.00')
        other=Restaurant.objects.create(manager=self.manager,name='Other House',address='2 Main Road')
        item=FoodItem.objects.create(restaurant=other,name='Rice',price=Decimal('50.00'))
        self.client.post(f'/cart/add/{item.pk}/')
        self.assertEqual(self.client.session['foodiehub_cart'],{str(self.food.pk):1})

    def test_unavailable_food_cannot_be_added(self):
        self.food.is_available=False;self.food.save()
        self.assertEqual(self.client.post(f'/cart/add/{self.food.pk}/').status_code,404)

    def test_checkout_snapshots_price_and_ownership(self):
        self.client.force_login(self.customer);self.client.post(f'/cart/add/{self.food.pk}/')
        get=self.client.get('/orders/checkout/');nonce=get.context['nonce'];self.assertFalse(get.context['online_enabled'])
        response=self.client.post('/orders/checkout/',{'nonce':nonce,'address':self.customer.addresses.first().pk,'payment_method':'cod'})
        self.assertEqual(response.status_code,302)
        order=Order.objects.get(customer=self.customer)
        self.assertEqual(order.total,Decimal('225.00'))
        item=order.items.get();self.assertEqual(item.unit_price,Decimal('200.00'))
        self.food.price=Decimal('999.00');self.food.save();item.refresh_from_db()
        self.assertEqual(item.unit_price,Decimal('200.00'))
        stranger=User.objects.create_user(username='stranger',email='stranger@test.example',password='Testpass123!')
        self.client.force_login(stranger)
        self.assertEqual(self.client.get(f'/orders/{order.number}/').status_code,404)

    def test_checkout_duplicate_nonce_does_not_duplicate_order(self):
        self.client.force_login(self.customer);self.client.post(f'/cart/add/{self.food.pk}/')
        get=self.client.get('/orders/checkout/');payload={'nonce':get.context['nonce'],'address':self.customer.addresses.first().pk,'payment_method':'cod'}
        self.client.post('/orders/checkout/',payload);self.client.post('/orders/checkout/',payload)
        self.assertEqual(Order.objects.filter(customer=self.customer).count(),1)

    def test_manager_is_scoped_to_assigned_restaurant(self):
        self.client.force_login(self.manager)
        self.assertEqual(self.client.get('/manager/').status_code,200)
        other=User.objects.create_user(username='other-manager',email='other@test.example',password='Testpass123!',role=User.Role.RESTAURANT_MANAGER)
        self.client.force_login(other)
        self.assertEqual(self.client.get('/manager/').status_code,404)

    def test_status_transitions_are_validated(self):
        order=Order.objects.create(customer=self.customer,restaurant=self.restaurant,number='FHTEST001',customer_name='Sam',contact_phone='1234567890',address_text='Pune',subtotal=200,delivery_fee=25,total=225)
        with self.assertRaises(ValidationError): change_status(order,Order.Status.DELIVERED)
        change_status(order,Order.Status.CONFIRMED);order.refresh_from_db();self.assertEqual(order.status,Order.Status.CONFIRMED)

    def test_manager_cannot_open_another_managers_order(self):
        other_manager=User.objects.create_user(username='other-manager-2',email='other2@test.example',password='Testpass123!',role=User.Role.RESTAURANT_MANAGER)
        other_restaurant=Restaurant.objects.create(manager=other_manager,name='Private Kitchen',address='2 Main Road')
        other_order=Order.objects.create(customer=self.customer,restaurant=other_restaurant,number='FHOTHER01',customer_name='Sam',contact_phone='1234567890',address_text='Pune',subtotal=1,delivery_fee=0,total=1)
        self.client.force_login(self.manager)
        self.assertEqual(self.client.get(f'/manager/orders/{other_order.number}/').status_code,404)
