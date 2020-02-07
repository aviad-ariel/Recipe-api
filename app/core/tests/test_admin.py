 from django.test import TestCase, Client
 from django.contrib.auth import get_user_model
 from django.urls import reverse

 
 class AdminSiteTests(TestCase):

     def setup(self):
         self.client = Client()
         self.admin_user = get_user_model().objects.create_superuser(
             email='test@admin.com',
             password='admin123'
         )
         self.client.force_login(self.admin_user)
         self.user = get_user_model().objects.create_user(
             email='test@user.com',
             password='user123',
             name='Regular User'
         )

         def test_user_listet(self):
             """Test to check listed user on user page"""
             url = reverse('admin:core_user_changelist')
             res = self.client.get(url)

             assertContains(res, self.user.name)
             assertContains(res, self.user.email)
