from django.contrib import admin
from .models import CheckInSession, Attendee

@admin.register(CheckInSession)
class CheckInSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)

@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = ("uid", "qr_code", "checked_in", "checkin_date", "session")
    list_filter = ("session", "checked_in")
    search_fields = ("uid", "qr_code")
