from django.views.generic.base import TemplateView
from django.shortcuts import render
from django.db.models import Max, Min, Count, Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from core.models import DataPoint
from core.serializers import DataPointSerializer
from django.core.paginator import Paginator, EmptyPage
from django.core.exceptions import FieldError
import json
import logging

logger = logging.getLogger(__name__)
# Create your views here.


class MainView(TemplateView):

    template_name = "vue_app.html"


class ViewConfig(APIView):
    def retrieve_min_max(self, field):
        minimum = DataPoint.objects.all().aggregate(
            Min(f"{field}"))[f"{field}__min"]
        if minimum is None:
            minimum = 0
        maximum = DataPoint.objects.all().aggregate(
            Max(f"{field}"))[f"{field}__max"]
        if maximum is None:
            maximum = 0
        return (minimum, maximum)

    def get(self, request):

        # attendance lows and highs
        estimate_low_min, estimate_low_max = self.retrieve_min_max(
            "estimate_low")
        estimate_best_min, estimate_best_max = self.retrieve_min_max(
            "estimate_best")
        estimate_high_min, estimate_high_max = self.retrieve_min_max(
            "estimate_high")

        # adjusted lows and highs
        adjusted_low_min, adjusted_low_max = self.retrieve_min_max(
            "adjusted_low")
        adjusted_high_min, adjusted_high_max = self.retrieve_min_max(
            "adjusted_high")

        # arrests, injuries, property damage
        reported_arrests_min, reported_arrests_max = self.retrieve_min_max(
            "reported_arrests")
        reported_participant_injuries_min, reported_participant_injuries_max = self.retrieve_min_max(
            "reported_participant_injuries")
        reported_police_injuries_min, reported_police_injuries_max = self.retrieve_min_max(
            "reported_police_injuries")
        reported_property_damage_min, reported_property_damage_max = self.retrieve_min_max(
            "reported_property_damage")

        data = {
            "headers": [
                {
                    "value": "city",
                    "text": "City"
                },
                {
                    "value": "location",
                    "text": "Location"
                },
                {
                    "value": "county",
                    "text": "County"
                },
                {
                    "value": "state",
                    "text": "State"
                },
                {
                    "value": "date",
                    "text": "Date"
                },
                {
                    "value": "estimate_low",
                    "text": "Estimate Low"
                },
                {
                    "value": "estimate_best",
                    "text": "Estimate Best"
                },
                {
                    "value": "estimate_high",
                    "text": "Estimate High"
                },
                {
                    "value": "adjusted_low",
                    "text": "Adjusted Low"
                },
                {
                    "value": "adjusted_high",
                    "text": "Adjusted High"
                },
                {
                    "value": "actor",
                    "text": "Actor"
                },
                {
                    "value": "claim",
                    "text": "Claim"
                },
                {
                    "value": "event_type",
                    "text": "Event Type"
                },
                {
                    "value": "reported_arrests",
                    "text": "Reported Arrests"
                },
                {
                    "value": "reported_participant_injuries",
                    "text": "Reported Participant Injuries"
                },
                {
                    "value": "reported_police_injuries",
                    "text": "Reported Police Injuries"
                },
                {
                    "value": "reported_property_damage",
                    "text": "Reported Property Damage"
                },
            ],
            "stateOptions": DataPoint.objects.order_by().values_list("state", flat=True).distinct(),
            "eventTypeOptions": DataPoint.objects.order_by().values_list("event_type", flat=True).distinct(),
            "estimate_low_min": estimate_low_min,
            "estimate_low_max": estimate_low_max,
            "estimate_best_min": estimate_best_min,
            "estimate_best_max": estimate_best_max,
            "estimate_high_min": estimate_high_min,
            "estimate_high_max": estimate_high_max,
            "adjusted_low_min": adjusted_low_min,
            "adjusted_low_max": adjusted_low_max,
            "adjusted_high_min": adjusted_high_min,
            "adjusted_high_max": adjusted_high_max,

            "reported_arrests_min": reported_arrests_min,
            "reported_arrests_max": reported_arrests_max,
            "reported_participant_injuries_min": reported_participant_injuries_min,
            "reported_participant_injuries_max": reported_participant_injuries_max,
            "reported_police_injuries_min": reported_police_injuries_min,
            "reported_police_injuries_max": reported_police_injuries_max,
            "reported_property_damage_min": reported_property_damage_min,
            "reported_property_damage_max": reported_property_damage_max,
        }
        return Response(data, status=HTTP_200_OK)


class GraphData(APIView):

    def format_queryparams(self, query_params):
        # this is necessary because DRF sets every query param to be a list, even if its only one value
        # so we need to remove single value lists and replace them with just the value for dictionary unpacking
        filters = {}
        for param in query_params:
            if "[]" in param:
                filters[param[0:-2]] = query_params.getlist(param)
            else:
                filters[param] = query_params[param]
        return filters

    def get(self, request):
        field_x = request.query_params.get("fieldX")
        field_y = request.query_params.get("fieldY", None)
        filters = json.loads(request.query_params.get('filters'))
        del filters["order_by"]
        del filters["page_size"]
        del filters["page"]
        queryset = DataPoint.objects.all()
        if "exclude" in filters:
            exclude_dict = filters["exclude"]
            for key in exclude_dict:
                expression = {}
                expression[key] = exclude_dict[key]
                queryset = queryset.exclude(**expression)
            del filters["exclude"]
        queryset = queryset.filter(
            **self.format_queryparams(filters)
        )

        if field_y is None:
            order_by = "-count"
            if field_x == 'date':
                order_by = 'date'
            data_x = queryset.values(field_x).annotate(
                count=Count('pk', distinct=True)).order_by(order_by)
            # we aren't cross graphing
            # ergo just city (events per city)
            return Response({
                "x": data_x
            }, status=HTTP_200_OK)
        else:
            # we are cross graphing
            # ergo city vs estimate_best

            # if field_y is numerical:
            # .annotate(num=Sum('estimate_low'))
            numerical = [
                "estimate_low",
                "estimate_best",
                "estimate_high",
                "adjusted_low",
                "adjusted_high",
                "reported_arrests",
                "reported_participant_injuries",
                "reported_police_injuries",
                "reported_property_damage",
            ]
            order_by = "-y"
            if field_x == 'date':
                order_by = 'date'
            if field_y in numerical:
                data_y = queryset.values(field_x).annotate(
                    y=Sum(field_y)).order_by(order_by)
            else:
                data_y = queryset.values(field_x).annotate(
                    y=Count(field_y)).order_by(order_by)
            return Response({
                "x": [],
                "y": data_y
            })


class DataPointsApiView(APIView):
    """ This endpoint returns a list of data points that match accepted filters.

    Accepts any valid Django ORM filters.

    Defaults:
    order_by: -date
    page_size: 50
    page: 1

    Returns:

    {
        "page": current page as int, 1-indexed,
        "page_size": current page size as int,
        "num_pages": the number of pages as int,
        "start": the 1-index start of the page,
        "end": the 1-index end of the page,
        "total": the total number of objects that match filters,
        "data": serialized array of data points
    }
    """

    def format_queryparams(self, query_params):
        # this is necessary because DRF sets every query param to be a list, even if its only one value
        # so we need to remove single value lists and replace them with just the value for dictionary unpacking
        filters = {}
        for param in query_params:
            if "[]" in param:
                filters[param[0:-2]] = query_params.getlist(param)
            else:
                filters[param] = query_params[param]
        return filters

    def get(self, request):
        try:
            query_params = request.query_params.copy()
            if "order_by" in query_params:
                # we need to order the objects to have deterministic pagination, but we don't
                # want to dictionary unpack order_by into the filter
                order_by = query_params["order_by"]
                del query_params["order_by"]
            else:
                order_by = "-date"

            if "page_size" in query_params:
                # we need the page size, but we don't want to dictionary unpack into the filter
                page_size = query_params["page_size"]
                del query_params["page_size"]
            else:
                page_size = 50

            if "page" in query_params:
                # we need the page, but we don't want to dictionary unpack into the filter
                page = query_params["page"]
                del query_params["page"]
            else:
                page = 1
            queryset = DataPoint.objects.all()
            if "exclude" in query_params:
                exclude_dict = json.loads(query_params["exclude"])
                for key in exclude_dict:
                    expression = {}
                    expression[key] = exclude_dict[key]
                    queryset = queryset.exclude(**expression)
                del query_params["exclude"]
            # filter, order by, and paginate.
            queryset = queryset.filter(
                **self.format_queryparams(query_params)).order_by(order_by)
            paginator = Paginator(queryset, page_size)

            # this can throw an error, caught on except EmptyPage
            paginated_queryset = paginator.page(page)

            # serialize to JSON and return
            serializer = DataPointSerializer(
                paginated_queryset.object_list, many=True)
            response_data = {
                "page": page,
                "page_size": page_size,
                "num_pages": paginator.num_pages,
                "total": paginator.count,
                "data": serializer.data,
                "start": paginated_queryset.start_index(),
                "end": paginated_queryset.end_index()
            }
            return Response(response_data, status=HTTP_200_OK)
        except EmptyPage:
            # it's possible the user requested an invalid page
            return Response({"data": "Page has no data."}, status=HTTP_400_BAD_REQUEST)
        except FieldError as e:
            # some query param did not fit with the model schema
            return Response({"data": str(e)}, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(str(e))
            return Response({"data": "Server error"}, status=HTTP_500_INTERNAL_SERVER_ERROR)
