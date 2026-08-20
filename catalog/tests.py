# 自动测试

from django.test import TestCase


class ProjectSkeletonTest(TestCase):
    def test_home_page_exists(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

