from rest_framework import serializers
from core.models import DataPoint


class DataPointSerializer(serializers.ModelSerializer):
    sources = serializers.SerializerMethodField()

    def get_sources(self, obj):
        return obj.load_sources()

    class Meta:
        model = DataPoint
        fields = (
            'id',
            'city',
            'location',
            'county',
            'state',
            'date',
            'estimate_low',
            'estimate_best',
            'estimate_high',
            'adjusted_low',
            'adjusted_high',
            'actor',
            'claim',
            'event_type',
            'reported_arrests',
            'reported_participant_injuries',
            'reported_police_injuries',
            'reported_property_damage',
            'sources',
        )
