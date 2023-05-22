On ouvre la photo LIGNE_NB sur paint pour avoir ses coordonnées en pixel, et on calcule nous-même à la main l'équation de la droite dans le repère de l'image
Le but est de connaître le résultat pour voir si l'algorithme ne fait pas n'importe quoi


===============================================
NOTE IMPORTANTE :
Le repère : x vers la droite, y vers le bas, les repères d'images sur python et image sont les mêmes
===============================================
![ligne](https://github.com/hacktivist25/ballTracking/assets/125929174/8ee5481b-38cc-4e5d-a863-20aced7b4acb)
pixels des extrémités :
- Un pixel en   (1036 ; 896)
- l'autre en    (2790 ; 938)

a= \frac{ y2-y1 }{ x2-x1 }
 = \frac{ 938 - 896 }/{ 2790 - 1036 }
 = 0,0239

b=y2-ax2
 = 938 - 0,0239*2790
 = 871,2

----------------------------------------------------------------
l'équation doit être 0.0239x + 871.2 dans le repère de l'image
----------------------------------------------------------------
on va voir ce que renvoie l'algorithme que l'on a élaboré pour différentes résolutions angulaires et de distance : 
Tout d'abord, l'image de base déjà montrée au dessus est soumis à l'algorithme.
L'algorithme la transforme en noir et blanc et prend les contours avec un seuillage automatique sur un filtre de canny :

![ligne NB](https://github.com/hacktivist25/ballTracking/assets/125929174/13e767e5-f338-47de-9625-d04c508b7a22)



Une fois la transformée de Hough faite, on obtient rho et theta comme suit : en traçant un plan de hough qui utilise l'équation suivante :

<img width="508" alt="Principe hough" src="https://github.com/hacktivist25/ballTracking/assets/125929174/1620bebb-d5fd-447a-9c3f-de50598e0162">

nous utilisons cela dans l'équation y = -cos(theta)/sin(theta) x + rho / sin(theta), on on trouve l'équation de la droite ainsi :

Voici quelques tests : tout d'abord avec une résolution en distance de 1 pour 1, et une résolution angulaire d'1° :
![plan de hough reperage max](https://github.com/hacktivist25/ballTracking/assets/125929174/ea53bd0a-e7a0-49d4-a89d-3df8f85f1ae4)
![droite reconnue](https://github.com/hacktivist25/ballTracking/assets/125929174/471c3aa3-9360-4df5-bec8-a7f5736f51d5)
![rendu](https://github.com/hacktivist25/ballTracking/assets/125929174/57457367-89e9-4559-89e3-f6f84e3c0057)

Cette fois : distance 4 pour 1, 0.1° de résolution angulaire :
![plan hough reperage max](https://github.com/hacktivist25/ballTracking/assets/125929174/abf96d39-29aa-4e34-9c9f-fe83391898e9)
![droite reconnue](https://github.com/hacktivist25/ballTracking/assets/125929174/d6f479f2-f502-495a-932a-5499355673af)
![rendu](https://github.com/hacktivist25/ballTracking/assets/125929174/c39291bd-f4bf-42b2-b30d-efc9aacf663b)

puis 4 pour 1 en distance, 1° en résolution angulaire :
![plan de hough avec reperage du max](https://github.com/hacktivist25/ballTracking/assets/125929174/ff90890d-186d-4668-a735-19fd0c0504c8)
![droite trouvee](https://github.com/hacktivist25/ballTracking/assets/125929174/2b132c6e-0ece-405e-ae71-e7fe169b12e0)
![rendu](https://github.com/hacktivist25/ballTracking/assets/125929174/e37097dd-0618-4c10-994e-d0e6efec54b2)


Cela marche pour deux droites sous certaines conditions :
Prenons cette image :
![blablabla](https://github.com/hacktivist25/ballTracking/assets/125929174/62a7f9d5-cc56-4772-aaa4-71627593616a)
Le repère que l'on veut (les axes x et y) peuvent ne pas être détectés : le rebord de la feuille peut par exemple passer pour une droite, et l'algorithme peut prendre ce rebord de feuille comme un de nos axes, et pas le petit vecteur pour le repère... 
Après BEAUCOUP de recherches et de tests, nous n'avons pas réussi à le corriger : La méthode la plus prometteuse était celle-ci : 
En dessinant des flèches épaisses et en appliquant une opération de fermeture (on dilate l'image puis on l'érode), on aurait pu obtenir un gros trait blanc pour nos axes, vu l'allure qu'il ont ci dessous :
![transformation_Canny](https://github.com/hacktivist25/ballTracking/assets/125929174/eb9cb2bd-af74-4522-a8aa-82e248e62cb8)
Les axes auraient étés "remplis" de blanc (points d'intére^ts, et ceux-ci auraint produit dur le plan de hough non pas un maxima "ponctuel", mais une pléthode de valeurs hautes sur une zone circulaire réduite : aunso, au lieu de chercher le max/le point qui a eu le plus de votes, on cherche la zone ou la moyenne des votes sur une aire sirculaire réduite est la plus haute : ça n'a pas fonctionné comme souhaité, en plus d'alourdir considérablement les calculs
Ont doit donc contrôler l'environnement pour que l'on aie une transformée de canny commme ci dessus, sans que les bords de la feuille ne soient détectés, grâce à un bon seuillage.

Maitenant, on remarque que les droites du repère sont dédoublées, car l'épaisseur du repère tracé au stylo n'est pas nulle : 
Pour ne pas qu'il détecte deux droites parallèles et côte à côte, il suffit de chercher deux maxima qui aient une certaine distance l'un de l'autre sur le plan de hough : une distance/norme supérieur à 20 entre les coordonnées des deux points suffit pour ne pas capter deux fois la même droite décalée
Cela donne donc ceci :
![Hough Droites](https://github.com/hacktivist25/ballTracking/assets/125929174/bbb36285-f46d-4e3c-897c-3d945812ba33)

On trouve bien deux maximas éloignés l'un de l'autre : reste à effectuer les transformations habituelles et dessiner les droites trouvées sur l'image brute pour voir si les coefficients sont bons : on obtient alors ceci
![droites](https://github.com/hacktivist25/ballTracking/assets/125929174/8bed9042-a510-4381-922e-a9b10ba04093)
Les droites collent bien au repère

Maintenant on peut se lancer sur la transformée de Hough pour trouver un cercle de rayon inconnu




