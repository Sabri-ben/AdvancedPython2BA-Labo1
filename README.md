
1.Objectif:

Le but est de dévelloper une IA qui est capable de jouer au jeu Kasimado en prenant des décisions optimales à partir d'une exploration d'arbre de jeu.

2.Comment notre IA prend une précsion ?

Dans ce jeu , l'IA devra jouer contre un humain qui réfléchit avant de jouer.
L'intelligence artificielle fait 3 étapes: -Elle regarde tous les coups possibles.
                                           -Elle imagine ce que le joueur adversaire pourrai faire comme coup.
                                           -Puis, elle choisit le coups à faire qui donne le meilleur résultat.

3.Qu'est ce que c'est minimax et quel est son role?

Dans la creéation de ce jeu, nous avons utilsé la méthode qui se nomme Minimax.
Cette méthode suit l'idée :
 -Quand c'est à notre tour (celle de l'IA), on cherche le meilleur coup.
 -Quand c'est le tour de l'adversaire, il choisire le pire des coups à faire.

 En conclusion, l'IA joue aux échecs dans sa tête mais de manière plus malin vu qu'il choisit à chaque fois le meilleur des choix.

4.Problème/Solution:

Ici le problème que je rencontrai dans ce jeu, c'est la rapidité de réflexion vu qu'il y a beaoucoup de possibilités.

Donc, la solution à ce problème est la méthode alpha-béta qui est une réflexion très rapide du stle par exemple: -Si on voit qu’un chemin est déjà mauvais, on arrête de le regarder , cherche une autre possibilité.

5.Commment l'IA si la position est bonne ou non?

Elle utilise donc une fonction simple :

def evaluate(board, my_kind):

Cette fonction répond à une seule question :

“Est-ce que cette position est bonne pour moi ou pas ?”

L’IA donne un score à la position :

score positif → c’est bien pour elle
score négatif → c’est mieux pour l’adversaire

Elle regarde toutes les cases du plateau.Pour chaque pièce, elle se pose 2 questions :

1️Est-ce que la pièce est proche de gagner ?
plus elle est avancée → plus c’est bien
plus elle est loin → moins c’est bien

Donc : avancer = gagner des points

Est-ce que la pièce est bien placée ?
au centre → beaucoup de possibilités
sur le côté → bloquée

Donc :

centre = bonus

Comment elle calcule

Pour chaque pièce :-elle ajoute des points si c’est sa pièce
                   -elle enlève des points si c’est une pièce adverse

Traduction simple :

“Ce qui est bon pour moi = +
Ce qui est bon pour l’adversaire = −”

Résultat final: À la fin, elle obtient un nombre.

Exemple :

+50 → très bonne position
0 → équilibré
−30 → mauvaise position

6.Structure du projet
.
├── client.py          → lance la partie et communique avec le serveur
├── strategy.py        → le “cerveau” de l’IA
├── tests/
│   └── test_strategy.py → vérifie que tout fonctionne bien
└── README.md

7.Pour lancer le client

Dans le terminal:
python client.py <url_serveur> <nom_joueur>

8.Pour lancer les test:

Dans le terminal:
pytest tests/


