from django.contrib import admin
from .models import UserProfile, chatMessages, Conversation


admin.site.register(UserProfile)
admin.site.register(chatMessages)
admin.site.register(Conversation)


