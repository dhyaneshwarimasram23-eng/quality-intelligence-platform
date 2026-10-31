from qi.db.database import init_db, engine
from qi.models.models import Base

def test_database_creation():
    """Test that database tables can be created"""
    init_db()
    # Check that tables exist
    table_names = Base.metadata.tables.keys()
    assert "test_runs" in table_names
    assert "test_results" in table_names
    assert "failure_evidence" in table_names
    assert "flaky_test_history" in table_names
    print("All database tables created successfully!")