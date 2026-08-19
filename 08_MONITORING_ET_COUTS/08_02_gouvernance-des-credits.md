# 08.02 — Gouvernance des Copilot Credits

## Objectif du fichier

- **À quoi sert ce fichier** : maîtriser le coût de l'agent, qui est facturé à l'usage et non couvert par une licence forfaitaire.
- **Étape du développement** : étape 08, exploitation. Les garde-fous doivent exister **dès l'étape 02**.
- **Ce que vous faites** : vous posez une allocation et une limite dans le Power Platform admin center, et vous instaurez un suivi.
- **Résultat attendu avant de passer à l'étape suivante** : une limite existe, une alerte est configurée, et vous savez qui la surveille.

---

## Le modèle de coût, en trois phrases

Les agents propulsés par le harness GitHub Copilot sont facturés **à l'usage, en Copilot Credits**. Cette facturation s'applique à **toute** utilisation : conversations réelles, mais aussi construction, tests dans l'onglet Preview et exécutions d'évaluation. Elle s'applique **même si votre organisation dispose de licences Microsoft 365 Copilot** **[OFFICIEL]**.

C'est la différence de modèle économique la plus importante entre l'ancien agent et le nouveau, et elle doit être connue de votre sponsor avant la mise à l'échelle.

## Ce qui consomme, par ordre d'importance

| Poste | Quand | Ordre de grandeur |
|---|---|---|
| **Exécutions d'évaluation** | Phase de projet | **Le poste dominant pendant le développement.** 53 cas × plusieurs exécutions par jour, et trois essais sur les cas analytiques |
| Conversations utilisateurs | Après publication | Le poste dominant en régime établi |
| Tests dans Preview | Phase de projet | Faible unitairement, non négligeable en cumul |
| Consultation de la source | À chaque question de données | Inclus dans le coût de la réponse |

Conséquence pratique en phase de projet : **regroupez vos exécutions d'évaluation**. Modifier une description, relancer les 53 cas, remodifier, relancer — c'est le réflexe le plus coûteux. Testez les cas ciblés dans Preview, et réservez la suite complète aux moments de décision.

## Les garde-fous à poser

Dans le **Power Platform admin center** > **Licensing** > **Copilot Studio** :

1. **Allocation de crédits sur l'environnement** — sans elle, vous serez bloqué en plein développement.
2. **Limite mensuelle au niveau de l'agent**, avec un seuil de notification. Posez-la même large : une limite existante vaut mieux qu'une découverte en fin de mois.
3. **Règle d'application** — choisissez consciemment entre alerter et bloquer.

> **Recommandation pour ce projet** : en développement, **alerter** plutôt que bloquer — un blocage en pleine campagne de tests fait perdre plus qu'il n'économise. Après la bascule, la question se repose : un agent de dictionnaire qui s'arrête est gênant mais pas critique ; un agent qui dérape en coût sans alerte l'est davantage. **[CHOIX PROJET]**

**À savoir :** une limite posée au niveau d'un agent ne plafonne pas le total de l'environnement. Si plusieurs agents cohabitent, l'allocation d'environnement reste le garde-fou global.

## Estimer avant de mettre à l'échelle

Avant d'ouvrir l'agent à l'ensemble des utilisateurs, faites l'exercice avec les chiffres du pilote :

```
Consommation observée pendant le pilote : ......... crédits
Nombre d'utilisateurs pilotes : ...................
Consommation moyenne par utilisateur et par mois : ........
Nombre d'utilisateurs cibles : ....................
Estimation mensuelle en régime établi : ...........
Budget validé : ...................................
```

Deux précautions de lecture : les utilisateurs pilotes testent l'agent et consomment souvent **plus** que des utilisateurs en régime normal ; à l'inverse, une adoption large amène des usages que le pilote n'a pas produits. Prenez une marge, et re-mesurez un mois après la bascule.

## Ce que cette architecture vous fait économiser

Ce n'est pas neutre, et cela mérite d'être dit à votre sponsor : l'agent n'a **aucun outil**, **aucun flux**, **aucune exécution de code**. Chaque question déclenche au plus une consultation de la source et une génération de réponse. Il n'y a ni action de flux facturée, ni appel d'outil, ni chaîne d'appels multiples.

C'est le profil de consommation le plus sobre qu'un agent de ce type puisse avoir sur cette plateforme, et c'est une conséquence directe du choix de simplicité.

## Critères de fin d'étape

- [ ] Une allocation de crédits existe sur l'environnement.
- [ ] Une limite mensuelle et une alerte sont posées au niveau de l'agent.
- [ ] Le sponsor connaît le modèle de facturation à l'usage.
- [ ] Une estimation de consommation en régime établi a été faite après le pilote.
- [ ] Je passe au dossier `09_ALM_ET_MAINTENANCE`.
