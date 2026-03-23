🧪 **Data Quality Template**

## 🎯 Objectif

Comparer rapidement les données entre :

- source (prod)
- DWH (dev)

👉 Valider qu’un développement (ex: Talaxie) est correct.

---

## ⚙️ Installation

### 1️⃣ Récupérer le projet

```bash
git clone https://github.com/ton-user/talaxie-dq-template.git
cd talaxie-dq-template
2️⃣ Installer les dépendances
pip install -r requirements.txt

Vérifier Python : python --version

🔧 Configuration

👉 Fichier à modifier : dq/config.yml (connexion bdd)

🧠 Définir un check métier

👉 Créer : dq/checks/mon_check.yml

Copier le template :

cp dq/checks/example.yml dq/checks/mon_check.yml

👉 Structure : voir dq/checks/example.yml

Champs
name : nom du test
table : table métier (ex: sales)
measure : agrégat SQL (SUM, COUNT…)
tolerance : écart acceptable
where (optionnel) : filtre SQL
📊 Exemples
CA
- name: ca
  table: sales
  measure: sum(amount)
  tolerance: 0.01

Compare :

SELECT sum(amount) FROM prod.sales
SELECT sum(amount) FROM dwh.fact_sales
Volume
- name: volume
  table: sales
  measure: count(*)
🚀 Lancer un test
python dq/run.py dq/checks/mon_check.yml

👉 À lancer à la racine du projet

📈 Résultat
🔎 Validation : ventes
✅ ca OK
❌ volume KO → 10000 vs 9980

👉 Interprétation :

OK → données cohérentes
KO → problème dans le dev
🎯 À retenir
Modifier uniquement : dq/config.yml et dq/checks/mon_check.yml
Ne pas toucher au code Python
1 fichier = 1 thème métier
1 commande = validation
