"""
读取manifest.schema.json
        ↓
检查Schema本身是否合法
        ↓
读取manifest.csv并转换字段类型
        ↓
逐行执行JSON Schema验证
        ↓
核对本地文件大小和SHA-256
"""
from __future__ import annotations
import csv 
import json 
from typing import Any 
from pathlib import Path 
from jsonschema import Draft202012Validator

#=========================
# BASIC SETTINGS
#=========================

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
MANIFEST_PATH = ROOT_DIR / 'data' / 'manifest.csv'
SCHEMA_PATH = ROOT_DIR / 'data' / 'manifest.schema.json'

def load_json_schema(path: Path) -> dict[str,Any]:
    with path.open('r',encoding = 'utf-8') as file:
        return json.load(file)
    
def validate_schema_definition(schema: dict[str,Any]) -> None:
    Draft202012Validator.check_schema(schema)
    
def load_manifest_csv(path: Path) -> tuple[list[str],list[dict[str,str|None]]]:
    with path.open('r',encoding = 'utf-8-sig', newline = '') as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("Manifest 缺少表头")
        
        fieldnames = list(reader.fieldnames)
        rows = list(reader)
    return fieldnames, rows

def validate_manifest_header(
        fieldnames: list[str],
        schema: dict[str,Any]
) -> None:
    expected_fieldnames =  list(schema['properties'].keys())

    duplicates = sorted({
        name
        for name in fieldnames 
        if fieldnames.count(name) > 1
    })

    missing = [name for name in expected_fieldnames if name not in fieldnames]

    extra = [name for name in fieldnames if name not in expected_fieldnames]

    errors: list[str] = []

    if duplicates:
        errors.append(f"重复列:{duplicates}")

    if missing:
        errors.append(f"缺少列：{missing}")

    if extra:
        errors.append(f"未知列：{extra}")

    if errors:
        raise ValueError("Manifest 表头无效:" + ";".join(errors))

    if fieldnames != expected_fieldnames:
        raise ValueError("Manifest 表头顺序和 Schema不一致")

def normalize_row(
        row: dict[str,str|None]
) -> dict[str,Any]:
    normalized: dict[str,Any] = {}

    for fieldname,value in row.items():
        if value is None:
            normalized[fieldname] = None
            continue 

        stripped_value = value.strip()

        if stripped_value == "":
            normalized[fieldname] = None 

        else:
            normalized[fieldname] = stripped_value

        record_id = normalized.get('record_id')
        byte_size = normalized.get('byte_size')

        if byte_size is not None:
            try:
                normalized['byte_size'] = int(byte_size)
            except (TypeError,ValueError) as error:
                raise ValueError(
                    f"{record_id} : byte_size 必须是整数"
                    f"实际为{byte_size!r}"
                ) from error 
    return normalized

def main() -> int:
    schema = load_json_schema(SCHEMA_PATH)

    fieldnames, rows = load_manifest_csv(MANIFEST_PATH)

    validate_schema_definition(schema)
    validate_manifest_header(fieldnames,schema)

    normalized_rows = [
        normalize_row(row) for row in rows
    ]   

    first_row = normalized_rows[0]

    print(f"local_path: {first_row['local_path']!r}")
    print(f"byte_size: {first_row['byte_size']!r}")
    print(f"byte_size type: {type(first_row['byte_size']).__name__}")

    return 0 

if __name__ == "__main__":
    raise SystemExit(main())
