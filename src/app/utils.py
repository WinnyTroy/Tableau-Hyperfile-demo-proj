# Utility functions file
import os
import pandas as pd
from typing import List
from pathlib import Path
from app.settings import settings
from app.libs.client import TableauClient
from tableauhyperapi import (
    SqlType, Connection, HyperProcess, TableName,
    escape_string_literal, TableDefinition, CreateMode)



def element_type_to_hyper_sql_type(elem_type: str) -> SqlType:
    type_map = {
        'integer': SqlType.big_int,
        'decimal': SqlType.double,
        'text': SqlType.text,
    }
    return type_map.get(elem_type)


def _pandas_type_to_hyper_sql_type(type: str) -> SqlType:
    # TODO: Remove pandas; Intial thought was to derive the column type
    # using Pandas but ran into constraint issues on the DB level for some
    # of the numerical fields. In the future we should probably use the XLSForm
    # JSON to create the schema for a CSV Import...
    type_map = {
        'b': SqlType.bool,
        'i': SqlType.big_int,
        'u': SqlType.big_int,
        'f': SqlType.double,
        'c': SqlType.double,
        'O': SqlType.text,
        'S': SqlType.text,
        'a': SqlType.text,
        'U': SqlType.text
    }
    return SqlType.text


def _import_csv_to_hyperfile(
        path: str, csv_path: str, process: HyperProcess,
        table_name: TableName = TableName("Extract", "Extract"),
        null_field: str = "NULL", delimiter: str = ",") -> int:
    """
    Imports CSV data into a HyperFile
    """
    with Connection(
            endpoint=process.endpoint, database=path) as connection:
        command = (
            f"COPY {table_name} from {escape_string_literal(csv_path)} with "
            f"(format csv, NULL '{null_field}', delimiter '{delimiter}', header)"
        )
        count = connection.execute_command(command=command)
        return count


def _prep_csv_for_import(csv_path: Path) -> List[TableDefinition.Column]:
    """
    Creates a schema definition from the csv headers.
    DISCLAIMER: This function doesn't actually try to derive the columns
    type. It returns every column as a string column
    """
    columns: List[SqlType] = []
    df = pd.read_csv(csv_path, na_values=['n/a', ''])
    df = df.convert_dtypes()
    for name, dtype in df.dtypes.iteritems():
        column = TableDefinition.Column(
            name,
            _pandas_type_to_hyper_sql_type(dtype.kind)()
        )
        columns.append(column)
    # Save dataframe to CSV as the dataframe is more cleaner
    # in most cases. We also don't want the headers to be within
    # the CSV as Hyper picks the header as a value
    with open(csv_path, "w") as f:
        f.truncate(0)
    df.to_csv(csv_path, na_rep='NULL', header=False, index=False)
    return columns


def handle_csv_import(
        file_identifier: str,
        csv_path: Path,
        process: HyperProcess,
        publish: bool = False) -> int:
    """
    Handles CSV Import to Hyperfile
    """
    database_path = f"{settings.media_path}/{file_identifier}.hyper"
    table_name = TableName("Extract", "Extract")
    columns = _prep_csv_for_import(csv_path=csv_path)
    # TODO: Check if columns match saved Hyper file ?
    if not os.path.isfile(database_path):
        with Connection(
                endpoint=process.endpoint,
                database=database_path,
                create_mode=CreateMode.CREATE_AND_REPLACE) as connection:
            connection.catalog.create_schema('Extract')
            extract_table = TableDefinition(
                table_name,
                columns=columns
            )
            connection.catalog.create_table(extract_table)
    import_count = _import_csv_to_hyperfile(
        path=database_path, csv_path=str(csv_path),
        table_name=table_name, process=process)
    if publish:
        tableau_client = TableauClient()
        tableau_client.publish_hyper(database_path)

    return import_count