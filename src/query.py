"""Stage 4: Predefined Cypher queries against both graphs."""
import yaml
import falkordb


def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)


def connect(config: dict, database: str):
    client = falkordb.FalkorDB(host=config["falkordb_host"], port=config["falkordb_port"])
    return client.select_graph(database)


QUERIES = {
    "odysseus_ego_network": {
        "description": "All direct relations involving Odysseus",
        "cypher": """
            MATCH (a)-[r]->(b)
            WHERE toLower(a.name) CONTAINS 'odysseus' OR toLower(b.name) CONTAINS 'odysseus'
            RETURN a.name, type(r), b.name
            LIMIT 50
        """,
    },
    "journey_path": {
        "description": "TRAVELS_TO chain (schema graph only)",
        "cypher": """
            MATCH (a)-[r:TRAVELS_TO]->(b)
            RETURN a.name, b.name
            ORDER BY a.name
        """,
    },
    "divine_intervention": {
        "description": "Gods protecting, punishing, enchanting, or detaining characters",
        "cypher": """
            MATCH (god)-[r]->(target)
            WHERE type(r) IN ['PROTECTS', 'PUNISHES', 'ENCHANTS', 'DETAINS']
            RETURN god.name, type(r), target.name
        """,
    },
    "disguise_recognition": {
        "description": "Disguise and recognition events",
        "cypher": """
            MATCH (a)-[r]->(b)
            WHERE type(r) IN ['DISGUISES_AS', 'RECOGNIZES', 'DETAINS']
            RETURN a.name, type(r), b.name
        """,
    },
}


def run_queries(graph, label: str):
    print(f"\n{'='*50}")
    print(f"Graph: {label}")
    print(f"{'='*50}")
    for name, q in QUERIES.items():
        print(f"\n>> {name}: {q['description']}")
        try:
            result = graph.query(q["cypher"])
            rows = result.result_set
            if not rows:
                print("   (no results)")
            for row in rows[:20]:
                print(" ", row)
        except Exception as e:
            print(f"   ERROR: {e}")


if __name__ == "__main__":
    config = load_config()

    schema_graph = connect(config, "odyssey_schema")
    open_graph = connect(config, "odyssey_open")

    run_queries(schema_graph, "odyssey_schema (guided)")
    run_queries(open_graph, "odyssey_open (open-domain)")
