from django.db import models
import uuid
# Create your models here.
class User(models.Model):
    #user
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)

class UserSongInteraction(models.Model):
    #user foreign key
    liked = models.BooleanField(default=False)
    playlist = models.BooleanField(default=False)
    interaction_date = models.DateTimeField(auto_now_add=True)

