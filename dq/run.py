import yaml
import sys


# 📌 Pourquoi YAML ?
# → pour éviter de modifier le code à chaque projet
# → tu changes juste config + règles
def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


# 📌 Pourquoi une fonction de connexion ?
# → rendre le code indépendant de la base (Postgres, Oracle, etc.)
def connect_db(db_config):
    import psycopg2  # simplifié ici

    return psycopg2.connect(
        host=db_config["host"],
        database=db_config["database"],
        user=db_config["user"],
        password=db_config["password"]
    )


# 📌 Pourquoi exécuter du SQL ?
# → on compare des données réelles (pas juste la connexion)
# → objectif : valider que le DWH est correct
def run_query(conn, query):
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchone()[0]
    cur.close()
    return result


# 📌 Génération automatique des requêtes
# → évite d’écrire du SQL partout
def build_query(db_type, table, measure):

    # convention projet :
    # prod.sales
    # dwh.fact_sales

    if db_type == "src":
        return f"SELECT {measure} FROM prod.{table}"
    else:
        return f"SELECT {measure} FROM dwh.fact_{table}"


def main(check_file):

    # 📌 1. config projet (connexions)
    config = load_yaml("dq/config.yml")

    # 📌 2. règles métier (ex: ventes)
    checks = load_yaml(check_file)

    # 📌 3. connexions aux 2 environnements
    conn_src = connect_db(config["source_db"])
    conn_dwh = connect_db(config["dwh_db"])

    print(f"\n🔎 Validation métier : {checks['theme']}\n")

    for check in checks["checks"]:

        # 📌 on calcule les indicateurs métier
        src_val = run_query(conn_src, build_query("src", check["table"], check["measure"]))
        dwh_val = run_query(conn_dwh, build_query("dwh", check["table"], check["measure"]))

        # 📌 tolérance métier (écart acceptable)
        tol = check.get("tolerance", config["defaults"]["tolerance"])

        # 📌 comparaison
        if abs(src_val - dwh_val) > tol:
            print(f"❌ {check['name']} KO → incohérence data")
        else:
            print(f"✅ {check['name']} OK")

    conn_src.close()
    conn_dwh.close()


if __name__ == "__main__":
    main(sys.argv[1])
