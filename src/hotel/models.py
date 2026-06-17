from django.db import models
from django.contrib.auth.models import User
# Create your models here.
#TABLE HOTEL
class Hotel(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    logo = models.ImageField(upload_to='hotel/',blank=True)
    photo = models.ImageField(upload_to='hotel/',blank=True)
    
    def __str__(self):
        return self.name


#TABLE TYPE CHAMBRE
class Type_chambre(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    
    def __str__(self):
        return self.title

#TABLE EQUIPEMENT CHAMBRE
class Equipement(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    image = models.ImageField(upload_to='equipement/',blank=True)
    
    def __str__(self):
        return self.title

#TABLE CHAMBRE AVEC LES RELATION
class Chambre(models.Model):
    ROLE_CHOISE = (
        ('Disponible', 'Disponible'),
        ('Non disponible', 'Non disponible'),
    )
    titre = models.CharField(max_length=50)
    nbr_personne = models.IntegerField()
    prix = models.DecimalField(max_digits=9, decimal_places=2)
    status = models.CharField(max_length=20, choices=ROLE_CHOISE)

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    type_chambre = models.ForeignKey(Type_chambre, on_delete=models.CASCADE)
    equipements = models.ManyToManyField(Equipement, blank=True, related_name='chambres')
    def __str__(self):
        return self.titre

#TABLE CHAMBRE
class Chambre_photo(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='chambre/',blank=True)
    
    chambre = models.ForeignKey(Chambre, on_delete=models.CASCADE,related_name='photos')
    def __str__(self):
        return self.name
    
#TABLE RESERVATION
class Reservation(models.Model):
    ROLES_CHOISE = (
        ('Refusé','Refusé'),
        ('En attente de validation','En attente de validation'),
        ('Validé','Validé'),
        )
    
    nbr_pers = models.IntegerField()
    prix_total = models.DecimalField(max_digits=9, decimal_places=2)
    status = models.CharField(max_length=50,choices=ROLES_CHOISE,default='En attente de validation')
    date_arrivee = models.DateTimeField()
    date_depart = models.DateTimeField()
    
    #Relation
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    chambre = models.ForeignKey(Chambre, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.status

#TABLE PAIEMENT
class Payement(models.Model):
    ROLE_CHOISE=(
        ('Payé','Payé'),
        ('Non payé','Non payé'),
        )
    PAYEMENT_CHOISE = (
        ('Espece','Espece'),
        ('Mobile','Mobile'),
        )
    cin = models.CharField(max_length=50)
    capture = models.ImageField(upload_to='payement',blank=True)
    description = models.TextField()
    status = models.CharField(max_length=50,choices=ROLE_CHOISE,default='Non payé')
    mode_payement = models.CharField(max_length=50,choices=PAYEMENT_CHOISE, default='Sur place')
    
    #Relation
    reservation = models.OneToOneField(Reservation,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.mode_payement
    
#AVIS CLIENT
class Avis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    note = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
#CONTACT
class ContactMessage(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    sujet = models.CharField(max_length=150)
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nom} - {self.sujet}"