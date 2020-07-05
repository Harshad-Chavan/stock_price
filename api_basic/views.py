from django.shortcuts import render,HttpResponse
from rest_framework.response import Response
from rest_framework import viewsets
from .serializers import PriceSerializer,SecSerializer
from .scrapper3 import compute_price,get_securities
# Create your views here.
class TaskViewSet(viewsets.ViewSet):
    # Required for the Browsable API renderer to have a nice form.
    serializer_class = PriceSerializer

    def list(self, request):
        print(request.query_params)
        names = get_securities(request.query_params["flag"])
        name = list(names.keys())[0]
        scripcode = names[name]
        print(name,scripcode)
        security = compute_price(name,scripcode)
        serializer = PriceSerializer(
            instance=security.values(), many=True)
        return Response(serializer.data)

class SecListViewSet(viewsets.ViewSet):
    # Required for the Browsable API renderer to have a nice form.
    serializer_class = SecSerializer

    def list(self, request):
        print(request.query_params)
        temp = {}
        names = get_securities(request.query_params["flag"])
        print(names)
        for key,value in names.items():
            temp[key] = {"symbol_name": key,"scripcode": value }
        # names = get_securities(request.query_params["flag"])
        serializer = SecSerializer(
            instance=temp.values(), many=True)
        return Response(serializer.data)