from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Batch, Student
from .forms import BatchForm, StudentForm


# ══════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════

@login_required
def dashboard(request):
    context = {
        'page_title': 'Dashboard',
        'total_students': Student.objects.filter(is_active=True).count(),
        'total_batches':  Batch.objects.filter(is_active=True).count(),
        'recent_students': Student.objects.select_related('batch').order_by('-created_at')[:5],
    }
    return render(request, 'core/dashboard.html', context)


# ══════════════════════════════════════════════════════════════════
#  BATCH CRUD
# ══════════════════════════════════════════════════════════════════

@login_required
def batch_list(request):
    """List all batches with optional search."""
    q = request.GET.get('q', '').strip()
    batches = Batch.objects.all()
    if q:
        batches = batches.filter(
            Q(name__icontains=q) | Q(subject__icontains=q)
        )
    return render(request, 'core/batches/list.html', {
        'batches': batches,
        'q': q,
        'page_title': 'Batches',
    })


@login_required
def batch_create(request):
    """Create a new batch."""
    form = BatchForm(request.POST or None)
    if form.is_valid():
        batch = form.save()
        messages.success(request, f'Batch "{batch.name}" created successfully.')
        return redirect('core:batch_list')
    return render(request, 'core/batches/form.html', {
        'form': form,
        'page_title': 'Add Batch',
        'action': 'Create',
    })


@login_required
def batch_edit(request, pk):
    """Edit an existing batch."""
    batch = get_object_or_404(Batch, pk=pk)
    form = BatchForm(request.POST or None, instance=batch)
    if form.is_valid():
        form.save()
        messages.success(request, f'Batch "{batch.name}" updated successfully.')
        return redirect('core:batch_list')
    return render(request, 'core/batches/form.html', {
        'form': form,
        'object': batch,
        'page_title': f'Edit Batch — {batch.name}',
        'action': 'Update',
    })


@login_required
def batch_delete(request, pk):
    """Confirm and delete a batch."""
    batch = get_object_or_404(Batch, pk=pk)
    if request.method == 'POST':
        name = batch.name
        batch.delete()
        messages.success(request, f'Batch "{name}" deleted.')
        return redirect('core:batch_list')
    return render(request, 'core/confirm_delete.html', {
        'object': batch,
        'object_type': 'Batch',
        'cancel_url': 'core:batch_list',
        'page_title': f'Delete Batch — {batch.name}',
    })


# ══════════════════════════════════════════════════════════════════
#  STUDENT CRUD
# ══════════════════════════════════════════════════════════════════

@login_required
def student_list(request):
    """List students with search and optional batch filter."""
    q = request.GET.get('q', '').strip()
    batch_id = request.GET.get('batch', '').strip()

    students = Student.objects.select_related('batch').all()

    if q:
        students = students.filter(
            Q(name__icontains=q) |
            Q(phone__icontains=q) |
            Q(email__icontains=q)
        )
    if batch_id:
        students = students.filter(batch_id=batch_id)

    batches = Batch.objects.filter(is_active=True)

    return render(request, 'core/students/list.html', {
        'students': students,
        'batches': batches,
        'q': q,
        'selected_batch': batch_id,
        'page_title': 'Students',
    })


@login_required
def student_create(request):
    """Create a new student."""
    form = StudentForm(request.POST or None)
    if form.is_valid():
        student = form.save()
        messages.success(request, f'Student "{student.name}" enrolled successfully.')
        return redirect('core:student_list')
    return render(request, 'core/students/form.html', {
        'form': form,
        'page_title': 'Enroll Student',
        'action': 'Enroll',
    })


@login_required
def student_edit(request, pk):
    """Edit an existing student."""
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST or None, instance=student)
    if form.is_valid():
        form.save()
        messages.success(request, f'Student "{student.name}" updated successfully.')
        return redirect('core:student_list')
    return render(request, 'core/students/form.html', {
        'form': form,
        'object': student,
        'page_title': f'Edit Student — {student.name}',
        'action': 'Update',
    })


@login_required
def student_delete(request, pk):
    """Confirm and delete a student."""
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        name = student.name
        student.delete()
        messages.success(request, f'Student "{name}" removed.')
        return redirect('core:student_list')
    return render(request, 'core/confirm_delete.html', {
        'object': student,
        'object_type': 'Student',
        'cancel_url': 'core:student_list',
        'page_title': f'Delete Student — {student.name}',
    })
