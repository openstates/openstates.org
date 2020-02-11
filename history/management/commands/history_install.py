from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection
from collections import namedtuple


GET_TRIGGERS_SQL = """
select event_object_schema as table_schema,
       event_object_table as table_name,
       trigger_schema,
       trigger_name,
       string_agg(event_manipulation, ',') as event,
       action_timing as activation,
       action_condition as condition,
       action_statement as definition
from information_schema.triggers
group by 1,2,3,4,6,7,8
order by table_schema, table_name;
"""

CREATE_TRIGGER_TEMPLATE_SQL = """
CREATE TRIGGER history_insert AFTER INSERT ON {0}
  FOR EACH ROW EXECUTE PROCEDURE history_insert();
CREATE TRIGGER history_delete AFTER DELETE ON {0}
  FOR EACH ROW EXECUTE PROCEDURE history_delete();
CREATE TRIGGER history_update AFTER UPDATE ON {0}
  FOR EACH ROW EXECUTE PROCEDURE history_update();
"""


class Command(BaseCommand):
    help = "install required triggers for history tracking"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--uninstall", action="store_true")

    def _exec_sql(self, statement):
        with connection.cursor() as cursor:
            if self.dry_run:
                print(statement)
            else:
                cursor.execute(statement)

    def uninstall(self):
        drop_sql = ""
        count = 0
        tables = set()
        with connection.cursor() as cursor:
            cursor.execute(GET_TRIGGERS_SQL)
            desc = cursor.description
            nt_result = namedtuple("Result", [col[0] for col in desc])
            for row in cursor.fetchall():
                result = nt_result(*row)
                if result.trigger_name in (
                    "history_insert",
                    "history_update",
                    "history_delete",
                ):
                    drop_sql += (
                        f"DROP TRIGGER {result.trigger_name} ON {result.table_name};\n"
                    )
                    count += 1
                    tables.add(result.table_name)

        print(
            f"Found {count} existing triggers installed on {len(tables)} tables, dropping them."
        )
        self._exec_sql(drop_sql)

    def handle(self, *args, **options):
        self.dry_run = options["dry_run"]
        if self.dry_run:
            print("Dry Run: SQL will be printed but database will not be modified.")
        if options["uninstall"]:
            self.uninstall()
        for table in settings.HISTORY_TABLES:
            print(f"Installing triggers on {table}.")
            self._exec_sql(CREATE_TRIGGER_TEMPLATE_SQL.format(table, table, table))
        print("Installing get_object_id function from settings.")
        self._exec_sql(settings.HISTORY_GET_OBJECT_ID_SQL)
