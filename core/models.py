from django.db import models
import json

# Create your models here.


class DataPoint(models.Model):
    city = models.TextField("City or Town", blank=True, null=True)
    location = models.TextField("Location", blank=True, null=True)
    county = models.TextField("County", blank=True, null=True)
    state = models.TextField("State or Territory", blank=True, null=True)
    date = models.DateField(
        "Date", blank=True, null=True)
    estimate_low = models.IntegerField(
        "Attendance Low Estimate", blank=True, null=True)
    estimate_best = models.IntegerField(
        "Attendance Best Estimate", blank=True, null=True)
    estimate_high = models.IntegerField(
        "Attendance High Estimate", blank=True, null=True)
    adjusted_low = models.IntegerField(
        "Adjusted Attendance Low", blank=True, null=True)
    adjusted_high = models.IntegerField(
        "Adjusted Attendance High", blank=True, null=True)
    actor = models.TextField("Actor", blank=True, null=True)
    claim = models.TextField("Claim", blank=True, null=True)
    event_type = models.TextField("Event Type", blank=True, null=True)
    reported_arrests = models.IntegerField(
        "Reported Arrests", blank=True, null=True)
    reported_participant_injuries = models.IntegerField(
        "Reported Participant Injuries", blank=True, null=True)
    reported_police_injuries = models.IntegerField(
        "Reported Police Injuries", blank=True, null=True)
    reported_property_damage = models.IntegerField(
        "Reported Property Damage", blank=True, null=True)

    # I didn't use JsonField here because if the user's local Sqlite was not compiled with ENABLE_JSON1 it will
    # throw a shitfit here. We lose filtering by sources, but c'est la vie. I wasn't planning on supporting that anyway
    sources = models.TextField(
        "Array of Sources in JSON Format", blank=True, null=True)

    def save_sources(self, sources: list):
        """Saves sources to the sources field.
        """
        self.sources = json.dumps(sources)
        self.save()

    def load_sources(self) -> list:
        """Returns sources as list from TextField"""
        return json.loads(self.sources)
