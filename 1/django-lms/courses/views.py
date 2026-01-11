from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.conf import settings
import json
import csv
import io
from .models import Course, UserProfile, Enrollment, SavedSearch


def index(request):
    courses = Course.objects.filter(is_hidden=False)[:10]
    return render(request, 'courses/index.html', {'courses': courses})


def search(request):
    def _safe_json_load(value):
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return {}

    def _load_payload():
        if request.method != 'POST':
            return {}
        if request.content_type and 'application/json' in request.content_type:
            return _safe_json_load(request.body.decode('utf-8'))
        raw_payload = request.POST.get('payload', '')
        return _safe_json_load(raw_payload)

    def _extract_filters(payload):
        filters = {}

        simple = payload.get('simple', {})
        if isinstance(simple, dict):
            for key, value in simple.items():
                if value not in (None, ''):
                    filters[key] = value

        clauses = payload.get('clauses', [])
        if isinstance(clauses, list):
            for clause in clauses:
                if not isinstance(clause, dict):
                    continue
                key = clause.get('key')
                if key:
                    filters[key] = clause.get('value')

        advanced = payload.get('advanced', {})
        if isinstance(advanced, dict):
            filters.update(advanced)

        return filters

    def _coerce_isnull(filters):
        for key, value in list(filters.items()):
            if not isinstance(key, str) or not key.endswith('__isnull'):
                continue
            if isinstance(value, str):
                lowered = value.strip().lower()
                if lowered in ('1', 'true', 'yes', 'on'):
                    filters[key] = True
                elif lowered in ('0', 'false', 'no', 'off'):
                    filters[key] = False
        return filters

    payload = {}
    filters = request.GET.dict()
    export_requested = (
        request.GET.get('export') == 'csv'
        or request.POST.get('export') == 'csv'
    )
    saved_searches = []
    active_saved = None
    save_message = None

    payload = _load_payload()

    if request.user.is_authenticated:
        saved_searches = SavedSearch.objects.filter(user=request.user).order_by('-created_at')[:5]
        saved_id = request.POST.get('saved_id')
        if saved_id:
            try:
                active_saved = SavedSearch.objects.get(id=saved_id, user=request.user)
                saved_payload = _safe_json_load(active_saved.payload)
                filters.update(_extract_filters(saved_payload))
            except (SavedSearch.DoesNotExist, ValueError):
                active_saved = None

    filters.update(_extract_filters(payload))

    system_filters = {}
    if not request.user.is_staff:
        system_filters['is_hidden'] = False
    filters.update(system_filters)
    _coerce_isnull(filters)
    connector = filters.pop('connector', None)
    negated = filters.pop('negated', None)
    filters.pop('export', None)

    if request.method == 'POST' and request.user.is_authenticated:
        save_name = request.POST.get('save_name', '').strip()
        if save_name and payload:
            SavedSearch.objects.create(
                user=request.user,
                name=save_name,
                payload=json.dumps(payload)
            )
            save_message = 'Search saved'

    if connector is not None or negated is not None:
        q_object = Q(**filters)
        if connector:
            q_object.connector = str(connector).upper()
        if negated is not None:
            q_object.negated = str(negated).lower() in ('1', 'true', 'yes', 'on')
        courses = Course.objects.filter(q_object)
    else:
        courses = Course.objects.filter(**filters)

    if export_requested:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Title', 'Category', 'Level', 'Owner', 'API Key'])
        for course in courses:
            owner = course.userprofile.user.username if course.userprofile else ''
            api_key = course.userprofile.api_key if course.userprofile else ''
            writer.writerow([course.title, course.category, course.level, owner, api_key])

        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="course_report.csv"'
        return response

    return render(request, 'courses/search.html', {
        'courses': courses,
        'filters': filters,
        'payload': json.dumps(payload, ensure_ascii=True, indent=2) if payload else '',
        'saved_searches': saved_searches,
        'active_saved': active_saved,
        'save_message': save_message,
    })


def course_detail(request, course_id):
    try:
        course = Course.objects.get(id=course_id)
        return render(request, 'courses/detail.html', {'course': course})
    except Course.DoesNotExist:
        return HttpResponse("Course not found", status=404)


@login_required
def profile(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        enrollments = Enrollment.objects.filter(user=request.user)
        return render(request, 'courses/profile.html', {
            'profile': profile,
            'enrollments': enrollments
        })
    except UserProfile.DoesNotExist:
        return render(request, 'courses/profile.html', {
            'profile': None,
            'enrollments': []
        })


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/portal/')
        else:
            return render(request, 'courses/login.html', {
                'error': 'Invalid credentials'
            })
    return render(request, 'courses/login.html')


def logout_view(request):
    logout(request)
    return redirect('/portal/')
