#!/usr/bin/env python3
import json
import sys

def extract_high_fields():
    try:
        with open('field_database_v1.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        high_fields = []
        for field_name, field_data in data['fields'].items():
            if field_data.get('power_pool_suitability') == 'HIGH':
                high_fields.append({
                    'name': field_name,
                    'dataset': field_data.get('dataset', 'UNKNOWN'),
                    'data_type': field_data.get('data_type', 'UNKNOWN'),
                    'frequency': field_data.get('usage_statistics', {}).get('frequency', 0),
                    'correlation_risk': field_data.get('correlation_risk', {}).get('level', 'UNKNOWN')
                })
        
        print(f"找到 {len(high_fields)} 个power_pool_suitability为HIGH的字段:")
        print("-" * 80)
        for field in high_fields:
            print(f"名称: {field['name']}")
            print(f"  数据集: {field['dataset']}, 数据类型: {field['data_type']}")
            print(f"  使用频率: {field['frequency']}, 相关性风险: {field['correlation_risk']}")
            print()
        
        return high_fields
    except Exception as e:
        print(f"错误: {e}")
        return []

if __name__ == "__main__":
    extract_high_fields()