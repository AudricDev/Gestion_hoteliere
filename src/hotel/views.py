from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .models import *
from accounts.models import *
from django.contrib.auth import authenticate, login as auth_login,logout
from django.contrib import messages
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.db import transaction
from django.core.paginator import Paginator
import re

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
    contact_count = ContactMessage.objects.filter(lu=False).count()        
    return render (request,'gestionUtilisateur.html',{
        'users':user,
        'reservations':reservation,
        'chambre_dispo':chambre_dispo,
        'chambre_occupe':chambre_occupe,
        'contact_count':contact_count
        })

#modifier profil
@login_required
def update_profil(request):
    profil = request.user.user_profil
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        photo = request.FILES.get("photo")

        # Modifier User 
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        # Modifier User_profil
        profil.name = f"{first_name} {last_name}"

        if photo:
            profil.photo = photo
        profil.save()

        messages.success(request, "Profil mis à jour avec succès")
        return redirect(request.META.get('HTTP_REFERER'))
    
    if(user.user_profil.role == "Admin"):
        return redirect('dashboard')
    elif user.user_profil.role == "Responsable":
        return redirect('responsable')
    else:
        return redirect('index')
        
# affichage des chambre
def nosChambre(request):
    chambre = Chambre.objects.all()        
    return render(request,'nosChambre.html',{
        'chambres':chambre,
        })

# affichage des chambre
def avisClient(request):
    return render(request,'avisClient.html')

# affichage presentation de la plateform
def apropos(request):
    return render(request,'apropos.html')

# redirection contact
def contact(request):
    return render(request,'contact.html')

# envoie message contact
def contactMessage(request):
    if request.method == "POST":
        nom = request.POST.get("nom")
        email = request.POST.get("email")
        sujet = request.POST.get("sujet")
        message = request.POST.get("message")
        # Vérification simple
        if not all([nom, email, sujet, message]):
            messages.error(request, "Tous les champs sont obligatoires")
            return redirect("contact")

        # Sauvegarde en base
        ContactMessage.objects.create(
            nom=nom,
            email=email,
            sujet=sujet,
            message=message
        )

        messages.success(request, "Message envoyé avec succès 👍")
        return redirect("contact")
    return render(request, "contact.html")

#gestion contact
@login_required
def gestionContact(request):
    messages_list = ContactMessage.objects.all().order_by("-date_envoi")
    #pagination
    
    #10 messages par page
    paginator = Paginator(messages_list, 10)
    page_number = request.GET.get("page")
    messages_page = paginator.get_page(page_number)
    new_messages = ContactMessage.objects.filter(lu=False).count()
    return render(request, "gestionContact.html", {
        "messages_contact": messages_page,
        "new_messages": new_messages,
    })

# marque le message comme lu
def mark_contact_read(request, id):
    msg = get_object_or_404(ContactMessage, id=id)
    msg.lu = True
    msg.save()
    messages.success(request, "Message marqué comme lu")
    return redirect("gestionContact")

#supprimer message
def delete_contact(request, id):
    msg = get_object_or_404(ContactMessage, id=id)
    msg.delete()

    messages.success(request, "Message supprimé")
    return redirect("gestionContact")

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
        
        #Verification nom pour qu'il soit logique
        if len(set(first_name.lower())) == 1:
            messages.error(request, "Le nom saisi n'est pas valide")
            return redirect('inscription')

        #Verification nom pour qu'il soit logique
        if len(set(last_name.lower())) == 1:
            messages.error(request, "Le prenom saisi n'est pas valide")
            return redirect('inscription')

        #Verification nom pour qu'il soit logique
        if len(set(username.lower())) == 1:
            messages.error(request, "Le nom d'utilisateur saisi n'est pas valide")
            return redirect('inscription')
        
        # Vérification champs vides
        if not all([first_name, last_name, username, email, password1, password2]):
            messages.error(request, "Tous les champs sont obligatoires.")
            return redirect("inscription")

        # Vérification mot de passe
        if password1 != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect("inscription")

        if len(password1) < 8:
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
            return redirect("inscription")

        if not re.search(r'[A-Z]', password1):
            messages.error(request, "Le mot de passe doit contenir au moins une majuscule.")
            return redirect("inscription")
        
        if not re.search(r'[a-z]', password1):
            messages.error(request, "Le mot de passe doit contenir au moins une minuscule.")
            return redirect("inscription")

        if not re.search(r'[0-9]', password1):
            messages.error(request, "Le mot de passe doit contenir au moins un chiffre.")
            return redirect("inscription")
        
        # Vérification username
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur existe déjà.")
            return redirect("inscription")

        # Vérification email
        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return redirect("inscription")

        if not re.search(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9]+\.com$', email):
            messages.error(request, "Cet email ne pas valide.")
            return redirect("inscription")
        try:
            with transaction.atomic():
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
            messages.success(request, "Compte créé avec succès.")
            auth_login(request,user)
            return redirect("index")
        except Exception:
            messages.error(request, "Une erreur est survenue.")
            return redirect("inscription")
    return render(request, "inscription.html")

#formulaire d'inscription
def ajoutUtilisateur(request):
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
            return redirect('gestionUtilisateur')
        messages.error(request, "Les mots de passe ne correspondent pas")
        return redirect('gestionUtilisateur')
    return render(request, 'gestionUtilisateur.html')

#modifier utilisateur
def modifierUtilisateur(request,id):
    user = User.objects.get(id=id)
    if request.method == "POST":
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        user.user_profil.role = request.POST.get("role")
        user.save()
        user.user_profil.save()
    return redirect('gestionUtilisateur')


#supprimer utilisateur
def supprimerUtilisateur(request,id):
    utilisateur = get_object_or_404(User,id=id)
    utilisateur.delete()
    return redirect('gestionUtilisateur')

#cherche utilisateur
def chercherUtilisateur(request):
    data_input = request.GET.get("search")
    chambre_dispo = Chambre.objects.filter(status='Disponible').count()
    chambre_occupe = Chambre.objects.filter(status='Non disponible').count()
    reservation = Reservation.objects.all()
    contact_count = ContactMessage.objects.filter(lu=False).count()        
    resultat = User.objects.filter(
        Q(username__icontains = data_input) | 
        Q(first_name__icontains = data_input)|
        Q(email__icontains = data_input) | 
        Q(last_name__icontains = data_input)
        )
    context = {
        'users' : resultat,
        'chambre_dispo':chambre_dispo, 
        'chambre_occupe':chambre_occupe, 
        'reservations':reservation,
        'contact_count':contact_count
    }
    return render(request,'gestionUtilisateur.html',context)  

#tabeau de board
from .models import Reservation, Chambre, ContactMessage

def dashboard(request):
    reservations = Reservation.objects.all()
    chambre_dispo = Chambre.objects.filter(status='Disponible').count()
    chambre_occupe = Chambre.objects.filter(status='Non disponible').count()
    contact_count = ContactMessage.objects.filter(lu=False).count()
    return render(request, "dashboard.html", {
        "reservations": reservations,
        "chambre_dispo": chambre_dispo,
        "chambre_occupe": chambre_occupe,
        "contact_count": contact_count
    })

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
    contact_count = ContactMessage.objects.filter(lu=False).count()    
    return render (request,'gestionChambre.html',{
        'chambre':chambre,
        'hotels':hotels,
        'types': types,
        'chambre_dispo':chambre_dispo,
        'reservations':reservation,
        'chambre_occupe':chambre_occupe,
        "contact_count": contact_count
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

#Rechercher chambre
def chercherChambre(request):
    data_input = request.GET.get("search")
    chambre_dispo = Chambre.objects.filter(status='Disponible').count()
    chambre_occupe = Chambre.objects.filter(status='Non disponible').count()
    reservation = Reservation.objects.all()
    contact_count = ContactMessage.objects.filter(lu=False).count()
    resultat = Chambre.objects.filter(
        Q(titre__icontains = data_input) | 
        Q(status__icontains = data_input)
        )
    context = {
        'chambre' : resultat,
        'chambre_dispo':chambre_dispo, 
        'chambre_occupe':chambre_occupe, 
        'reservations':reservation,
        "contact_count": contact_count 
    }
    return render(request,'gestionChambre.html',context)  

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
    contact_count = ContactMessage.objects.filter(lu=False).count()    
    return render (request,'gestionReservation.html',{
        'chambre':chambre,
        'hotels':hotels,
        'types': types,
        'chambre_dispo':chambre_dispo,
        'reservations':reservation,
        'chambre_occupe':chambre_occupe,
        'contact_count':contact_count

        })

#Reservation 
def reserverChambre(request, id):

    # Vérification connexion
    if not request.user.is_authenticated:
        return redirect('login')

    chambre = get_object_or_404(Chambre, id=id)
    if request.method == "POST":
        date_arrivee = parse_datetime(request.POST.get("date_arrivee"))
        date_depart = parse_datetime(request.POST.get("date_depart"))
        date_reservations = timezone.now()
        nbr_pers = request.POST.get("nbr_pers")

        # Conversion timezone
        if date_arrivee:
            date_arrivee = timezone.make_aware(date_arrivee)
        if date_depart:
            date_depart = timezone.make_aware(date_depart)

        # Vérification format date
        if not date_arrivee or not date_depart:
            messages.error(request, "Dates invalides.")
            return render(request, "reservation.html", {
                "chambre": chambre
            })

        # Vérification logique des dates
        if date_arrivee < timezone.now():
            messages.error(
                request,
                "La date d'arrivée ne peut pas être dans le passé."
            )
            return render(request, "reservation.html", {
                "chambre": chambre
            })

        if date_depart <= date_arrivee:
            messages.error(
                request,
                "La date de départ doit être après la date d'arrivée."
            )
            return render(request, "reservation.html", {
                "chambre": chambre
            })

        # Vérification disponibilité chambre
        conflit = Reservation.objects.filter(
            chambre=chambre,
            date_arrivee__lt=date_depart,
            date_depart__gt=date_arrivee,
            status__in=["En attente de validation", "Validé"]
        ).exists()
        if conflit:
            messages.error(
                request,
                "Cette chambre est déjà réservée pendant cette période."
            )
            return render(request, "reservation.html", {
                "chambre": chambre
            })

        # Calcul du nombre de nuits
        nuits = (date_depart - date_arrivee).days

        if nuits <= 0:
            nuits = 1

        total = chambre.prix * nuits

        # Création réservation
        reservation = Reservation.objects.create(
            nbr_pers=nbr_pers,
            prix_total=total,
            user_id=request.user,
            chambre=chambre,
            date_arrivee=date_arrivee,
            date_depart=date_depart,
            date_reservation=date_reservations,
            status="En attente de validation"
        )

        # Redirection vers paiement
        return redirect(
            'paiement',
            reservation_id=reservation.id
        )

    return render(request, "reservation.html", {
        "chambre": chambre
    })

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
        if request.POST.get("mode_payement") == "Espèce":
            return redirect('mesReservations', reservation.id)
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
    contact_count = ContactMessage.objects.filter(lu=False).count()        
    return render (request,'gestionEquipement.html',{
        'equipements':equipement,
        'chambre_dispo':chambre_dispo,
        'chambre_occupe':chambre_occupe,
        'reservations':reservation,
        'contact_count':contact_count
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

#modification equipement
#modification chambre
def modifierEquipement(request, id):
    equipement = Equipement.objects.get(id=id)    
    if request.method == "POST":
        equipement.title = request.POST.get("title")
        equipement.description = request.POST.get("description")
        equipement.image = request.POST.get("image")
        equipement.save()
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