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
CREATE OR REPLACE FUNCTION get_object_id(table_name name, r RECORD) returns varchar(100) as $$
BEGIN
  CASE table_name
  WHEN 'opencivicdata_bill' THEN
    RETURN r.id;
  WHEN 'opencivicdata_billactionrelatedentity' THEN
    RETURN (select a.bill_id from opencivicdata_billaction a WHERE a.id=r.action_id);
  WHEN 'opencivicdata_billdocumentlink' THEN
    RETURN (select x.bill_id from opencivicdata_billdocument x WHERE x.id=r.document_id);
  WHEN 'opencivicdata_billversionlink' THEN
    RETURN (select x.bill_id from opencivicdata_billversion x WHERE x.id=r.version_id);
  ELSE
    RETURN r.bill_id;
  END CASE;
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION history_insert()
RETURNS TRIGGER AS $$
DECLARE
  object_id varchar(100) := get_object_id(TG_TABLE_NAME, NEW);
BEGIN
  INSERT INTO history_change(event_time, table_name, object_id, new)
     VALUES(CURRENT_TIMESTAMP, TG_TABLE_NAME, object_id, row_to_json(NEW)::jsonb);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION history_delete()
RETURNS TRIGGER AS $$
DECLARE
  object_id varchar(100) := get_object_id(TG_TABLE_NAME, OLD);
BEGIN
  INSERT INTO history_change(event_time, table_name, object_id, old)
     VALUES(CURRENT_TIMESTAMP, TG_TABLE_NAME, object_id, row_to_json(OLD)::jsonb);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION history_update()
RETURNS TRIGGER AS $$
DECLARE
  js_new jsonb := row_to_json(NEW)::jsonb;
  js_old jsonb := row_to_json(OLD)::jsonb;
  object_id varchar(100) := get_object_id(TG_TABLE_NAME, OLD);
BEGIN
  INSERT INTO history_change(event_time, table_name, object_id, old, new)
     VALUES(CURRENT_TIMESTAMP, TG_TABLE_NAME, object_id, js_old - js_new, js_new - js_old);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER history_insert AFTER INSERT ON opencivicdata_bill
  FOR EACH ROW EXECUTE PROCEDURE history_insert();
CREATE TRIGGER history_delete AFTER DELETE ON opencivicdata_bill
  FOR EACH ROW EXECUTE PROCEDURE history_delete();
CREATE TRIGGER history_update AFTER UPDATE ON opencivicdata_bill
  FOR EACH ROW EXECUTE PROCEDURE history_update();

CREATE TRIGGER history_insert AFTER INSERT ON opencivicdata_billabstract
  FOR EACH ROW EXECUTE PROCEDURE history_insert();
CREATE TRIGGER history_delete AFTER DELETE ON opencivicdata_billabstract
  FOR EACH ROW EXECUTE PROCEDURE history_delete();
CREATE TRIGGER history_update AFTER UPDATE ON opencivicdata_billabstract
  FOR EACH ROW EXECUTE PROCEDURE history_update();

CREATE TRIGGER history_insert AFTER INSERT ON opencivicdata_billtitle
  FOR EACH ROW EXECUTE PROCEDURE history_insert();
CREATE TRIGGER history_delete AFTER DELETE ON opencivicdata_billtitle
  FOR EACH ROW EXECUTE PROCEDURE history_delete();
CREATE TRIGGER history_update AFTER UPDATE ON opencivicdata_billtitle
  FOR EACH ROW EXECUTE PROCEDURE history_update();

CREATE TRIGGER history_insert AFTER INSERT ON opencivicdata_billidentifier
  FOR EACH ROW EXECUTE PROCEDURE history_insert();
CREATE TRIGGER history_delete AFTER DELETE ON opencivicdata_billidentifier
  FOR EACH ROW EXECUTE PROCEDURE history_delete();
CREATE TRIGGER history_update AFTER UPDATE ON opencivicdata_billidentifier
  FOR EACH ROW EXECUTE PROCEDURE history_update();

CREATE TRIGGER history_insert AFTER INSERT ON opencivicdata_billaction
  FOR EACH ROW EXECUTE PROCEDURE history_insert();
CREATE TRIGGER history_delete AFTER DELETE ON opencivicdata_billaction
  FOR EACH ROW EXECUTE PROCEDURE history_delete();
CREATE TRIGGER history_update AFTER UPDATE ON opencivicdata_billaction
  FOR EACH ROW EXECUTE PROCEDURE history_update();

CREATE TRIGGER history_insert AFTER INSERT ON opencivicdata_relatedbill
  FOR EACH ROW EXECUTE PROCEDURE history_insert();
CREATE TRIGGER history_delete AFTER DELETE ON opencivicdata_relatedbill
  FOR EACH ROW EXECUTE PROCEDURE history_delete();
CREATE TRIGGER history_update AFTER UPDATE ON opencivicdata_relatedbill
  FOR EACH ROW EXECUTE PROCEDURE history_update();

CREATE TRIGGER history_insert AFTER INSERT ON opencivicdata_billsponsorship
  FOR EACH ROW EXECUTE PROCEDURE history_insert();
CREATE TRIGGER history_delete AFTER DELETE ON opencivicdata_billsponsorship
  FOR EACH ROW EXECUTE PROCEDURE history_delete();
CREATE TRIGGER history_update AFTER UPDATE ON opencivicdata_billsponsorship
  FOR EACH ROW EXECUTE PROCEDURE history_update();

CREATE TRIGGER history_insert AFTER INSERT ON opencivicdata_billdocument
  FOR EACH ROW EXECUTE PROCEDURE history_insert();
CREATE TRIGGER history_delete AFTER DELETE ON opencivicdata_billdocument
  FOR EACH ROW EXECUTE PROCEDURE history_delete();
CREATE TRIGGER history_update AFTER UPDATE ON opencivicdata_billdocument
  FOR EACH ROW EXECUTE PROCEDURE history_update();

CREATE TRIGGER history_insert AFTER INSERT ON opencivicdata_billversion
  FOR EACH ROW EXECUTE PROCEDURE history_insert();
CREATE TRIGGER history_delete AFTER DELETE ON opencivicdata_billversion
  FOR EACH ROW EXECUTE PROCEDURE history_delete();
CREATE TRIGGER history_update AFTER UPDATE ON opencivicdata_billversion
  FOR EACH ROW EXECUTE PROCEDURE history_update();

CREATE TRIGGER history_insert AFTER INSERT ON opencivicdata_billsource
  FOR EACH ROW EXECUTE PROCEDURE history_insert();
CREATE TRIGGER history_delete AFTER DELETE ON opencivicdata_billsource
  FOR EACH ROW EXECUTE PROCEDURE history_delete();
CREATE TRIGGER history_update AFTER UPDATE ON opencivicdata_billsource
  FOR EACH ROW EXECUTE PROCEDURE history_update();

CREATE TRIGGER history_insert AFTER INSERT ON opencivicdata_billversionlink
  FOR EACH ROW EXECUTE PROCEDURE history_insert();
CREATE TRIGGER history_delete AFTER DELETE ON opencivicdata_billversionlink
  FOR EACH ROW EXECUTE PROCEDURE history_delete();
CREATE TRIGGER history_update AFTER UPDATE ON opencivicdata_billversionlink
  FOR EACH ROW EXECUTE PROCEDURE history_update();

CREATE TRIGGER history_insert AFTER INSERT ON opencivicdata_billdocumentlink
  FOR EACH ROW EXECUTE PROCEDURE history_insert();
CREATE TRIGGER history_delete AFTER DELETE ON opencivicdata_billdocumentlink
  FOR EACH ROW EXECUTE PROCEDURE history_delete();
CREATE TRIGGER history_update AFTER UPDATE ON opencivicdata_billdocumentlink
  FOR EACH ROW EXECUTE PROCEDURE history_update();

CREATE TRIGGER history_insert AFTER INSERT ON opencivicdata_billactionrelatedentity
  FOR EACH ROW EXECUTE PROCEDURE history_insert();
CREATE TRIGGER history_delete AFTER DELETE ON opencivicdata_billactionrelatedentity
  FOR EACH ROW EXECUTE PROCEDURE history_delete();
CREATE TRIGGER history_update AFTER UPDATE ON opencivicdata_billactionrelatedentity
  FOR EACH ROW EXECUTE PROCEDURE history_update();
"""


class Migration(migrations.Migration):
    dependencies = [("history", "0001_initial")]

    operations = [migrations.RunSQL(JSON_DELETE_OP), migrations.RunSQL(TRIGGER_SQL)]
