from django.db import models
from django.conf import settings



class CheckInSession(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    password = models.CharField(max_length=100, blank=True, null=True)  # optionnel
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({'closed' if self.is_closed else 'open'})"
    

# class Attendee(models.Model):
#     session = models.ForeignKey(CheckInSession, on_delete=models.CASCADE, null=True, blank=True)
#     uid = models.CharField(max_length=200)
#     qr_code = models.CharField(max_length=200)
#     checked_in = models.BooleanField(default=False)
#     checkin_date = models.DateTimeField(null=True, blank=True)

#     class Meta:
#         unique_together = ('session', 'qr_code')

#     def __str__(self):
#         return f"{self.uid} @ {self.session}"

class Attendee(models.Model):
    session = models.ForeignKey(CheckInSession, on_delete=models.CASCADE, null=True, blank=True)

    uid = models.CharField(max_length=200)
    qr_code = models.CharField(max_length=200)

    # Nouveaux champs optionnels
    nom = models.CharField(max_length=200, null=True, blank=True)
    prenom = models.CharField(max_length=200, null=True, blank=True)
    tel = models.CharField(max_length=50, null=True, blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    checked_in = models.BooleanField(default=False)
    checkin_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('session', 'qr_code')

    def __str__(self):
        return f"{self.uid} @ {self.session}"
