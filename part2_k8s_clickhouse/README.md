## Partie 2

J'ai utilise k3d parce que c'est un outil que j'ai deja utilise et qui est pratique pour rapidement creer un cluster de test leger de k8s.

J'ai prefere utiliser un Statefulset pour le test car la logique de volume persitent est integre dans la logique d'un statefulset. J;aurais pu utiliser un deployment pour le test comme on n'a qu'une seule replica a creer, mais il faudrait creer le PVC a part et specifier une strategie Recreate pour que le pod a remplacer soit detruit avant que le nouveau soit cree.
Le statefulset est le choix que j'aurais fait en prod, puisqu'il garantie une identite fixe aux pods quand ils sont recrees.

Lors de son demarrage clickhouse aura un script qui tourne pour que la table job_metrics soit ajoute, je vais utiliser une ConfigMap pour que ca soit plus lisible, sinon le script sera hardcode dans le statefulset et ca ne fera pas propre.

J'ai choisi un service NodePort car il expose un port de mon node pour qu'il soit accessible a l'exterieur du cluster, necessaire pour que le script `send-metrics.py` puisse envoyer ses donnees dans clickhouse.
