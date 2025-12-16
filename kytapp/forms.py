# kytapp/forms.py

from django import forms
from django.forms.models import ModelForm,inlineformset_factory
from .models import KYTSession, RiskEvaluation, Countermeasure

# リスク評価用のフォーム
class RiskEvaluationForm(forms.ModelForm):
    class Meta:
        model = RiskEvaluation
        fields = [ 'severity', 'probability' ]
        labels = {
            'severity': '重篤度（1〜5）',
            'probability': '可能性（1〜5）',
        }
        widgets = {
            'severity': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'probability': forms.Select(choices=[(i, i) for i in range(1, 6)]),
        }

# フォームセット取得関数（参加人数に応じて行数を設定）
def get_risk_evaluation_formset(participant_count):
    return inlineformset_factory(
        KYTSession, RiskEvaluation,
        form=RiskEvaluationForm,
        fields=('severity', 'probability'),
        extra=0,
        can_delete=False
    )

# 対策入力フォーム
class CountermeasureForm(forms.ModelForm):
    class Meta:
        model = Countermeasure
        fields = ['who', 'where', 'what', 'when','text']
        labels = {'text': '対策内容'}
        widgets = {
            'who': forms.TextInput(attrs={'placeholder': 'だれが'}),
            'where': forms.TextInput(attrs={'placeholder': 'どこで'}),
            'what': forms.TextInput(attrs={'placeholder': 'なにを'}),
            'when': forms.TextInput(attrs={'placeholder': 'いつ'}),
            'text': forms.Textarea(attrs={'rows': 2, 'cols': 40})
        }

# 対策用フォームセット（固定数でも可変でも、このままでも使えます）
CountermeasureFormSet = inlineformset_factory(
    KYTSession, Countermeasure,
    form=CountermeasureForm,
    extra=1,
    can_delete=True
)
