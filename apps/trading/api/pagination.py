from rest_framework.pagination import PageNumberPagination


class CurrencyPagination(PageNumberPagination):
    page_size = 4
