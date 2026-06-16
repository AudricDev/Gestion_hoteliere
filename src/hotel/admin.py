from django.contrib import admin
from .models import Hotel,Chambre_photo,Type_chambre,Equipement,Chambre,Reservation,Payement,Avis
from accounts.models import User_profil
# Register your models here.

class HotelAdmin(admin.ModelAdmin):
    list_display = ('name','description','logo','photo')
admin.site.register(Hotel, HotelAdmin)

#affichage chambre sur admin
class Chambre_photoAdmin(admin.ModelAdmin):
    list_display = ('name','image','chambre')
admin.site.register(Chambre_photo,Chambre_photoAdmin) 

#affichage type chambre sur admin
class Type_chambreAdmin(admin.ModelAdmin):
    list_display = ('title','description')
admin.site.register(Type_chambre,Type_chambreAdmin)

#affichage equipement
class EquipementAdmin(admin.ModelAdmin):
    list_display = ('title','description','image')
admin.site.register(Equipement,EquipementAdmin)

#affichage chambre
class ChambreAdmin(admin.ModelAdmin):
    list_display = ('titre','nbr_personne','prix','status','hotel','type_chambre')
admin.site.register(Chambre,ChambreAdmin)

#affichage User_profil
class User_profilAdmin(admin.ModelAdmin):
    list_display = ('role','photo','user_id')
admin.site.register(User_profil,User_profilAdmin)

#affichage reservation
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('nbr_pers','prix_total','status','user_id','chambre','date_arrivee','date_depart')
admin.site.register(Reservation,ReservationAdmin)

#affichage payement
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('cin','capture','description','status','mode_payement','reservation')
admin.site.register(Payement,PaymentAdmin )

#affichage avis client
class AvisClientAdmin(admin.ModelAdmin):
    list_display = ('user','message','note','created_at')
admin.site.register(Avis,AvisClientAdmin )