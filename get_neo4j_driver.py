from neo4j import GraphDatabase

# enter your Neo4j credentials here

    NEO4J_URI = "neo4j://127.0.0.1:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "mist460-graph-db-server-mikky"
    NEO4J_DATABASE = "mist460-graph-db-mikky"# Change this

def get_neo4j_driver():
    """Establishes and returns a connection instance (a "driver") to the Neo4j database using the credentials we set earlier."""
    uri = NEO4J_URI
    user = NEO4J_USERNAME
    password = NEO4J_PASSWORD
    return GraphDatabase.driver(uri, auth=(user, password), database=NEO4J_DATABASE)
