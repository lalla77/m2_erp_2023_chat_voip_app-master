from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from .models import chatMessages, Conversation
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as UserModel
from django.db.models import Q
import json,datetime
from django.core import serializers
from django.db import models





# Create your views here.


@login_required
def conversation(request, conversation_id):
    conversation = Conversation.objects.get(id=conversation_id)
    messages = chatMessages.objects.filter(conversation=conversation)
    # Mettre à jour le nombre de messages non lus pour cette conversation
    if conversation.user1 == request.user:
        conversation.unread_messages = chatMessages.objects.filter(conversation=conversation, recipient=request.user, unread=True).count()
    else:
        conversation.unread_messages = chatMessages.objects.filter(conversation=conversation, recipient=request.user, unread=True).count()
    conversation.save()
    return render(request, 'conversation.html', {'conversation': conversation, 'messages': messages})


@login_required
def home(request):
    User = get_user_model()
    users = User.objects.all()
    # conversation = Conversation.objects.all()
    chats = {}
    unread_counts = {}
    conversations = {}
    if request.method == 'GET' and 'u' in request.GET:
        # chats = chatMessages.objects.filter(Q(user_from=request.user.id & user_to=request.GET['u']) | Q(user_from=request.GET['u'] & user_to=request.user.id))
        chats = chatMessages.objects.filter(Q(user_from=request.user.id, user_to=request.GET['u']) | Q(user_from=request.GET['u'], user_to=request.user.id))
        chats = chats.order_by('date_created')



    for user in users:
        if user != request.user:
             # count = Conversation.objects.filter(user1=user, user2=request.user, unread_messages__gt=0).count()
             conversation = Conversation.objects.filter(user1=user, user2=request.user, is_read=False)
             # conversations[user.id] = conversation
             for c in conversation:
                 cu = c.unread_messages
                 unread_counts[user.id] = cu
                 conversations[user.id] = c.id
    context = {
        "page":"home",
        "users":users,
        "chats":chats,
        "chat_id": int(request.GET['u'] if request.method == 'GET' and 'u' in request.GET else 0),
        "unread_counts": unread_counts,
        "conversations": conversations,
    }
    print(request.GET['u'] if request.method == 'GET' and 'u' in request.GET else 0)
    return render(request,"chat/home.html",context)

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f'Account successfully created!')
            return redirect('chat-login')
        context = {
            "page":"register",
            "form" : form
        }
    else:
        context = {
            "page":"register",
            "form" : UserRegistrationForm()
        }
    return render(request,"chat/register.html",context)

@login_required
def profile(request):
    context = {
        "page":"profile",
    }
    return render(request,"chat/profile.html",context)

def get_messages(request):
    chats = chatMessages.objects.filter(Q(id__gt=request.POST['last_id']),Q(user_from=request.user.id, user_to=request.POST['chat_id']) | Q(user_from=request.POST['chat_id'], user_to=request.user.id))
    new_msgs = []
    for chat in list(chats):
        data = {}
        data['id'] = chat.id
        data['user_from'] = chat.user_from.id
        data['user_to'] = chat.user_to.id
        data['message'] = chat.message
        data['date_created'] = chat.date_created.strftime("%b-%d-%Y %H:%M")
        print(data)
        new_msgs.append(data)
    return HttpResponse(json.dumps(new_msgs), content_type="application/json")

# def send_chat(request):
#     resp = {}
#     User = get_user_model()
#     if request.method == 'POST':
#         post =request.POST
#
#         u_from = UserModel.objects.get(id=post['user_from'])
#         u_to = UserModel.objects.get(id=post['user_to'])
#         insert = chatMessages(user_from=u_from,user_to=u_to,message=post['message'])
#         try:
#             insert.save()
#             resp['status'] = 'success'
#         except Exception as ex:
#             resp['status'] = 'failed'
#             resp['mesg'] = ex
#     else:
#         resp['status'] = 'failed'
#
#     return HttpResponse(json.dumps(resp), content_type="application/json")
#

def send_chat(request):
    resp = {}
    User = get_user_model()
    if request.method == 'POST':
        post = request.POST

        u_from = UserModel.objects.get(id=post['user_from'])
        u_to = UserModel.objects.get(id=post['user_to'])
        message = post['message']

        conversation = Conversation.objects.filter(user1=u_from).filter(user2=u_to).first()
        if not conversation:
            conversation = Conversation.objects.create(user1=u_from, user2=u_to)
            # conversation.user1.add(u_from)
            # conversation.user2.add(u_to)


        chat_message = chatMessages(user_from=u_from, user_to=u_to, message=message)
        conversation.last_read_message = chat_message
        conversation.unread_messages += 1
        # conversation.save()

        try:
            chat_message.save()
            conversation.save()
            resp['status'] = 'success'
        except Exception as ex:
            resp['status'] = 'failed'
            resp['mesg'] = ex
    else:
        resp['status'] = 'failed'

    return HttpResponse(json.dumps(resp), content_type="application/json")


#      Envoi des notifications aux utilisateurs destinataires
    #      for recipient in conversation.user1.exclude(id=u_from.id):
    #     for recipient in User.objects.exclude(id=u_from.id).filter(id__in=conversation.user1.objects.all()):
    #         Conversation.objects.create(
    #             user_from=u_from,
    #             user_to=recipient,
    #             conversation=conversation,
    #             message=f"Vous avez reçu un nouveau message de {u_from.username}"
    #         )
    #
    #     resp['status'] = 'success'
    # else:
    #     resp['status'] = 'failed'
    #
    # return HttpResponse(json.dumps(resp), content_type="application/json")
    #

def index(request):
    return render(request, 'chat/index.html')

@csrf_exempt
def update_conversation(request, pk):
    # Récupérer la conversation
    conversation = get_object_or_404(Conversation, pk=pk)

    # Mettre à jour l'attribut is_read
    conversation.is_read = True
    # conversation.unread_messages=0
    conversation.save()

    # Retourner une réponse JSON pour indiquer que la mise à jour a été effectuée avec succès
    return JsonResponse({'success': True})




def index(request):
    return render(request, 'chat/index.html')


