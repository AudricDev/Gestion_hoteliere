from django.urls import path
from . import views

urlpatterns = [
    path('/',views.index,name='index'),
    path('',views.index,name='index'),
    path('inscription/',views.inscription,name='inscription'),
    path('login/',views.login,name='login'),
    path('connexion/',views.connexion,name='connexion'),
    path('deconnexion/',views.deconnexion,name='deconnexion'),
    path('admin/',views.listChambre,name="admin"),
    path('responsable/',views.responsable,name="responsable"),
    path('gestionUtilisateur/',views.gestionUtilisateur,name='gestionUtilisateur'),
    
    path('apropos/',views.apropos,name='apropos'),
    path('nosChambre/',views.nosChambre,name='nosChambre'),
    path('avisClient/',views.avisClient,name='avisClient'),
    path('detailChambre/<int:id>/',views.voirDetail,name='voirDetail'),
    path('ajoutChambre/',views.ajoutChambre,name='ajoutChambre'),
    path('supprimerChambre/<int:id>/',views.supprimerChambre,name='supprimer'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('gestionChambre/',views.gestionChambre,name='gestionChambre'),
    path('gestionReservation/',views.gestionReservation,name='gestionReservation'),

    path('reservation/<int:id>/',views.reserverChambre,name='reservation'),
    path('mesReservations/', views.mesReservations, name='mesReservations'),
    path('paiement/<int:reservation_id>/', views.paiement, name='paiement'),
    path('paiement-success/<int:reservation_id>/', views.paiement_success, name='paiement_success'),
    path("ajouter-avis/", views.ajouter_avis, name="ajouter_avis"),
    
    path("reservation/valider/<int:id>/",views.valider_reservation,name="valider_reservation"),
    path("reservation/refuser/<int:id>/",views.refuser_reservation,name="refuser_reservation"),
    
    path('gestionEquipement/',views.gestionEquipement,name='gestionEquipement'),
    path('ajoutEquipement/',views.ajoutEquipement,name='ajoutEquipement'),
    path('gestionMenage/',views.gestionMenage,name='gestionMenage'),
        
    path('supprimerEquipement/<int:id>/', views.supprimerEquipement, name='supprimerEquipement'),
    path('modifierChambre/<int:id>/', views.modifierChambre, name='modifierChambre'),

    path('ajout-photo-chambre/<int:id>/',views.ajoutPhotoChambre,name='ajoutPhotoChambre'),
    path('libererChambre/<int:id>/',views.libererChambre,name='libererChambre'),
    path('occuperChambre/<int:id>/',views.occuperChambre,name='occuperChambre')
]
