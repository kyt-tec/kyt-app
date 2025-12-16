# kytapp/models.py
from django.db import models
import random

class KYTSession(models.Model):
    participant_count = models.IntegerField("参加者人数", default=1)
    who = models.CharField(max_length=100, blank=True,null=True)
    where = models.CharField(max_length=200, blank=True,null=True)
    when = models.CharField(max_length=100, blank=True,null=True)
    what = models.CharField(max_length=200, blank=True,null=True)
    how = models.TextField(blank=True,null=True)
    image = models.ImageField(upload_to='kyt_images/', null=True, blank=True)
    expected_injury = models.TextField(blank=True,null=True)

    ROUND1_MODE_CHOICES = [
        ('random', 'すべてランダム'),
        ('fixed_what', 'whatを固定'),
    ]
    round1_mode = models.CharField(
        max_length=20,
        choices=ROUND1_MODE_CHOICES,
        default='random'
    )
    fixed_what_image = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    fixed_what_text = models.CharField(
    max_length=50,
    blank=True,
    null=True
)


    

    # 第4ラウンド
    final_goal = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    risk_score = models.IntegerField(null=True, blank=True)



    def __str__(self):
        return f"KYTSession {self.pk} - {self.created_at.date()}"


class RiskEvaluation(models.Model):
    #  Round2で4人分の入力を扱うための外部キー
    session = models.ForeignKey(KYTSession, on_delete=models.CASCADE, related_name='evaluations')

    # 各評価者（4人分など）の名前
    evaluator_name = models.CharField(max_length=100, blank=True)

    # 危険度評価項目
    severity = models.IntegerField(null=True, blank=True)
    probability = models.IntegerField(null=True, blank=True)
    participant = models.ForeignKey('Participant', null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def risk_score(self):
        if self.severity and self.probability:
            return self.severity * self.probability
        return None

    def __str__(self):
        return f"Evaluation by {self.evaluator_name} (Session {self.session.id})"


class Countermeasure(models.Model):
    session = models.ForeignKey(KYTSession, on_delete=models.CASCADE, related_name='countermeasures')

    who   = models.CharField("だれが", max_length=100, blank=True)
    where = models.CharField("どこで", max_length=100, blank=True)
    what  = models.CharField("なにを", max_length=100, blank=True)
    when  = models.CharField("いつ", max_length=100, blank=True)
    text = models.TextField("対策内容")

    is_best = models.BooleanField(default=False)

    def __str__(self):
        return f"対策: {self.text[:20]}"

    
class Participant(models.Model):
    session = models.ForeignKey(KYTSession, on_delete=models.CASCADE, related_name='participants')
    name = models.CharField(max_length=100)  # Aさん、Bさんなど
    who = models.CharField(max_length=100, blank=True,null=True)
    where = models.CharField(max_length=100, blank=True,null=True)
    when = models.CharField(max_length=100, blank=True,null=True)
    what = models.CharField(max_length=100, blank=True,null=True)
    how = models.TextField(blank=True,null=True)
    expected_injury = models.TextField(blank=True,null=True)

    color = models.CharField(max_length=10, default="#ccc")



    def __str__(self):
        return f"{self.name} in Session {self.session.pk}"