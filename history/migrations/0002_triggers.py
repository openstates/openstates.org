from django.db import migrations, models

JSON_DELETE_OP = """
--
-- Glyn Astill 16/01/2015
-- Attempt at hstore style delete operator for jsonb
--

SET search_path = 'public';

CREATE OR REPLACE FUNCTION jsonb_delete_left(a jsonb, b text)
RETURNS jsonb AS
$BODY$
    SELECT COALESCE(
        (
            SELECT ('{' || string_agg(to_json(key) || ':' || value, ',') || '}')
            FROM jsonb_each(a)
            WHERE key <> b
        )
    , '{}')::jsonb;
$BODY$
LANGUAGE sql IMMUTABLE STRICT;
COMMENT ON FUNCTION jsonb_delete_left(jsonb, text) IS 'delete key in second argument from first argument';

CREATE OPERATOR - ( PROCEDURE = jsonb_delete_left, LEFTARG = jsonb, RIGHTARG = text);
COMMENT ON OPERATOR - (jsonb, text) IS 'delete key from left operand';

--

CREATE OR REPLACE FUNCTION jsonb_delete_left(a jsonb, b text[])
RETURNS jsonb AS
$BODY$
    SELECT COALESCE(
        (
            SELECT ('{' || string_agg(to_json(key) || ':' || value, ',') || '}')
            FROM jsonb_each(a)
            WHERE key <> ALL(b)
        )
    , '{}')::jsonb;
$BODY$
LANGUAGE sql IMMUTABLE STRICT;
COMMENT ON FUNCTION jsonb_delete_left(jsonb, text[]) IS 'delete keys in second argument from first argument';

CREATE OPERATOR - ( PROCEDURE = jsonb_delete_left, LEFTARG = jsonb, RIGHTARG = text[]);
COMMENT ON OPERATOR - (jsonb, text[]) IS 'delete keys from left operand';

--

CREATE OR REPLACE FUNCTION jsonb_delete_left(a jsonb, b jsonb)
RETURNS jsonb AS
$BODY$
    SELECT COALESCE(
        (
            SELECT ('{' || string_agg(to_json(key) || ':' || value, ',') || '}')
            FROM jsonb_each(a)
            WHERE NOT ('{' || to_json(key) || ':' || value || '}')::jsonb <@ b
        )
    , '{}')::jsonb;
$BODY$
LANGUAGE sql IMMUTABLE STRICT;
COMMENT ON FUNCTION jsonb_delete_left(jsonb, jsonb) IS 'delete matching pairs in second argument from first argument';

CREATE OPERATOR - ( PROCEDURE = jsonb_delete_left, LEFTARG = jsonb, RIGHTARG = jsonb);
COMMENT ON OPERATOR - (jsonb, jsonb) IS 'delete matching pairs from left operand';
"""

TRIGGER_SQL = """
CREATE OR REPLACE FUNCTION history_insert()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO history_billhistory(event_time, table_name, bill_id, new)
     VALUES(CURRENT_TIMESTAMP, TG_TABLE_NAME, NEW.id, row_to_json(NEW)::jsonb);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION history_delete()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO history_billhistory(event_time, table_name, bill_id, old)
     VALUES(CURRENT_TIMESTAMP, TG_TABLE_NAME, OLD.id, row_to_json(OLD)::jsonb);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION history_update()
RETURNS TRIGGER AS $$
DECLARE
  js_new jsonb := row_to_json(NEW)::jsonb;
  js_old jsonb := row_to_json(OLD)::jsonb;
BEGIN
  INSERT INTO history_billhistory(event_time, table_name, bill_id, old, new)
     VALUES(CURRENT_TIMESTAMP, TG_TABLE_NAME, OLD.id, js_old - js_new, js_new - js_old);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER test_history_insert AFTER INSERT ON opencivicdata_bill
  FOR EACH ROW EXECUTE PROCEDURE history_insert();

CREATE TRIGGER test_history_delete AFTER DELETE ON opencivicdata_bill
  FOR EACH ROW EXECUTE PROCEDURE history_delete();

CREATE TRIGGER test_history_update AFTER UPDATE ON opencivicdata_bill
  FOR EACH ROW EXECUTE PROCEDURE history_update();
"""


class Migration(migrations.Migration):
    dependencies = [
        ("history", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(JSON_DELETE_OP),
        migrations.RunSQL(TRIGGER_SQL),
    ]
