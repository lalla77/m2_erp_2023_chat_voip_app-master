from django.db import models
# from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.





class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    gender = models.CharField(max_length=50)
    is_login = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} Profile'

class chatMessages(models.Model):
    # conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    user_from = models.ForeignKey(User,
        on_delete=models.CASCADE,related_name="+")
    user_to = models.ForeignKey(User,
        on_delete=models.CASCADE,related_name="+")
    message = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.message




class Conversation(models.Model):
    user1 = models.ForeignKey(User, related_name='+', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='+', on_delete=models.CASCADE)
    unread_messages = models.IntegerField(default=0)
    last_read_message = models.ForeignKey(chatMessages, on_delete=models.SET_NULL, null=True, related_name='+')
    is_read = models.BooleanField(default=False)

    # def __str__(self):
    #     return self.unread_messages

