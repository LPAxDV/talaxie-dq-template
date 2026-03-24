import yaml
import sys
import psycopg2


# 📌 Lire un fichier YAML (config ou checks)
def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


# 📌 Connexion à la base
# → ici Postgres (simple pour démarrer)
def connect_db(db_config):
    return psycopg2.connect(
        host=db_config["host"],
        database=db_config["database"],
        user=db_config["user"],
        password=db_config["password"]
    )


# 📌 Exécute une requête SQL et retourne une valeur (SUM, COUNT…)
def run_query(conn, query):
    cur = conn.cursor()
    cur.execute(query)
    result = cur.fetchone()[0]
    cur.close()
    return result


# 📌 Génère automatiquement le SQL
# → évite d’écrire du SQL à chaque fois
def build_query(env, table, measure, where=None):

    # convention simple :
    # source → prod.table
    # dwh → dwh.fact_table

    if env == "src":
        query = f"SELECT {measure} FROM prod.{table}"
    else:
        query = f"SELECT {measure} FROM dwh.fact_{table}"

    # filtre optionnel
    if where:
        query += f" WHERE {where}"

    return query


def main(check_file):

    # 1️⃣ Charger config (connexions)
    config = load_yaml("dq/config.yml")

    # 2️⃣ Charger règles métier
    checks = load_yaml(check_file)

    # 3️⃣ Connexions
    conn_src = connect_db(config["source_db"])
    conn_dwh = connect_db(config["dwh_db"])

    print(f"\n🔎 Validation : {checks['theme']}\n")

    has_error = False

    # 4️⃣ Boucle sur les checks
    for check in checks["checks"]:

        src_query = build_query("src", check["table"], check["measure"], check.get("where"))
        dwh_query = build_query("dwh", check["table"], check["measure"], check.get("where"))

        src_val = run_query(conn_src, src_query)
        dwh_val = run_query(conn_dwh, dwh_query)

        tol = check.get("tolerance", config["defaults"]["tolerance"])

        diff = dwh_val - src_val
        if abs(diff) > tol:
            print(
                f"❌ {check['name']} KO | "
                f"SRC={src_val} | DWH={dwh_val} | DIFF={diff}"
            )
            has_error = True
        else:
            print(f"✅ {check['name']} OK")

    conn_src.close()
    conn_dwh.close()

    # 📌 Important : permet de faire échouer un pipeline CI/CD ou Talaxie
    if has_error:
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1])
