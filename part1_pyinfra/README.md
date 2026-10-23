## Partie 1

J'ai cherche la maniere la plus simple de tester la partie 1, j'avais un serveur distant a ma disposition, qui servirait de serveur 1 et mon propre PC qui ferait office de 2e serveur.

Pour le serveur python, j'ai fait le choix de Flask, car c'est plus simple a mettre en place, plus lisible, et mettre la reponse au format JSON se fait avec jsonify qui fait partie du package de Flask, avec http_server ca aurait ete plus complique.

J'ai fait le choix de donner des droits de lecture et execution elargis a tous les utilisateurs pour les fichiers et dossiers lies au service puisque `ubuntu` n'est pas l'utilisateur que j'utilisais pendant mes tests.
