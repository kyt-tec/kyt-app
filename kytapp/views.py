# kytapp/views.py

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.views import View
from django.views.generic.edit import UpdateView
from .models import KYTSession,Participant,RiskEvaluation,Countermeasure
from .forms import  get_risk_evaluation_formset,CountermeasureFormSet
from django.views.generic import View,CreateView  
from django.urls import reverse
from django.forms import modelformset_factory
from django.http import HttpResponse
from django.forms.models import inlineformset_factory
from .forms import RiskEvaluationForm
from kytapp.models import Participant



def top(request):
    return HttpResponse("<h1>ようこそ KYT アプリへ</h1>")
import random

WHAT_CARDS = [
    {'image': 'what/what(カッター).jpg', 'text': 'カッター'},
    {'image': 'what/what(きり).jpg', 'text': 'きり'},
    {'image': 'what/what(のこぎり).jpg', 'text': 'のこぎり'},
    {'image': 'what/what(はさみ).jpg', 'text': 'はさみ'},
    {'image': 'what/what(ボール盤).jpg', 'text': 'ボール盤'},
    {'image': 'what/what(金づち).jpg', 'text': '金づち'},
    {'image': 'what/what(電動糸鋸).jpg', 'text': '電動糸鋸'},
]

class StartNewSessionView(CreateView):
    model = KYTSession
    fields = ['participant_count','round1_mode']
    template_name = 'kytapp/start.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)

        if self.object.round1_mode == 'fixed_what':
            card = random.choice(WHAT_CARDS)
            self.object.fixed_what_image = card['image']
            self.object.fixed_what_text = card['text']
        else:
            self.object.fixed_what_image = None

        self.object.save()
        return super().form_valid(form)

    #def form_valid(self, form):#
        # self.object = form.save()# セッション作成直後に participant_count を取得しておく
     #   return super().form_valid(form)

    def get_success_url(self):
        return reverse('kytapp:home', kwargs={'pk': self.object.pk})



COLORS = ["#ff6b6b", "#4dabf7", "#51cf66", "#ffa94d",
          "#9775fa", "#f06595", "#63e6be", "#d0bfff"]
class HomeIndexView(View):
    template_name = 'kytapp/home.html'

    def get(self, request):
        # セッション一覧を出す or 新規作成画面
        return render(request, self.template_name)



class HomeView(View):
    template_name = 'kytapp/group_select.html'

    def get(self, request, pk):
        session = get_object_or_404(KYTSession, pk=pk)

        # 参加者生成（初回のみ）
        needed = session.participant_count - session.participants.count()
        for i in range(needed):
            Participant.objects.create(
                session=session,
                name=f"参加者{i+1}",
                color=COLORS[i % len(COLORS)] if hasattr(Participant, "color") else "#cccccc"
            )

        ParticipantFormSet = modelformset_factory(
            Participant,
            fields=['name'],
            extra=0
        )
        formset = ParticipantFormSet(
            queryset=session.participants.all(),
            prefix='p'
        )

        # 🔥 form と participant をペアにして template へ渡す
        rows = []
        participants = list(session.participants.all())
        for form, participant in zip(formset.forms, participants):
            rows.append({
                "form": form,
                "participant": participant,
            })

        return render(request, self.template_name, {
            'session': session,
            'formset': formset,
            'rows': rows,
        })

    def post(self, request, pk):
        session = get_object_or_404(KYTSession, pk=pk)

        ParticipantFormSet = modelformset_factory(
            Participant,
            fields=['name'],
            extra=0
        )
        formset = ParticipantFormSet(
            request.POST,
            queryset=session.participants.all(),
            prefix='p'
        )

        if formset.is_valid():
            formset.save()
            return redirect('kytapp:round1', pk=session.pk)
        else:
            print("❌ formset invalid:", formset.errors)

        # バリデーション NG のときも rows を作り直して返す
        rows = []
        participants = list(session.participants.all())
        for form, participant in zip(formset.forms, participants):
            rows.append({
                "form": form,
                "participant": participant,
            })

        return render(request, self.template_name, {
            'session': session,
            'formset': formset,
            'rows': rows,
        })




class Round1View(View):
    template_name = 'kytapp/round1.html'


    def get(self, request, pk):
        session = get_object_or_404(KYTSession, pk=pk)

        
        ParticipantFormSet = modelformset_factory(
            Participant,
            fields=['name','who', 'where', 'when', 'what', 'how', 'expected_injury'],
            extra=0,
            can_delete=False
        )
        formset = ParticipantFormSet(queryset=session.participants.all(),prefix='form')

        return render(request, self.template_name, {
            'formset': formset,
            'session': session,
            'card_images': self.get_card_images(session),
            'participants': session.participants.all(),
            'card_categories': ['who','where','when','what'],
        })

    def post(self, request, pk):
        session = get_object_or_404(KYTSession, pk=pk)
        ParticipantFormSet = modelformset_factory(
            Participant,
            fields=['name','who', 'where', 'when', 'what', 'how', 'expected_injury'],
            extra=0,
            can_delete=False
        )
        formset = ParticipantFormSet(request.POST, queryset=session.participants.all(),prefix='form')

        if formset.is_valid():
            formset.save()
            return redirect('kytapp:round2', pk=session.pk)

        return render(request, self.template_name, {
            'formset': formset,
            'session': session,
            'card_images': self.get_card_images(session),
            'participants': session.participants.all(),
            'card_categories': ['who', 'where', 'when', 'what']
        })

    def get_card_images(self, session):
        # what の候補をまず定義
        what_cards = [
            {'image': 'what/what(カッター).jpg', 'text': 'カッター'},
            {'image': 'what/what(きり).jpg', 'text': 'きり'},
            {'image': 'what/what(のこぎり).jpg', 'text': 'のこぎり'},
            {'image': 'what/what(はさみ).jpg', 'text': 'はさみ'},
            {'image': 'what/what(ボール盤).jpg', 'text': 'ボール盤'},
            {'image': 'what/what(金づち).jpg', 'text': '金づち'},
            {'image': 'what/what(電動糸鋸).jpg', 'text': '電動糸鋸'},
        ]

        # ★ここで分岐（return の前！）
        if session.round1_mode == 'fixed_what':
            what_cards = [{
                'image': session.fixed_what_image,
                'text': session.fixed_what_text,
            }]  

            

        # 最後にまとめて return
        return {
            'who': [
                {'image': 'who/who(わたし).jpg', 'text': 'わたし'},
                {'image': 'who/who(近くの人).jpg', 'text': '近くの人'},
                {'image': 'who/who(先生).jpg', 'text': '先生'},
                {'image': 'who/who(友達).jpg', 'text': '友達'},
            ],
            'where': [
                {'image': 'where/where(机).jpg', 'text': '机'},
                {'image': 'where/where(作業台).jpg', 'text': '作業台'},
                {'image': 'where/where(床).jpg', 'text': '床'},
                {'image': 'where/where(通り道).jpg', 'text': '通り道'},
            ],
            'when': [
                {'image': 'when/when(休み時間).jpg', 'text': '休み時間'},
                {'image': 'when/when(作業中).jpg', 'text': '作業中'},
                {'image': 'when/when(準備中).jpg', 'text': '準備中'},
                {'image': 'when/when(片付け中).jpg', 'text': '片付け中'},
                {'image': 'when/when(話を聞いている時).jpg', 'text': '話を聞いている時'},
            ],
            'what': what_cards,
        }

       
        

    def get_success_url(self):
        return f'/kyt/round2/{self.object.pk}/'



# views.py
# kytapp/views.py


class Round2View(View):
    template_name = 'kytapp/round2.html'

    def get(self, request, pk):
        session = get_object_or_404(KYTSession, pk=pk)
        participants = list(session.participants.all())

        # 初回のみ RiskEvaluation を作成
        if session.evaluations.count() == 0:
            for p in participants:
                RiskEvaluation.objects.create(
                    session=session,
                    participant=p
                )

        queryset = session.evaluations.order_by('id')

        EvalFormSet = get_risk_evaluation_formset(len(participants))
        formset = EvalFormSet(
            instance=session,
            queryset=queryset
        )

        return render(request, self.template_name, {
            'formset': formset,
            'participants': participants,
            'session': session,
            'participant_count': len(participants),
            'most_dangerous_pks': [],
        })

    def post(self, request, pk):
        session = get_object_or_404(KYTSession, pk=pk)
        participants = list(session.participants.all())

        queryset = session.evaluations.order_by('id')

        EvalFormSet = get_risk_evaluation_formset(len(participants))
        formset = EvalFormSet(
            request.POST,
            instance=session,
            queryset=queryset
        )

        if not formset.is_valid():
            print("❌ FORMSET ERRORS:", formset.errors)
            return render(request, self.template_name, {
                'formset': formset,
                'participants': participants,
                'session': session,
                'participant_count': len(participants),
                'most_dangerous_pks': [],
            })

        # 🔵 ここで初めて保存される
        formset.save()

        evaluations = session.evaluations.select_related('participant').order_by('id')

        max_score = None
        most_dangerous = []

        for e in evaluations:
            if e.severity and e.probability:
                score = e.severity * e.probability
                if max_score is None or score > max_score:
                    max_score = score
                    most_dangerous = [e]
                elif score == max_score:
                    most_dangerous.append(e)

        session.risk_score = max_score or 0
        session.save()

        print("POST keys:", list(request.POST.keys())[:30])
        print("POST sample:", {k: request.POST[k] for k in request.POST.keys() if "severity" in k or "probability" in k})

        request.session['dangerous_participant_ids'] = [
            e.participant_id for e in most_dangerous
        ]
        request.session['danger_max_score'] = session.risk_score

        ## ★ WebSocket通知（risk_score は @property なので () なし）
        
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()

        # ★ 危険度一覧をまとめて送る
        risk_rows = []
        for e in evaluations:
            risk_rows.append({
                "pk": e.pk,
                "severity": e.severity,
                "probability": e.probability,
                "score": e.risk_score,
                "is_max": e in most_dangerous,
            })

        async_to_sync(channel_layer.group_send)(
            f"kyt_{session.id}",
            {
                "type": "broadcast_message",
                "data": {
                    "type": "risk_result",
                    "rows": risk_rows,
                }
            }
        )


        if request.POST.get("action") == "next":
            return redirect('kytapp:round3', pk=session.pk)

        return render(request, self.template_name, {
            'formset': formset,
            'participants': participants,
            'session': session,
            'participant_count': len(participants),
            'most_dangerous_pks': [e.pk for e in most_dangerous],
        })

    
 ## 


    


class Round3View(View):
    template_name = 'kytapp/round3.html'


    def get(self, request, pk):
        session = get_object_or_404(KYTSession, pk=pk)
        formset = CountermeasureFormSet(queryset=session.countermeasures.all())
        

        # 評価者名に対応する参加者情報取得
        ids = request.session.get('dangerous_participant_ids', [])
        max_score = request.session.get('danger_max_score', None)

        if ids:
            danger_participants = session.participants.filter(id__in=ids)
        else:
            danger_participants=[]
            
        

        return render(request, self.template_name, {
            'formset': formset,
            'session': session,
            'danger_participants': danger_participants,
            'max_score': max_score,
        })

    def post(self, request, pk):
        session = get_object_or_404(KYTSession, pk=pk)
        formset = CountermeasureFormSet(request.POST, queryset=session.countermeasures.all())


        print("📩 POSTリクエスト受信")
        if formset.is_valid():
            print("✅ formset is valid")

            countermeasures = formset.save(commit=False)
            #いったん全部false
            session.countermeasures.update(is_best=False)

            #選ばれたindex
            best_index = request.POST.get("best_countermeasure")

            for i,cm in enumerate(countermeasures):
                cm.session = session
                if best_index is not None and int(best_index) == i:
                    cm.is_best = True
                cm.save()

            return redirect('kytapp:round4', pk=session.pk)
        
        return render(request, self.template_name, {
            'formset': formset,
            'session': session,
        })



class Round4View(UpdateView):
    model = KYTSession
    fields = ['final_goal']
    template_name = 'kytapp/round4.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.object
        dangerous_ids = self.request.session.get('dangerous_participant_ids', [])
        danger_participant = session.participants.filter(id=dangerous_ids[0]).first() if dangerous_ids else None
        context['participant'] = danger_participant

        best_countermeasure = session.countermeasures.filter(is_best=True).first()
        context['best_countermeasure'] = best_countermeasure

        context['session'] = session

       

        # 危険度が高かった参加者ID取得
        dangerous_ids = self.request.session.get('dangerous_participant_ids', [])
        if dangerous_ids:
            # 先頭の1人を対象
            participant = session.participants.filter(id=dangerous_ids[0]).first()
        else:
            participant = None

        context['participant'] = participant  # 最も危険な人の情報を渡す
        context['session'] = session
        return context
    
    def get_success_url(self):
        return reverse('kytapp:complete', kwargs={'pk': self.object.pk})

  # 完了画面へのURL
class CompleteView(View):
    template_name = 'kytapp/complete.html'

    def get(self, request, pk):
        session = get_object_or_404(KYTSession, pk=pk)

        # 最も危険度が高かった参加者IDをセッションから取得
        ids = request.session.get('dangerous_participant_ids', [])
        if ids:
            dangerous_participant = session.participants.filter(id=ids[0]).first()
        else:
            dangerous_participant = None

        # 対策
        best_countermeasure = session.countermeasures.filter(is_best=True).first()

        context = {
            'session': session,
            'participant': dangerous_participant,
            'best_countermeasure': best_countermeasure,
        }
        return render(request, self.template_name, context)
    


