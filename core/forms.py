from django import forms
from .models import Batch, Student, Payment


# ── Shared widget helpers ────────────────────────────────────────────────────

def _text(placeholder='', cls='form-control'):
    return forms.TextInput(attrs={'class': cls, 'placeholder': placeholder})

def _email(placeholder=''):
    return forms.EmailInput(attrs={'class': 'form-control', 'placeholder': placeholder})

def _textarea(placeholder='', rows=3):
    return forms.Textarea(attrs={'class': 'form-control', 'placeholder': placeholder, 'rows': rows})

def _date():
    return forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})

def _number(placeholder=''):
    return forms.NumberInput(attrs={'class': 'form-control', 'placeholder': placeholder, 'step': '0.01'})

def _select():
    return forms.Select(attrs={'class': 'form-select'})

def _checkbox():
    return forms.CheckboxInput(attrs={'class': 'form-check-input'})


# ── Batch Form ───────────────────────────────────────────────────────────────

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['name', 'subject', 'schedule', 'monthly_fee', 'start_date', 'is_active']
        widgets = {
            'name':        _text('e.g. Class 10 Maths'),
            'subject':     _text('e.g. Mathematics'),
            'schedule':    _text('e.g. Mon/Wed/Fri  6:00 - 7:30 PM'),
            'monthly_fee': _number('e.g. 1500'),
            'start_date':  _date(),
            'is_active':   _checkbox(),
        }
        labels = {
            'monthly_fee': 'Monthly Fee (Rs.)',
            'is_active':   'Currently active?',
        }


# ── Student Form ─────────────────────────────────────────────────────────────

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'email', 'phone', 'address', 'batch', 'is_active']
        widgets = {
            'name':      _text('Full name'),
            'email':     _email('Email (optional)'),
            'phone':     _text('Phone number'),
            'address':   _textarea('Address (optional)'),
            'batch':     _select(),
            'is_active': _checkbox(),
        }
        labels = {
            'is_active': 'Currently active?',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active batches in the dropdown
        self.fields['batch'].queryset = Batch.objects.filter(is_active=True)
        self.fields['batch'].empty_label = '— No batch assigned —'


# ── Payment Form ─────────────────────────────────────────────────────────────

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['student', 'amount', 'date', 'mode', 'reference', 'remarks']
        widgets = {
            'student':   _select(),
            'amount':    _number('Enter amount, e.g. 1500'),
            'date':      _date(),
            'mode':      _select(),
            'reference': _text('e.g. UPI Ref / UTR / Cheque No.'),
            'remarks':   _text('e.g. November fee installment'),
        }
        labels = {
            'amount':    'Amount (Rs.)',
            'reference': 'Reference / Transaction ID (Optional)',
            'remarks':   'Remarks / Note (Optional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.filter(is_active=True).order_by('name')
        self.fields['student'].empty_label = '— Select Student —'
