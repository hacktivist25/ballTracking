On ouvre la photo LIGNE_NB sur paint pour avoir ses coordonnées en pixel, et on calcule nous-même à la main l'équation de la droite dans le repère de l'image
Le but est de connaître le résultat pour voir si l'algorithme ne fait pas n'importe quoi




NOTE IMPORTANTE :
Le repère : x vers la droite, y vers le bas, les repères d'images sur python et image sont les mêmes : l'origine se situe tout en haut à gauche de l'image

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





Fonctionnement de la transformée de Hough : [1]
Au lieu de rester dnas un repère cartésien standard qui poserait des soucis de calculs pour le coefficient directeur d'une droite quasiment verticale, et qui nécessiterai une mémoire trop grande, on passe dans un autre repère qui s'affranchi de ces contraintes 

![représentation](https://github.com/hacktivist25/ballTracking/assets/125929174/9996d755-cf6f-4159-a651-5bf480d9f6ee)

Le repère de hough possède en abscisse et en ordonnées non pas x et y, mais thetoa et rho
On voit que theta est l'angle que forme se segment perpendiculaire à la droite reliant deux points, et passant pas l'origine, avec l'axe des abscisses de l'image (x), et rho représente la longueur du segment précédent
Ces valeurs seront reportées sur ce que l'on appelle plan de Hough

On obtient un plan de hough en apppliquant l'algorithme suivant :
Pour chaque point d'intérêt (qui est un point de contour, trouvé par un filtrage de canny) :
1-Fare passer des droites par ce point, dans toutes les directions (faire varier theta de 0 à 180°
2-Calculer le rho correspondant à chaque fois, à l'aide de la formule de changement de repère [2] :

![equa de base](https://github.com/hacktivist25/ballTracking/assets/125929174/ba059c49-816b-48e6-bb4e-31d5baab5d81)
  
3-Placer le point (theta, rho) sur le plan
   
   
   
 Une fois cela fait, le plan de hough devrait ressembler à quelque chose comme cela :
 
 ![plan Hough](https://github.com/hacktivist25/ballTracking/assets/125929174/e1ef9c5d-9ce2-44f3-a5ce-d1d6e487ed46)
 
 Le point le plus blanc, c'est à dire celui sur lequel beaucoup de droites passent/pour lequel beaucoup de points ont cette coordonnée en commun, est un maximum, et est l'endroit sur le plan de hough où il est probable qu'il y aie une droite sur le plan cartésien
 On récupère alors les coordonnées de ce point maximal, et on est capable d'en donner l'équation dans le plan cartésien avec la transformée inverse [2]:
 
 ![equa inverse](https://github.com/hacktivist25/ballTracking/assets/125929174/0512534d-becd-4da3-9f03-67bd13e69422)

 De là, on obtient notre équation, avec des coefficients en pixels, pour notre plan d'image : on s'occupera de la conversion en distance réalle plus tard



Pour faire tout cela, il faut tout d'abord détecter les contours : On utilise pour cela le filtre de Canny :
On prend d'abord une photo avec l'appareil photo de la caméra RaspberryPi Model4B dont voici quelques specs : [4] Nous avons un model v2 : deuxième colonne

![Picamera Module V2](https://github.com/hacktivist25/ballTracking/assets/125929174/86944bda-2170-4753-8654-5de31a99d428)

On retiendra pour le moment qu'elle prend des photos de résolution 3280 px / 1845 px
Les photos sont en format RGB
On commence par binariser le format pour avoir une image en niveaux de gris (grayscaling)
Ensuite, la détextion de bords se fait en recherchant les gradients de l'image : UN gradient renvoie une valeur vectorielle qui point vers la direction de l'image à partir d'un point telle que la variation de niveau de gris soit la plus forte dans la direction : voilà ce qu'est un gradient, et il permet en effet de détecter les bords, car les bords desobjets marquent une transition brutale avec un autre objet, un fond... [5]
Nous utilisons une fonction toute faite dnas la bibliothèque openCV


Voyons ce que cela donne pour le moment :

Tout d'abord, l'image de base déjà montrée au dessus est soumis à l'algorithme.
L'algorithme la transforme en noir et blanc et prend les contours avec un seuillage automatique sur un filtre de canny :

![ligne NB](https://github.com/hacktivist25/ballTracking/assets/125929174/13e767e5-f338-47de-9625-d04c508b7a22)

On construit ensuite le fameux plan de hough avec une matrice accumulatrice : 
On initialise une matrice avec une taille pouvant accueillir toutes les coordonnées possibles de droites dnas l'image : 
Theta varie de 0 à 180°, et la distance entre l'origine du repère (le point tout en haut à gauche de l'image) maximale est de la taille de la diagonale de l'image, c'est à dire  D = sqrt(3280² + 1845²)
La matrice accumulatrice est donc de taille Dx180
Et pour chaque point auquel on applique la transformée (LIGNE 41), on incrémente de 1 l'élément de la matrice accumulatrice [rho,theta] (on appelle cela un vote pour un point/une coordonnée) : on trouvera ainsi les maximas, c'est à dire les points (rho,theta) du plan de hought pour lesquels le plus de points d'intérêts peuvent passer
Cetta matrice a aussi le bon goût de pouvoir réduire sa taille suivant si l'on veut optimiser le temps de calcul en sacrifiant un peu de précision : on peut créer une matrice accumulatrice deux fois plus petite, pour cela il suffit de ne s'intéresser qu'à un point sur quatre de l'image en noir et blanc



Voici quelques tests : tout d'abord avec une résolution en distance de 1 pour 1, et une résolution angulaire d'1° : C'est à dire que lors de la transformation de Hough (LIGNE 41), on fait varier theta d'un degré.
![plan de hough reperage max](https://github.com/hacktivist25/ballTracking/assets/125929174/ea53bd0a-e7a0-49d4-a89d-3df8f85f1ae4)

On a notre plan de hough tracé (on représente la matrice accumulatrice sous forme d'image), et on repère le maximum global de la matrice accumulatrice (rectangle gris) et on a alors les "coordonnées de la droite" dans le plan de hough, et de là on peut se servir de la transformée inverse (LIGNE 54)
![droite reconnue](https://github.com/hacktivist25/ballTracking/assets/125929174/471c3aa3-9360-4df5-bec8-a7f5736f51d5)

On trouve alors cette droite, que l'on transpose sur l'image brute de la caméra
![rendu](https://github.com/hacktivist25/ballTracking/assets/125929174/57457367-89e9-4559-89e3-f6f84e3c0057)




Cette fois : distance 4 pour 1, 0.1° de résolution angulaire : 
![plan hough reperage max](https://github.com/hacktivist25/ballTracking/assets/125929174/abf96d39-29aa-4e34-9c9f-fe83391898e9)
![droite reconnue](https://github.com/hacktivist25/ballTracking/assets/125929174/d6f479f2-f502-495a-932a-5499355673af)
![rendu](https://github.com/hacktivist25/ballTracking/assets/125929174/c39291bd-f4bf-42b2-b30d-efc9aacf663b)




puis 4 pour 1 en distance, 1° en résolution angulaire :
![plan de hough avec reperage du max](https://github.com/hacktivist25/ballTracking/assets/125929174/ff90890d-186d-4668-a735-19fd0c0504c8)
![droite trouvee](https://github.com/hacktivist25/ballTracking/assets/125929174/2b132c6e-0ece-405e-ae71-e7fe169b12e0)
![rendu](https://github.com/hacktivist25/ballTracking/assets/125929174/e37097dd-0618-4c10-994e-d0e6efec54b2)


Malgré que les coefficients semblent un peu éloignés de ceux que l'on doivent trouver en ligne24, la précision à l'oeil reste satisfaisante : bien évidemment, le traitement avec un pas de rotation de 0.1° lors de la transformaée onduit à des résultats plus précis, mais qui prennent bien plus de temps
Même avec la configuration la plus rapide, le temps d'exécution reste si lent qu'on est bien loin de s'approcher du temps réel... (Màj : on aurait dû utiliser C qui tuilise moins de ressources, et exploiter le multithreading...)



Cela marche pour deux droites sous certaines conditions :
Prenons cette image :
![blablabla](https://github.com/hacktivist25/ballTracking/assets/125929174/62a7f9d5-cc56-4772-aaa4-71627593616a)

Le repère que l'on veut (les axes x et y) peuvent ne pas être détectés : le rebord de la feuille peut par exemple passer pour une droite, et l'algorithme peut prendre ce rebord de feuille comme un de nos axes, et pas le petit vecteur pour le repère... 
Après BEAUCOUP de recherches et de tests, nous n'avons pas réussi à le corriger : La méthode la plus prometteuse était celle-ci : 
En dessinant des flèches épaisses pour le repère et en appliquant une opération de fermeture (on dilate l'image puis on l'érode), on aurait pu obtenir un gros trait blanc pour nos axes, vu l'allure qu'ils ont ci dessous :
![transformation_Canny](https://github.com/hacktivist25/ballTracking/assets/125929174/eb9cb2bd-af74-4522-a8aa-82e248e62cb8)

Les axes auraient étés "remplis" de blanc (points d'intérêts, et ceux-ci auraint produit sur le plan de hough non pas un maxima "ponctuel", mais un ensemble de valeurs "hautes"/beaucoup votées sur une zone circulaire réduite : aunso, au lieu de chercher le max/le point qui a eu le plus de votes, on cherche la zone ou la moyenne des votes sur une aire sirculaire réduite est la plus haute : ça n'a pas fonctionné comme souhaité, en plus d'alourdir considérablement les calculs
Ont doit donc contrôler l'environnement pour que l'on aie une transformée de canny commme ci dessus, sans que les bords de la feuille ne soient détectés, grâce à un bon seuillage.

Maitenant, on remarque que les droites du repère sont dédoublées, car l'épaisseur du repère tracé au stylo n'est pas nulle : 
Pour ne pas qu'il détecte deux droites parallèles et côte à côte, il suffit de chercher deux maxima qui aient une certaine distance l'un de l'autre sur le plan de hough : une distance/norme supérieur à 20 entre les coordonnées des deux points suffit pour ne pas capter deux fois la même droite décalée
Cela donne donc ceci :
![Hough Droites](https://github.com/hacktivist25/ballTracking/assets/125929174/bbb36285-f46d-4e3c-897c-3d945812ba33)

On trouve bien deux maximas éloignés l'un de l'autre : reste à effectuer les transformations habituelles et dessiner les droites trouvées sur l'image brute pour voir si les coefficients sont bons : on obtient alors ceci
![droites](https://github.com/hacktivist25/ballTracking/assets/125929174/8bed9042-a510-4381-922e-a9b10ba04093)
![equaDroites](https://github.com/hacktivist25/ballTracking/assets/125929174/52d347fa-9c94-4f99-ac3d-c998f83ea64c)



Les droites collent bien au repère


Maintenant on peut se lancer sur la transformée de Hough pour trouver un cercle de rayon inconnu :
Le principe est le même [6],[7]
Sauf que l'on peut garde le plan x,y : plus besoin de faire des transformées en (rho, theta)

On commence déjà par l'aver l'ancienne image des droites que l'on a trouvé pour ne pas perturber le futur processus de détection de cercle : on otient alors ceci :
![cannySansLignes](https://github.com/hacktivist25/ballTracking/assets/125929174/3dfaed0c-693a-4603-b84b-e8b4ca1beb65)

On s'est débarassé des deux lignes du repère :
En principe, les points blancs que l'on voit sont dû aux ombres de l'image initialse : mais ils ressembelent  un bruit poivre et sel, on pourrait donc en principe les traiter en convoluant l'image avec un filtre moyenneur ou Gaussien, snas que le flou apporté par le proessus ne soit excessivement gênant pour la détextion de cercle... Mais comme une opération si simpl en python mange du temps processeur, nous ne le ferons pas.

![Capture d’écran 2023-05-22 141347](https://github.com/hacktivist25/ballTracking/assets/125929174/118f588b-2ded-4cd1-9eb8-3f5a8f097163)

On garde le repère cartésien standard, et pour chaque point d'intérêt/de contour, on dessine un cercle autour de ce point
On le fait pour des rayons de cercle de plus en plus grand
On sauvegarde tout cela dnas une grosse matrice accumulatrice en trois dimension : la même dimension que l'image, dupliquée auta nt de fois qu'il y a de rayons possibles détectables, en fonction de la précision que l'on souhaite y apporter
On remarque alors que si les cercles que l'on dessine autour des points d'intérêt ont le même rayon que le cercle préssuposé où ces points se situent, ils s'intersectent au centre du cercle présupposé.
Ainsi, ce popint aura un très grand nombre de vote et sera le maximum de la matrice accumulatrice : on a alors ses coordonnées en fonction de sa position dans la matrice, et son rayon en fonction de la première dimension de la matrice accumulatrice : 
La matrice est de taille N,X,Y avec X et Y les dimensions en pixels de l'image (3280 par 1845, et N dépend de la présision/le pas entre les rayons des cercles que l'on dessine

Au lieu de tracer un cercle complet, on optimise par un calcul de gradient : 
Pour chaque point d'intérêt, au lieu de tracer un cercle complet, on calcule le gradient de ce point d'intérêt sur l'image noir et blanc du dessus : le gradient nous donnera alors les directions dans lesquelles tracer des arcs de cercle : on prend juste deux noyaux Gx et Gy donnant le gradient en x et en Y, et on obtient l'angle absolu par la norme euclidienne des deux vecteurs, et on trace des arcs de cercle e direction de cet angle, et à l'opposé, sur une amplitude de 45° au vu de la précision de l'angle obtenu par cette méthode : on trace ainsi seulement un quart de cercle pour chaque points plutôt qu'un cercle complet

si on essaye maintenant de détecter le cercle, voilà ce que cela donne, avec un pas de 5 pixels pour le rayon, et en traçant 128 points de chaque cercles (ceux que l'on trace pour chaque points d'intérêts

![gough cercle](https://github.com/hacktivist25/ballTracking/assets/125929174/bf156d16-3d50-43de-9b7d-1f515b168234)
 ()
Voilà le plan pour lequel on aurait un maximum : il se situe au42èpme plan de notre matrice accumulatrice, et les coordonnées du maximum sur ce plan sont (1392, 952) : ce sont les coordonnées de son centre, qu'on note aCentre et bCentre
Le 42ème plan représent un rayon de 260 pixels, puisque l'on commence nos recherches à partir d'un cercle de rayon 50 pixels : 42*5 + 50 = 260
Et voilà le cercle trouvé, avec ses coordonnées aCentre, bCentre, et son rayon, trouvé juste avant :

![finalite](https://github.com/hacktivist25/ballTracking/assets/125929174/5bb32c74-d685-4b8b-a4e3-d74c5479794f)
![infos final](https://github.com/hacktivist25/ballTracking/assets/125929174/90034c36-5040-49e6-bfd1-aa24a1b4cd76)

Cela colle parfaitement avec la balle que l'on voit sur le plan :


Reste à convertir ces coordonnées pixel en coordonnées réelles : 
C'est là qu'entre en jeu notre capteur de distance et notre centrale inertielle, ainsi que d'autres specs de notre caméra.

Intéressons nous d'abord aux deux capteurs que nous utiliserons :
Le capteur de distance : VL53L0X de chez STMicroElectronics : son GitHub pour l'installation de la  bibliothèque, les commandes... [9]
Sa fiche technique [9]

![SDA and SCL](https://github.com/hacktivist25/ballTracking/assets/125929174/11ce09d5-9ec8-474c-97ef-f584c039231b)
![tech specs](https://github.com/hacktivist25/ballTracking/assets/125929174/dee71896-b7ca-4d05-a8e8-fc87ef06d9c0)
![specs](https://github.com/hacktivist25/ballTracking/assets/125929174/2d262447-3f35-463d-b301-8e09cad7fa69)

On retiens qu'il fonctionne via un protocole I2C, son adresse est 0x22 (on a reprogrammé l'adresse)
L'horloge qui cadence l'envoie de données de l'esclave (le capteur) jusqu'au maître (la carte raspberryPi Model4B) va jusqu'à 400kHz
Il fonctionne en 3.3 Volts


L'accéléromètre, partie de l'IMU MP9250 : sa fiche technique : [10] et son gitHub [11]

![accelerometre IMU 10D0F specs](https://github.com/hacktivist25/ballTracking/assets/125929174/d9f4674f-28d1-4f4c-b2f5-531bdb94ae19)
![specs](https://github.com/hacktivist25/ballTracking/assets/125929174/f3e2d720-278b-4b61-93ae-3c1bc23ba97d)
![table](https://github.com/hacktivist25/ballTracking/assets/125929174/e910169f-0717-43eb-96e2-199f184d4d01)

idem, fonctionne par protocole I2C, son adresse est 0x68, fonctionne avec une horloge SCL jusqu'à 400kHz (quelle aubaine)
il fonctionne en 5 Volts

Enfin, on regarde la fiche technique du raspberry pour voir comment faire les branchements : [12]
![GPIO4 Raspberrypi du site officiel](https://github.com/hacktivist25/ballTracking/assets/125929174/47281e75-ef10-4480-8c80-abbc5defbb07)
![Capture d’écran 2023-05-14 214212](https://github.com/hacktivist25/ballTracking/assets/125929174/762610f5-6a39-42b5-a472-497b73d1e0f9)


on obtient le schéma de branchements suivant :

[sch.pdf](https://github.com/hacktivist25/ballTracking/files/11566803/sch.pdf)

et on peut les faire fonctionner correctement avc les fonctions caputreAngle et captureDistance à la toute fin du code balltracking.py :
captureDistancene fait que lire la distance du capteure VL53L0X
captureAngle ne fait que lire les valeurs des accéléromètres selon les 3 axes de l'IMU, et en déduit le pitch avec la formule : pitch = 180 * m.atan (accelerationX/m.sqrt(accelerationY*accelerationY + accelerationZ*accelerationZ))/m.pi; 

![Pitch](https://github.com/hacktivist25/ballTracking/assets/125929174/888faa6a-9bc1-4cd6-8dfd-e1b3a295954a)

Le but va être d'avoir un pitch de -90° pour que la caméra pointe parfaitement vers le dessous pour simplifier les calculs : on ne prend pas n compte la distorsion caméra, au vu de cette photo 

![calibrageBas](https://github.com/hacktivist25/ballTracking/assets/125929174/58143319-4f67-47ce-ba93-a6934d192753)

ON pourra déduire ainsi les coordonnées de la balle par rapport au centre optique de la caméra/le centre de l'image, en distance réelles, juste en connaissant la distance entre la caméra et le centre de l'image, et le champ angulaire de la caméra, donné par les specs de la caméra raspberrypi camera model v2 :

![CamScanner 05-25-2023 18 01 (1)_1](https://github.com/hacktivist25/ballTracking/assets/125929174/7ef9f7fa-08ca-4bcd-b80a-5f5f3b38174b)

![CamScanner 05-25-2023 18 01 (1)_2](https://github.com/hacktivist25/ballTracking/assets/125929174/e1c332d5-da35-43c1-959d-83f4aad1e003)

Les points équidistants en pixels sur une image correspondent à des points de l'obet réel à égal pas angulaire par rapport à la caméra
Ainsi en négligeant dnas un premier temps les distorsions de l'image, on arrive à avoi les coordonnées assez exactes du centre d'une balle par rapprot au centre d'une image : le reste n'est qu'affaire de changement de repère : il suffit de trouver l'intersection ded deux droites du repère dessiné sur l'image grpâce à leur deux équations :
On a d1 : y = a1x + b1
et d2 : y = a2x + b2

on pose alors (a1-a2)x + (b1-b2) = 0
d'où x = (b2-b1)/(a1-a2)
et on en déduit l'ordonnée d'intersetion :
Des deux équations, on déduit deux vecteurs directeurs, et il n'y a plus qu'à faire des changements de repère en usant le module vector de python (pas encore fait : de toute façon, le projet sera transposé ultérieurement en C pour attendre les objectifs de temps réel)



[1] https://towardsdatascience.com/lines-detection-with-hough-transform-84020b3b1549
[2] https://homepages.inf.ed.ac.uk/rbf/HIPR2/hough.htm
[3] https://sbme-tutorials.github.io/2021/cv/notes/4_week4.html
[4] https://www.raspberrypi.com/documentation/accessories/camera.html
[5] https://indiantechwarrior.com/canny-edge-detection-for-image-processing/
[6] https://arxiv.org/ftp/arxiv/papers/1405/1405.7242.pdf
[7] https://en.wikipedia.org/wiki/Circle_Hough_Transform
[8] https://github.com/Gadgetoid/VL53L0X-python
[9] https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&ved=2ahUKEwiTkOKj_oj_AhWMUKQEHfo5DT0QFnoECA0QAQ&url=https%3A%2F%2Fwww.st.com%2Fresource%2Fen%2Fdatasheet%2Fvl53l0x.pdf&usg=AOvVaw2D772P0Ms66VJ7lbKKynB-
[10] https://invensense.tdk.com/wp-content/uploads/2015/02/PS-MPU-9250A-01-v1.1.pdf
[11] https://github.com/FaBoPlatform/FaBo9AXIS-MPU9250-Python
[12] https://pinout.xyz/pinout/pin7_gpio4#
