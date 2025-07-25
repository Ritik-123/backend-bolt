from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class PaginatedAPIView(APIView):
    page_size = 10

    def paginate_queryset(self, queryset, request):
        paginator = PageNumberPagination()
        paginator.page_size = self.page_size
        page = paginator.paginate_queryset(queryset, request)
        return paginator, page

    def paginated_response(self, paginator, data):
        return paginator.get_paginated_response(data)
