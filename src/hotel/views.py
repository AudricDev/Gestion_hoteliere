from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .models import *
from accounts.models import *
from django.contrib.auth import authenticate, login as auth_login,logout
from django.contrib import messages
from django.utils.dateparse import parse_datetime
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    chambre = Chambre.objects.all()
    avis = Avis.objects.select_related("user").order_by("-id")
    return render(request,'layouts/index.html',{
        'chambres':chambre,
        "avis": avis
        })

#gestionUtilisateur
def gestionUtilisateur(request):
    if not request.user.is_authenticated:
        return redirect('login')
    reservation = Reservation.objects.all()
    user = User.objects.all()
    chambre_dispo = Chambre.objects.filter(status='Disponible').count()
    chambre_occupe = Chambre.objects.filter(status='Non disponible').count()
    return render (request,'gestionUtilisateur.html',{
        'users':user,
        'reservations':reservation,
        'chambre_dispo':chambre_dispo,
        'chambre_occupe':chambre_occupe
        })
    
# affichage des chambre
def nosChambre(request):
    chambre = Chambre.objects.all()
    return render(request,'nosChambre.html',{'chambres':chambre})

# affichage des chambre
def avisClient(request):
    return render(request,'avisClient.html')

# affichage presentation de la plateform
def apropos(request):
    return render(request,'apropos.html')

# affichage des chambre
def responsable(request):
    if not request.user.is_authenticated:
        return redirect('login')
    reservation = Reservation.objects.all()
    chambre = Chambre.objects.all()
    hotels = Hotel.objects.all()
    types = Type_chambre.objects.all()
    chambre_dispo = Chambre.objects.filter(status='Disponible').count()
    chambre_occupe = Chambre.objects.filter(status='Non disponible').count()
    chambre = Chambre.objects.all()
    return render(request,'responsable.html',{
        'chambres':chambre,
        'hotels':hotels,
        'types': types,
        'reservations': reservation,
        'chambre_dispo':chambre_dispo,
        'chambre_occupe':chambre_occupe
        })

# voir les details du chambre
def voirDetail(request,id):
    detail = Chambre.objects.filter(id=id).first()
    if detail:
        return render(request,'detailChambre.html',{'details':detail})
    else:
        return render(request,'404.html')
    
#connexion
def connexion(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            # ROLE
            try:
                profil = user.user_profil.role
            except:
                profil = "User"
            if profil == "Admin":
                return redirect("admin")
            elif profil == "Responsable":
                return redirect("responsable")
            else:
                return redirect("index")  # ou accueil
        else:
            messages.error(request, "Identifiants incorrects")
    return render(request, "login.html")

#deconnexion
def deconnexion(request):
    logout(request)
    return redirect('login')

#login
def login(request):
    return render(request,'login.html')

#formulaire d'inscription
def inscription(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 == password2:
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password1
            )
            User_profil.objects.create(
                user=user,
                name=f"{first_name} {last_name}",
                role="User"
            )
            return redirect('login')
        messages.error(request, "Les mots de passe ne correspondent pas")
        return redirect('inscription')
    return render(request, 'inscription.html')

#tabeau de board
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    reservation = Reservation.objects.all()
    chambre_dispo = Chambre.objects.filter(status='Disponible').count()
    chambre_occupe = Chambre.objects.filter(status='Non disponible').count()
    return render(request,'dashboard.html',{
        'chambre_dispo':chambre_dispo,
        'reservations':reservation,
        'chambre_occupe':chambre_occupe
        }
)

#gestionChambre
def gestionChambre(request):
    if not request.user.is_authenticated:
        return redirect('login')
    reservation = Reservation.objects.all()
    chambre = Chambre.objects.all()
    hotels = Hotel.objects.all()
    types = Type_chambre.objects.all()
    chambre_dispo = Chambre.objects.filter(status='Disponible').count()
    chambre_occupe = Chambre.objects.filter(status='Non disponible').count()
    return render (request,'gestionChambre.html',{
        'chambre':chambre,
        'hotels':hotels,
        'types': types,
        'chambre_dispo':chambre_dispo,
        'reservations':reservation,
        'chambre_occupe':chambre_occupe
        })

# read chambre
def listChambre(request):
    chambre = Chambre.objects.all()
    hotels = Hotel.objects.all()
    types = Type_chambre.objects.all()
    return render (request,'admin.html',{
        'chambre':chambre,
        'hotels':hotels,
        "types": types
        })

# ajout chambre
def ajoutChambre(request):
    chambre = Chambre.objects.all()
    chambre_dispo = Chambre.objects.filter(status='Disponible').count()
    chambre_occupe = Chambre.objects.filter(status='Non disponible').count()
    if request.method == "POST":
        type_chambre = Type_chambre.objects.get(
            id=request.POST.get("type_chambre")
        )

        hotel = Hotel.objects.get(
            id=request.POST.get("hotel")
        )

        Chambre.objects.create(
            type_chambre=type_chambre,
            titre=request.POST.get("titre"),
            status=request.POST.get("status"),
            prix=request.POST.get("prix"),
            nbr_personne=request.POST.get("nbr_pers"),
            hotel=hotel
        )
    return render(request,'gestionChambre.html',{
        'chambre':chambre,
        'chambre_dispo':chambre_dispo,
        'chambre_occupe':chambre_occupe
        })

#supprimer chambre
def supprimerChambre(request,id):
    chambre = get_object_or_404(Chambre,id=id)
    chambre.delete()
    return redirect('gestionChambre')

#modification chambre
def modifierChambre(request, id):
    chambre = Chambre.objects.get(id=id)
    
    if request.method == "POST":
        chambre.hotel_id = request.POST.get("hotel")
        chambre.titre = request.POST.get("titre")
        chambre.type_chambre_id = request.POST.get("type_chambre")
        chambre.status = request.POST.get("status")
        chambre.nbr_personne = request.POST.get("nbr_pers")
        chambre.prix = request.POST.get("prix")
        chambre.save()
        return redirect('gestionChambre')
    
#gestionReservation
def gestionReservation(request):
    if not request.user.is_authenticated:
        return redirect('login')
    reservation = Reservation.objects.all()
    chambre = Chambre.objects.all()
    hotels = Hotel.objects.all()
    types = Type_chambre.objects.all()
    chambre_dispo = Chambre.objects.filter(status='Disponible').count()
    chambre_occupe = Chambre.objects.filter(status='Non disponible').count()
    return render (request,'gestionReservation.html',{
        'chambre':chambre,
        'hotels':hotels,
        'types': types,
        'chambre_dispo':chambre_dispo,
        'reservations':reservation,
        'chambre_occupe':chambre_occupe
        })

#Reservation 


def reserverChambre(request, id):
    if not request.user.is_authenticated:
        return redirect('login')
    chambre = get_object_or_404(Chambre, id=id)
    if request.method == "POST":
        date_arrivee = parse_datetime(request.POST.get("date_arrivee"))
        date_depart = parse_datetime(request.POST.get("date_depart"))
        nbr_pers = request.POST.get("nbr_pers")

        # sécurité dates
        if not date_arrivee or not date_depart:
            return render(request, "reservation.html", {
                "chambre": chambre,
                "error": "Dates invalides"
            })

        # calcul nuits
        nuits = (date_depart - date_arrivee).days
        if nuits <= 0:
            nuits = 1

        total = chambre.prix * nuits

        # création réservation
        reservation = Reservation.objects.create(
            nbr_pers=nbr_pers,
            prix_total=total,
            user_id=request.user,
            chambre=chambre,
            date_arrivee=date_arrivee,
            date_depart=date_depart,
            status="En attente de validation"
        )
        # REDIRECTION VERS PAIEMENT sady maka ny id anle reservation
        return redirect('paiement', reservation_id=reservation.id)
    return render(request, "reservation.html", {"chambre": chambre})

#liste reservation pour l'utilisateur
def mesReservations(request):
    if not request.user.is_authenticated:
        return redirect('login')

    reservations = Reservation.objects.filter(user_id=request.user).order_by("-id")

    return render(request, "mesReservations.html", {
        "reservations": reservations
    })
    
# Valider réservation
def valider_reservation(request, id):
    reservation = get_object_or_404(Reservation, id=id)

    if (
        reservation.payement.status == "Non payé"
        and reservation.status == "En attente de validation"
    ):
        # Paiement
        reservation.payement.status = "Payé"
        reservation.payement.save()

        # Réservation
        reservation.status = "Validé"
        reservation.save()

        # Chambre
        reservation.chambre.status = "Non disponible"
        reservation.chambre.save()

    return redirect("gestionReservation")
    
#refuser réservation
def refuser_reservation(request, id):
    reservation = get_object_or_404(Reservation, id=id)

    if reservation.status == "En attente de validation":
        reservation.status = "Refusé"
        reservation.save()

    return redirect("gestionReservation")
    
#Paiement
def paiement(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    if request.method == "POST":
        Payement.objects.create(
            reservation=reservation,
            cin=request.POST.get("cin"),
            description=request.POST.get("description"),
            mode_payement=request.POST.get("mode_payement"),
            capture=request.FILES.get("capture"),
            status="Non payé"
        )
        return redirect('paiement_success', reservation.id)

    return render(request, "formPaiement.html", {
        "reservation": reservation
    })

#Paiement success
def paiement_success(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    return render(request, "paiement_success.html", {
        "reservation": reservation
    })
    
#gestionEquipement
def gestionEquipement(request):
    if not request.user.is_authenticated:
        return redirect('login')
    reservation = Reservation.objects.all()
    equipement = Equipement.objects.all()
    chambre_dispo = Chambre.objects.filter(status='Disponible').count()
    chambre_occupe = Chambre.objects.filter(status='Non disponible').count()
    return render (request,'gestionEquipement.html',{
        'equipements':equipement,
        'chambre_dispo':chambre_dispo,
        'chambre_occupe':chambre_occupe,
        'reservations':reservation
        })

#gestionMenage
def gestionMenage(request):
    if not request.user.is_authenticated:
        return redirect('login')
    reservation = Reservation.objects.all()
    chambre = Chambre.objects.all()
    hotels = Hotel.objects.all()
    types = Type_chambre.objects.all()
    chambre_dispo = Chambre.objects.filter(status='Disponible').count()
    chambre_occupe = Chambre.objects.filter(status='Non disponible').count()
    return render (request,'gestionMenage.html',{
        'chambre':chambre,
        'hotels':hotels,
        'types': types,
        'chambre_dispo':chambre_dispo,
        'reservations':reservation,
        'chambre_occupe':chambre_occupe
        })

#liberer la chambre selectionnéé
def libererChambre(request,id):
    chambre = get_object_or_404(Chambre,id=id)
    chambre.status = "Disponible"
    chambre.save()
    return redirect('gestionMenage')

#occuper la chambre selectionnéé
def occuperChambre(request,id):
    chambre = get_object_or_404(Chambre,id=id)
    chambre.status = "Non disponible"
    chambre.save()
    return redirect('gestionMenage')

#AjoutEquipement
def ajoutEquipement(request):
    equipement= Equipement.objects.all()
    if request.method == "POST":
        Equipement.objects.create(
            title = request.POST.get("titre"),
            description = request.POST.get("description"),
            image = request.FILES.get("image")
        )
    return render(request, 'gestionEquipement.html',{'equipements':equipement})

#supprimer equiment
def supprimerEquipement(request,id):
    equipement = get_object_or_404(Equipement,id=id)
    equipement.delete()
    return redirect('gestionEquipement')

#ajouter photo dans chambre photo
def ajoutPhotoChambre(request, id):
    chambre = Chambre.objects.get(id=id)
    if request.method == "POST":
        Chambre_photo.objects.create(
            chambre = chambre,
            name = request.POST.get("name"),
            image = request.FILES.get("image")
        )
    return redirect('gestionChambre')

#AVIS CLIENT
def avisClient(request):
    avis = Avis.objects.select_related("user").order_by("-id")
    return render(request, "avisClient.html", {
        "avis": avis
    })

#ajout avis

@login_required
def ajouter_avis(request):
    if request.method == "POST":
        message = request.POST.get("message")
        note = request.POST.get("note")
        Avis.objects.create(
            user=request.user,
            message=message,
            note=note
        )
        return redirect("avisClient")
    return render(request, "ajouterAvis.html")