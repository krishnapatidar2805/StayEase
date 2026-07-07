import uuid
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse

from rooms.models import Room
from .models import Booking, Payment
from .forms import BookingForm
from adminpanel.notifications import notify_admins


@login_required
def book_room_view(request, pk):
    room = get_object_or_404(Room, pk=pk)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['check_out']

            if check_out <= check_in:
                messages.error(request, 'Check-out date must be after check-in date.')
            elif check_in < date.today():
                messages.error(request, 'Check-in date cannot be in the past.')
            else:
                booking = form.save(commit=False)
                booking.user = request.user
                booking.room = room
                nights = (check_out - check_in).days
                booking.total_amount = room.price_per_night * nights
                booking.status = 'pending'
                booking.save()

                notify_admins(
                    'booking',
                    f'New booking request: {room.name} by {request.user.username} ({nights} night{"s" if nights != 1 else ""})',
                    link=f'/manage/bookings/',
                    email_subject=f'[StayEase] New booking — {room.name}',
                    email_body=(
                        f'{request.user.get_full_name() or request.user.username} just requested a booking.\n\n'
                        f'Room: {room.name}\nCheck-in: {check_in}\nCheck-out: {check_out}\n'
                        f'Guests: {booking.guests}\nTotal: Rs. {booking.total_amount}\n\n'
                        f'View it at http://127.0.0.1:8000/manage/bookings/'
                    ),
                )
                return redirect('bookings:payment', booking_id=booking.booking_id)
    else:
        form = BookingForm(initial={'guests': 1})

    return render(request, 'bookings/book_room.html', {'form': form, 'room': room})


@login_required
def payment_view(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)

    if hasattr(booking, 'payment') and booking.payment.status == 'success':
        return redirect('bookings:confirmation', booking_id=booking.booking_id)

    if request.method == 'POST':
        method = request.POST.get('method', 'upi')
        # --- Simulated payment gateway ---
        # In production this would call Razorpay / Stripe / PayU etc.
        txn_id = f"TXN{uuid.uuid4().hex[:12].upper()}"
        Payment.objects.update_or_create(
            booking=booking,
            defaults={'method': method, 'transaction_id': txn_id, 'amount': booking.total_amount, 'status': 'success'},
        )
        # NOTE: booking.status stays 'pending' after payment — it only becomes
        # 'confirmed' once the admin manually approves it from /manage/bookings/.
        # This gives the hotel a chance to verify availability before the
        # room is treated as actually booked.

        notify_admins(
            'payment',
            f'Payment received: Rs. {booking.total_amount} for {booking.room.name} ({booking.user.username}) — awaiting your confirmation',
            link='/manage/bookings/',
            email_subject=f'[StayEase] Payment received — {booking.room.name} (needs confirmation)',
            email_body=(
                f'{booking.user.get_full_name() or booking.user.username} completed payment.\n\n'
                f'Room: {booking.room.name}\nAmount: Rs. {booking.total_amount}\n'
                f'Method: {method}\nTransaction ID: {txn_id}\n\n'
                f'This booking is PENDING — please confirm it from the admin panel:\n'
                f'http://127.0.0.1:8000/manage/bookings/'
            ),
        )

        messages.success(request, 'Payment successful! Your booking is now awaiting confirmation from the hotel.')
        return redirect('bookings:confirmation', booking_id=booking.booking_id)

    return render(request, 'bookings/payment.html', {'booking': booking})


@login_required
def confirmation_view(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    return render(request, 'bookings/confirmation.html', {'booking': booking})


@login_required
def booking_history_view(request):
    bookings = Booking.objects.filter(user=request.user).select_related('room')
    return render(request, 'bookings/history.html', {'bookings': bookings})


@login_required
def cancel_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    if booking.status in ('pending', 'confirmed'):
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled successfully.')
    return redirect('bookings:history')


@login_required
def download_invoice_view(request, booking_id):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    import io

    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b><font size=20 color='#0f3d5c'>StayEase</font></b>", styles['Title']))
    elements.append(Paragraph("Hotel Booking Invoice", styles['Heading2']))
    elements.append(Spacer(1, 12))

    info_data = [
        ['Booking ID', str(booking.booking_id)],
        ['Guest Name', booking.user.get_full_name() or booking.user.username],
        ['Room', booking.room.name],
        ['Check-in', booking.check_in.strftime('%d %b %Y')],
        ['Check-out', booking.check_out.strftime('%d %b %Y')],
        ['Nights', str(booking.nights)],
        ['Guests', str(booking.guests)],
        ['Status', booking.get_status_display()],
    ]
    if hasattr(booking, 'payment'):
        info_data.append(['Payment Method', booking.payment.get_method_display()])
        info_data.append(['Transaction ID', booking.payment.transaction_id])

    table = Table(info_data, colWidths=[150, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f4f8')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    amount_data = [['Price per night', f"Rs. {booking.room.price_per_night}"],
                   ['Nights', str(booking.nights)],
                   ['Total Amount', f"Rs. {booking.total_amount}"]]
    amount_table = Table(amount_data, colWidths=[350, 150])
    amount_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f0fe')),
    ]))
    elements.append(amount_table)
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("Thank you for booking with StayEase!", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{booking.booking_id}.pdf"'
    return response
