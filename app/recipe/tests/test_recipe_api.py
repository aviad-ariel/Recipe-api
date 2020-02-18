from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer


RECIPE_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **kwargs):
    """Create recipe for testing"""
    defaults = {
        'title': 'Sample Recipe',
        'duration': 10,
        'price': 5.55
    }
    # update/create default values from kwargs, exists value will be override
    defaults.update(kwargs)
    return Recipe.objects.create(user=user, **defaults)


class PricateRecipeAPITest(TestCase):
    """Test private api endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        """Test retriving recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_limited_for_user(self):
        other_user = get_user_model().objects.create_user('t@t.com', 'pass')
        sample_recipe(user=other_user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user).order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
