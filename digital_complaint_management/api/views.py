from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from django.db.models import Count

from accounts.models import CustomUser
from departments.models import Department
from staff.models import StaffProfile
from complaints.models import Category, Complaint
from feedback.models import ComplaintFeedback
from notifications.models import Notification
from complaints.services import register_complaint

from .serializers import (
    UserSerializer, DepartmentSerializer, StaffProfileSerializer,
    CategorySerializer, ComplaintSerializer, ComplaintFeedbackSerializer,
    NotificationSerializer
)

class AuthLoginAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            return Response({
                'success': True,
                'user': UserSerializer(user).data
            })
        return Response({'success': False, 'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ComplaintViewSet(viewsets.ModelViewSet):
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'complaint_id'

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN' or user.is_superuser:
            return Complaint.objects.all().select_related('category', 'department', 'assigned_staff')
        elif user.role == 'STAFF':
            return Complaint.objects.filter(assigned_staff=user).select_related('category', 'department')
        return Complaint.objects.filter(user=user).select_related('category', 'department')

    def perform_create(self, serializer):
        data = serializer.validated_data
        files = self.request.FILES.getlist('attachments')
        complaint = register_complaint(self.request.user, data, files)
        serializer.instance = complaint


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True).prefetch_related('subcategories')
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.filter(is_active=True)
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.AllowAny]


class StaffViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StaffProfile.objects.filter(is_available=True).select_related('user', 'department')
    serializer_class = StaffProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class FeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = ComplaintFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'ADMIN' or self.request.user.is_superuser:
            return ComplaintFeedback.objects.all()
        return ComplaintFeedback.objects.filter(user=self.request.user)


class ReportSummaryAPI(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        total = Complaint.objects.count()
        resolved = Complaint.objects.filter(status__in=['RESOLVED', 'CLOSED']).count()
        pending = total - resolved
        by_status = list(Complaint.objects.values('status').annotate(count=Count('id')))
        by_priority = list(Complaint.objects.values('priority').annotate(count=Count('id')))

        return Response({
            'total_complaints': total,
            'resolved_complaints': resolved,
            'pending_complaints': pending,
            'by_status': by_status,
            'by_priority': by_priority
        })
