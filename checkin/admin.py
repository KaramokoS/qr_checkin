import csv
from django.contrib import admin
from .models import CheckInSession, Attendee
from django import forms



class SessionAdminForm(forms.ModelForm):
    csv_file = forms.FileField(required=False, help_text="Uploader un CSV pour créer des participants")

    class Meta:
        model = CheckInSession
        fields = ['name', 'created_by', 'password', 'is_closed', 'csv_file']

@admin.register(CheckInSession)
class CheckInSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)
    form = SessionAdminForm

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # If CSV provided → import attendees
        csv_file = form.cleaned_data.get("csv_file")
        if csv_file:
            decoded = csv_file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded)

            for row in reader:
                Attendee.objects.update_or_create(
                    session=obj,
                    qr_code=row.get("qr_code", ""),
                    defaults={
                        "uid": row.get("uid", ""),
                        "nom": row.get("nom", ""),
                        "prenom": row.get("prenom", ""),
                        "tel": row.get("tel", ""),
                        "prix": row.get("prix", ""),
                        "checked_in": False,
                        "checkin_date": None
                    }
                )

@admin.register(Attendee)
class AttendeeAdmin(admin.ModelAdmin):
    list_display = ("uid", "qr_code", "checked_in", "checkin_date", "session")
    list_filter = ("session", "checked_in")
    search_fields = ("uid", "qr_code")
