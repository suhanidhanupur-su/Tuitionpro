from datetime import date as today_date, datetime
from decimal import Decimal
from calendar import monthrange

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.urls import reverse
from django.http import HttpResponse

from .models import Batch, Student, Attendance, Payment
from .forms import BatchForm, StudentForm, PaymentForm
from .receipt import generate_receipt_pdf


# ══════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════

@login_required
def dashboard(request):
    active_students = Student.objects.filter(is_active=True).select_related('batch')
    total_students  = active_students.count()
    total_batches   = Batch.objects.filter(is_active=True).count()

    # Calculate real-time fees collection and pending
    total_collected = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_due = sum(
        (s.pending_balance for s in active_students if s.pending_balance > 0),
        Decimal('0.00')
    )

    context = {
        'page_title':      'Dashboard',
        'total_students':  total_students,
        'total_batches':   total_batches,
        'total_collected': total_collected,
        'total_due':       total_due,
        'recent_students': Student.objects.select_related('batch').order_by('-created_at')[:5],
        'recent_payments': Payment.objects.select_related('student', 'student__batch').order_by('-created_at')[:5],
    }
    return render(request, 'core/dashboard.html', context)


# ══════════════════════════════════════════════════════════════════
#  BATCH CRUD
# ══════════════════════════════════════════════════════════════════

@login_required
def batch_list(request):
    q = request.GET.get('q', '').strip()
    batches = Batch.objects.all()
    if q:
        batches = batches.filter(Q(name__icontains=q) | Q(subject__icontains=q))
    return render(request, 'core/batches/list.html', {
        'batches': batches, 'q': q, 'page_title': 'Batches',
    })


@login_required
def batch_create(request):
    form = BatchForm(request.POST or None)
    if form.is_valid():
        batch = form.save()
        messages.success(request, f'Batch "{batch.name}" created successfully.')
        return redirect('core:batch_list')
    return render(request, 'core/batches/form.html', {
        'form': form, 'page_title': 'Add Batch', 'action': 'Create',
    })


@login_required
def batch_edit(request, pk):
    batch = get_object_or_404(Batch, pk=pk)
    form = BatchForm(request.POST or None, instance=batch)
    if form.is_valid():
        form.save()
        messages.success(request, f'Batch "{batch.name}" updated successfully.')
        return redirect('core:batch_list')
    return render(request, 'core/batches/form.html', {
        'form': form, 'object': batch,
        'page_title': f'Edit Batch - {batch.name}', 'action': 'Update',
    })


@login_required
def batch_delete(request, pk):
    batch = get_object_or_404(Batch, pk=pk)
    if request.method == 'POST':
        name = batch.name
        batch.delete()
        messages.success(request, f'Batch "{name}" deleted.')
        return redirect('core:batch_list')
    return render(request, 'core/confirm_delete.html', {
        'object': batch, 'object_type': 'Batch',
        'cancel_url': 'core:batch_list', 'page_title': f'Delete Batch - {batch.name}',
    })


# ══════════════════════════════════════════════════════════════════
#  STUDENT CRUD
# ══════════════════════════════════════════════════════════════════

@login_required
def student_list(request):
    q = request.GET.get('q', '').strip()
    batch_id = request.GET.get('batch', '').strip()
    students = Student.objects.select_related('batch').all()
    if q:
        students = students.filter(
            Q(name__icontains=q) | Q(phone__icontains=q) | Q(email__icontains=q)
        )
    if batch_id:
        students = students.filter(batch_id=batch_id)
    return render(request, 'core/students/list.html', {
        'students': students,
        'batches': Batch.objects.filter(is_active=True),
        'q': q, 'selected_batch': batch_id, 'page_title': 'Students',
    })


@login_required
def student_create(request):
    form = StudentForm(request.POST or None)
    if form.is_valid():
        student = form.save()
        messages.success(request, f'Student "{student.name}" enrolled successfully.')
        return redirect('core:student_list')
    return render(request, 'core/students/form.html', {
        'form': form, 'page_title': 'Enroll Student', 'action': 'Enroll',
    })


@login_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST or None, instance=student)
    if form.is_valid():
        form.save()
        messages.success(request, f'Student "{student.name}" updated successfully.')
        return redirect('core:student_list')
    return render(request, 'core/students/form.html', {
        'form': form, 'object': student,
        'page_title': f'Edit Student - {student.name}', 'action': 'Update',
    })


@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        name = student.name
        student.delete()
        messages.success(request, f'Student "{name}" removed.')
        return redirect('core:student_list')
    return render(request, 'core/confirm_delete.html', {
        'object': student, 'object_type': 'Student',
        'cancel_url': 'core:student_list', 'page_title': f'Delete Student - {student.name}',
    })


# ══════════════════════════════════════════════════════════════════
#  ATTENDANCE
# ══════════════════════════════════════════════════════════════════

@login_required
def attendance_mark(request):
    batches  = Batch.objects.filter(is_active=True)
    today    = today_date.today()

    batch_id = (request.POST.get('batch') or request.GET.get('batch', '')).strip()
    date_str = (request.POST.get('date')  or request.GET.get('date',  str(today))).strip()

    selected_batch = None
    students       = []
    attendance_map = {}
    already_saved  = False

    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = today
        date_str = str(today)

    if batch_id:
        selected_batch = get_object_or_404(Batch, pk=batch_id)
        students = Student.objects.filter(batch=selected_batch, is_active=True).order_by('name')

        existing = Attendance.objects.filter(
            batch=selected_batch,
            date=selected_date,
            student__in=students,
        )
        attendance_map = {a.student_id: a.status for a in existing}
        already_saved  = existing.exists()

    if request.method == 'POST' and selected_batch and students.exists():
        saved_count = 0
        for student in students:
            status = request.POST.get(f'status_{student.pk}', Attendance.STATUS_ABSENT)
            if status not in (Attendance.STATUS_PRESENT, Attendance.STATUS_ABSENT):
                status = Attendance.STATUS_ABSENT
            Attendance.objects.update_or_create(
                student=student,
                date=selected_date,
                defaults={'batch': selected_batch, 'status': status},
            )
            saved_count += 1

        messages.success(
            request,
            f'Attendance saved for {selected_batch.name} on '
            f'{selected_date.strftime("%d %b %Y")} ({saved_count} students).'
        )
        base = reverse('core:attendance_mark')
        return redirect(f'{base}?batch={batch_id}&date={date_str}')

    return render(request, 'core/attendance/mark.html', {
        'page_title':      'Daily Attendance',
        'batches':         batches,
        'selected_batch':  selected_batch,
        'selected_date':   date_str,
        'students':        students,
        'attendance_map':  attendance_map,
        'already_saved':   already_saved,
        'today':           str(today),
    })


@login_required
def attendance_report(request):
    batches = Batch.objects.filter(is_active=True)
    today   = today_date.today()

    batch_id = request.GET.get('batch', '').strip()
    try:
        month = int(request.GET.get('month', today.month))
        year  = int(request.GET.get('year',  today.year))
    except ValueError:
        month, year = today.month, today.year

    month = max(1, min(12, month))

    selected_batch = None
    report_data    = []
    days_in_month  = 0
    month_name     = ''

    if batch_id:
        selected_batch = get_object_or_404(Batch, pk=batch_id)
        students       = Student.objects.filter(batch=selected_batch, is_active=True).order_by('name')
        days_in_month  = monthrange(year, month)[1]
        month_name     = datetime(year, month, 1).strftime('%B %Y')

        records = Attendance.objects.filter(
            batch=selected_batch,
            date__year=year,
            date__month=month,
            student__in=students,
        ).values('student_id', 'date__day', 'status')

        att_lookup = {}
        for rec in records:
            sid = rec['student_id']
            att_lookup.setdefault(sid, {})[rec['date__day']] = rec['status']

        for student in students:
            day_map       = att_lookup.get(student.pk, {})
            present_count = sum(1 for s in day_map.values() if s == 'P')
            absent_count  = sum(1 for s in day_map.values() if s == 'A')
            total_marked  = len(day_map)
            percent       = round(present_count / total_marked * 100) if total_marked else 0

            report_data.append({
                'student':  student,
                'day_map':  day_map,
                'present':  present_count,
                'absent':   absent_count,
                'total':    total_marked,
                'percent':  percent,
            })

    month_choices = [(i, datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)]
    year_choices  = list(range(today.year - 2, today.year + 1))

    return render(request, 'core/attendance/report.html', {
        'page_title':      'Monthly Attendance Report',
        'batches':         batches,
        'selected_batch':  selected_batch,
        'batch_id':        batch_id,
        'month':           month,
        'year':            year,
        'month_name':      month_name,
        'days_in_month':   days_in_month,
        'report_data':     report_data,
        'month_choices':   month_choices,
        'year_choices':    year_choices,
    })


# ══════════════════════════════════════════════════════════════════
#  FEES & PAYMENTS
# ══════════════════════════════════════════════════════════════════

@login_required
def fee_dashboard(request):
    """
    Main Fees dashboard:
      - Student-wise ledger showing pending balance
      - Filter by batch, status (pending, cleared, advance), and search
      - Recent transaction logs with download receipt links
    """
    q        = request.GET.get('q', '').strip()
    batch_id = request.GET.get('batch', '').strip()
    status   = request.GET.get('status', '').strip()  # 'due', 'cleared', 'advance'

    students = Student.objects.filter(is_active=True).select_related('batch')

    if q:
        students = students.filter(
            Q(name__icontains=q) | Q(phone__icontains=q)
        )
    if batch_id:
        students = students.filter(batch_id=batch_id)

    # Convert to list so we can evaluate pending balances
    student_list_evaluated = list(students)

    if status == 'due':
        student_list_evaluated = [s for s in student_list_evaluated if s.pending_balance > 0]
    elif status == 'cleared':
        student_list_evaluated = [s for s in student_list_evaluated if s.pending_balance == 0]
    elif status == 'advance':
        student_list_evaluated = [s for s in student_list_evaluated if s.pending_balance < 0]

    # Metrics
    all_active = Student.objects.filter(is_active=True).select_related('batch')
    tot_expected = sum((s.total_fee_expected for s in all_active), Decimal('0.00'))
    tot_collected = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    tot_pending = sum((s.pending_balance for s in all_active if s.pending_balance > 0), Decimal('0.00'))

    recent_payments = Payment.objects.select_related('student', 'student__batch').order_by('-date', '-created_at')[:10]

    return render(request, 'core/fees/dashboard.html', {
        'page_title':      'Fees & Payments',
        'students':        student_list_evaluated,
        'batches':         Batch.objects.filter(is_active=True),
        'q':               q,
        'selected_batch':  batch_id,
        'selected_status': status,
        'tot_expected':    tot_expected,
        'tot_collected':   tot_collected,
        'tot_pending':     tot_pending,
        'recent_payments': recent_payments,
    })


@login_required
def payment_create(request):
    """
    Record a fee payment for a student.
    Can be pre-filled with ?student=<id>.
    """
    student_id = request.GET.get('student', '').strip()
    initial_data = {}
    selected_student = None

    if student_id:
        selected_student = get_object_or_404(Student, pk=student_id)
        initial_data['student'] = selected_student
        # Pre-fill amount with positive pending balance or monthly fee
        if selected_student.pending_balance > 0:
            initial_data['amount'] = selected_student.pending_balance
        elif selected_student.batch and selected_student.batch.monthly_fee:
            initial_data['amount'] = selected_student.batch.monthly_fee

    form = PaymentForm(request.POST or None, initial=initial_data)

    if form.is_valid():
        payment = form.save()
        messages.success(
            request,
            f'Payment of Rs. {payment.amount:,.2f} recorded for {payment.student.name}. '
            f'Receipt No: {payment.receipt_no}'
        )
        return redirect('core:payment_detail', pk=payment.pk)

    return render(request, 'core/fees/form.html', {
        'form':             form,
        'selected_student': selected_student,
        'page_title':       'Record Fee Payment',
    })


@login_required
def payment_detail(request, pk):
    """
    Payment confirmation & receipt preview page with download PDF button.
    """
    payment = get_object_or_404(Payment.objects.select_related('student', 'student__batch'), pk=pk)
    return render(request, 'core/fees/detail.html', {
        'payment':    payment,
        'page_title': f'Payment Receipt — {payment.receipt_no}',
    })


@login_required
def student_ledger(request, pk):
    """
    Shows full payment history and fee ledger for a single student.
    """
    student = get_object_or_404(Student.objects.select_related('batch'), pk=pk)
    payments = student.payments.all().order_by('-date', '-created_at')

    return render(request, 'core/fees/student_ledger.html', {
        'student':    student,
        'payments':   payments,
        'page_title': f'Fee Ledger — {student.name}',
    })


@login_required
def payment_receipt_pdf(request, pk):
    """
    Downloads receipt PDF.
    """
    payment = get_object_or_404(Payment.objects.select_related('student', 'student__batch'), pk=pk)
    pdf_bytes = generate_receipt_pdf(payment)

    filename = f"Receipt_{payment.receipt_no}.pdf"
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
