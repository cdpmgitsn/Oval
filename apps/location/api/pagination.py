from rest_framework.pagination import PageNumberPagination


class CountryPagination(PageNumberPagination):
    page_size = 4


class CityPagination(PageNumberPagination):
    page_size = 4
