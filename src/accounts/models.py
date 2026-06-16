from django.db import models
from django.contrib.auth.models import User
# Create your models here.
#TABLE USER-PROFIL
class User_profil(models.Model):
    ROLE_CHOICES = (
        ('Admin','Admin'),
        ('User','User'),
        ('Responsable','Responsable'),
    )
    name = models.CharField(max_length=50,blank=True)
    role = models.CharField(max_length=50,choices=ROLE_CHOICES, default='User',blank=True)
    photo = models.ImageField(upload_to='Utilisateur',blank=True, null=True)
    
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.role
    
    class Meta:
        verbose_name = 'User_profil'
        verbose_name_plural = 'User_profils'
    