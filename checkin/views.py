import csv
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import CheckInSession, Attendee

def session_list(request):
    sessions = CheckInSession.objects.order_by('-created_at')
    return render(request, 'session_list.html', {'sessions': sessions})


def create_session(request):
    # page pour créer une session et uploader un CSV (ou via ajax endpoint)
    if request.method == "POST":
        name = request.POST.get('name') or "Nouvelle session"
        password = request.POST.get('password') or None

        session = CheckInSession.objects.create(
            name=name,
            password=password
        )

        # si upload direct via form submit (non ajax)
        uploaded = request.FILES.get('csv_file')
        if uploaded:
            _create_attendees_from_file(uploaded, session)
            messages.success(request, "Session créée et CSV importé.")
            return redirect("scan_qr", session_id=session.id)

        messages.success(request, "Session créée. Téléverse un CSV pour ajouter des participants.")
        return redirect("scan_qr", session_id=session.id)

    return render(request, 'create_session.html')



def _create_attendees_from_file(file_obj, session):
    """
    Lit un fichier CSV et crée / met à jour les Attendees de la session.
    Colonnes attendues :
    uid, qr_code, nom, prenom, tel, prix
    Toutes sont optionnelles sauf qr_code.
    """

    decoded = file_obj.read().decode('utf-8').splitlines()
    reader = csv.DictReader(decoded)

    created = 0

    for row in reader:
        qr_code = (row.get('qr_code') or row.get('qr') or '').strip()
        if not qr_code:
            continue  # ligne invalide → on ignore

        uid = (row.get('uid') or row.get('id') or '').strip()
        nom = (row.get('nom') or '').strip()
        prenom = (row.get('prenom') or '').strip()
        tel = (row.get('tel') or row.get('telephone') or '').strip()

        # prix peut être vide ou invalide
        raw_prix = row.get('prix')
        try:
            prix = Decimal(raw_prix) if raw_prix not in (None, "", " ") else None
        except:
            prix = None

        Attendee.objects.update_or_create(
            session=session,
            qr_code=qr_code,
            defaults={
                'uid': uid,
                'nom': nom,
                'prenom': prenom,
                'tel': tel,
                'prix': prix,
                'checked_in': False,
                'checkin_date': None,
            }
        )
        created += 1

    return created


@require_POST
def upload_csv_ajax(request):
    # Ajax endpoint (progress handled on client for upload)
    file = request.FILES.get('csv_file')
    session_id = request.POST.get('session_id')
    session = get_object_or_404(CheckInSession, id=session_id)

    if session.is_closed:
        return JsonResponse({"error": "Session fermée"}, status=400)

    if not file.name.endswith('.csv'):
        return JsonResponse({"error": "Fichier non CSV"}, status=400)

    created = _create_attendees_from_file(file, session)
    return JsonResponse({"ok": True, "created": created})


def scan_qr(request, session_id):
    session = get_object_or_404(CheckInSession, id=session_id)
    # si mot de passe défini, vérifier paramètre ? token? ici simple: formulaire
    if session.password:
        # if user submitted password, keep in session (browser session) for convenience
        if request.method == "POST":
            input_pw = request.POST.get('session_password')
            if input_pw != session.password:
                messages.error(request, "Mot de passe invalide.")
                return redirect('session_list')
            request.session[f'session_access_{session_id}'] = True
        else:
            # if not yet validated, show password form
            if not request.session.get(f'session_access_{session_id}', False):
                return render(request, 'session_password.html', {'session': session})

    return render(request, 'scan.html', {'session': session})


def checkin_result(request, session_id):
    if request.method != "POST":
        return redirect('scan_qr', session_id=session_id)

    session = get_object_or_404(CheckInSession, id=session_id)
    if session.is_closed:
        return render(request, 'result.html', {'success': False, 'message': 'Session fermée.'})

    qr_code = request.POST.get('qr_code')
    try:
        attendee = Attendee.objects.get(session=session, qr_code=qr_code)
    except Attendee.DoesNotExist:
        context = {'success': False, 'message': 'QR Code inconnu.', 'session': session}
        return render(request, 'result.html', context)

    if attendee.checked_in:
        context = {
            'success': False,
            'message': 'QR Code déjà validé.',
            'checkin_date': attendee.checkin_date,
            'attendee': attendee,
            'session': session
        }
        return render(request, 'result.html', context)

    # première validation :
    attendee.checked_in = True
    attendee.checkin_date = timezone.localtime(timezone.now())
    attendee.save()

    # broadcast via channels layer
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"session_{session_id}",
            {
                "type": "attendee.checked_in",
                "attendee_id": attendee.id,
                "uid": attendee.uid,
                "qr_code": attendee.qr_code,
                "checkin_date": attendee.checkin_date.isoformat()
            }
        )
    except Exception:
        pass  # ignore broadcasting errors in dev

    context = {'success': True, 'message': 'Check-in réussi !', 'attendee': attendee, 'session': session}
    return render(request, 'result.html', context)


def session_admin(request, session_id):
    session = get_object_or_404(CheckInSession, id=session_id)
    attendees = session.attendees.order_by('-checked_in', 'uid')
    return render(request, 'session_admin.html', {'session': session, 'attendees': attendees})

def export_session_csv(request, session_id):
    session = get_object_or_404(CheckInSession, id=session_id)
    attendees = session.attendees.all()

    # Prepare CSV response
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    filename = f"session_{session.id}_export.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)

    # CSV Header (updated for extra fields)
    writer.writerow([
        'uid', 'qr_code', 'nom', 'prenom', 'tel', 'prix',
        'checked_in', 'checkin_date'
    ])

    # Write rows
    for a in attendees:
        writer.writerow([
            a.uid or '',
            a.qr_code or '',
            a.nom or '',
            a.prenom or '',
            a.tel or '',
            str(a.prix) if a.prix is not None else '',
            "1" if a.checked_in else "0",
            a.checkin_date.isoformat() if a.checkin_date else ''
        ])

    return response

@require_POST
def close_session(request, session_id):
    session = get_object_or_404(CheckInSession, id=session_id)
    session.is_closed = True
    session.save()
    # broadcast close event
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        async_to_sync(get_channel_layer().group_send)(
            f"session_{session_id}",
            {"type": "session.closed", "message": "Session closed"}
        )
    except Exception:
        pass
    return redirect('session_admin', session_id=session.id)

def live_table(request, session_id):
    session = get_object_or_404(CheckInSession, id=session_id)
    return render(request, "live_table.html", {"session": session})

def live_table_data(request, session_id):
    attendees = Attendee.objects.filter(session_id=session_id).order_by("-checkin_date")

    data = [
        {
            "uid": a.uid,
            "qr_code": a.qr_code,
            "checked_in": a.checked_in,
            "checkin_date": a.checkin_date.strftime("%Y-%m-%d %H:%M:%S") if a.checkin_date else "",
            "nom": a.nom or "",
            "prenom": a.prenom or "",
            "tel": a.tel or "",
            "prix": str(a.prix) if a.prix is not None else "",
        }
        for a in attendees
    ]

    return JsonResponse({"attendees": data})
