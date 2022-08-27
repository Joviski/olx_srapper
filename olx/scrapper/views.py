from datetime import date
import email
import imp
from django.shortcuts import render
import datetime
from pytz import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Ad
from .serializers import ScrapSerializer,AdsSerializer
from .tasks import ads_mining


# Create your views here.

class ScrapView(APIView):
    def post(self, request, format = None):
        serializer = ScrapSerializer(data=request.data)
        if serializer.is_valid():
            key= serializer.data['keyw'] #search keyword
            email= serializer.data['email'] #email address
            sample_size= serializer.data['size'] #sample size to send to email address
            
            #Check if this search is done today
            ad= Ad.objects.filter(keyw=key).last()
            if ad:
                if ad.date.today() ==  datetime.date.today():
                    today = datetime.datetime.today()
                    start_date = datetime.datetime(year=today.year, month=today.month, day=today.day, hour=0, minute=0, second=0) # represents 00:00:00
                    end_date = datetime.datetime(year=today.year, month=today.month, day=today.day, hour=23, minute=59, second=59) # represents 23:59:59
                    ads= list(Ad.objects.filter(keyw=key, date__range=(start_date, end_date)).values()) #Retrieve the searches done today with the passed keyword
                    return Response({'results': ads },status=status.HTTP_200_OK)
                
            
            ads_mining.s(key,sample_size,email).delay() #Perform async task "Using Celery" of scrapping (Using Selenium) & sending mail "Using Django Email"
            return Response({"message": "Ads are being collected now. You will receive a mail shortly with samples."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

                

            
            
            


    
