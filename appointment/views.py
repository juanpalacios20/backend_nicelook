from django.shortcuts import render
from rest_framework import viewsets,status
from .models import Appointment
from .serializers import appointmentSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import date

# Create your views here.
class appointmentViewSet(viewsets.ModelViewSet):
    serializer_class = appointmentSerializer
    queryset = Appointment.objects.all()
     
@api_view(['POST'])
def appointment_list(request):
    try:
        day = request.data.get('day')
        month = request.data.get('month')
        year = request.data.get('year')
        print(day, month, year)
        appointments_date = date(year, month, day) 
        appointments = Appointment.objects.filter(date = appointments_date)
        if not appointments.exists():
            return Response({'error': "Appointments doesn't exist" },status=status.HTTP_404_NOT_FOUND)
        serializer = appointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)