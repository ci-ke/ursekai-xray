#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 new_config.js 中的常量
从 mysekaiMaterials.json 和 mysekaiFixtures.json 读取信息并更新配置文件
"""

import json
import os
import sys

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def load_materials():
    """加载材料数据"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    materials_path = os.path.join(script_dir, 'mysekaiMaterials.json')

    with open(materials_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_fixtures():
    """加载家具数据"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    fixtures_path = os.path.join(script_dir, 'mysekaiFixtures.json')

    with open(fixtures_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_item_textures(materials):
    """生成 ITEM_TEXTURES 映射 (包含所有材料)"""
    textures = {}

    for material in materials:
        item_id = str(material['id'])
        icon_name = material['iconAssetbundleName']

        # 根据材料类型确定路径
        if material['mysekaiMaterialType'] == 'game_character':
            path = f"./icon/Texture2D/memoria/{icon_name}.png"
        else:
            path = f"./icon/Texture2D/{icon_name}.png"

        textures[item_id] = path

    return textures


def generate_fixture_textures(fixtures):
    """生成 mysekai_fixture 的纹理映射 (只包含 plant 类型)"""
    textures = {}

    for fixture in fixtures:
        # 只处理 plant 类型的家具
        if fixture['mysekaiFixtureType'] != 'plant':
            continue

        fixture_id = str(fixture['id'])
        asset_name = fixture['assetbundleName']

        # 生成纹理路径
        path = f"./icon/Texture2D/{asset_name}_{fixture_id}.png"
        textures[fixture_id] = path

    return textures


def generate_rare_items(materials):
    """生成 RARE_ITEM 列表 (rarity_2)"""
    rare_items = []

    for material in materials:
        # 排除 game_character 和 birthday_party 类型
        if material['mysekaiMaterialType'] in ['game_character', 'birthday_party']:
            continue

        if material['mysekaiMaterialRarityType'] == 'rarity_2':
            rare_items.append(material['id'])

    return sorted(rare_items)


def generate_super_rare_items(materials):
    """生成 SUPER_RARE_ITEM 列表 (rarity_3 和 rarity_4,并固定包含 5, 12, 20, 24)"""
    super_rare_items = set([5, 12, 20, 24])  # 固定包含这些ID

    for material in materials:
        # 排除 game_character 和 birthday_party 类型
        if material['mysekaiMaterialType'] in ['game_character', 'birthday_party']:
            continue

        rarity = material['mysekaiMaterialRarityType']
        if rarity in ['rarity_3', 'rarity_4']:
            super_rare_items.add(material['id'])

    return sorted(list(super_rare_items))


def generate_fixture_rare_items(fixtures):
    """生成 mysekai_fixture 的稀有物品列表 (plant 类型中 seq 在 21001001-21001004 范围内的)"""
    rare_items = []

    for fixture in fixtures:
        # 只处理 plant 类型的家具
        if fixture['mysekaiFixtureType'] != 'plant':
            continue

        # seq 在 21001001-21001004 范围内的是稀有物品(树苗)
        if 21001001 <= fixture['seq'] <= 21001004:
            rare_items.append(fixture['id'])

    return sorted(rare_items)


def format_js_object(data, indent=2):
    """格式化为 JavaScript 对象字符串"""
    lines = []
    indent_str = ' ' * indent

    for key, value in data.items():
        lines.append(f'{indent_str * 2}"{key}": "{value}",')

    return '\n'.join(lines)


def format_js_array(data, indent=2):
    """格式化为 JavaScript 数组字符串"""
    return ', '.join(str(x) for x in data)


def update_config(materials, fixtures):
    """更新 new_config.js 文件"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'new_config.js')

    # 生成数据
    item_textures = generate_item_textures(materials)
    fixture_textures = generate_fixture_textures(fixtures)
    rare_items = generate_rare_items(materials)
    super_rare_items = generate_super_rare_items(materials)
    fixture_rare_items = generate_fixture_rare_items(fixtures)

    # 构建新的配置内容
    config_content = f"""// Item texture mapping - maps item IDs to their texture asset paths
export const ITEM_TEXTURES = {{
    mysekai_material: {{
{format_js_object(item_textures)}
    }},
    mysekai_item: {{
        "7": "./icon/Texture2D/item_blueprint_fragment.png"
    }},
    mysekai_fixture: {{
{format_js_object(fixture_textures)}
    }},
    mysekai_music_record: {{
        "*": "./icon/Texture2D/item_surplus_music_record.png"
    }}
}};

// Rare item rarity tier definitions
export const RARE_ITEM = {{
    mysekai_material: [{format_js_array(rare_items)}],
    mysekai_item: [7],
    mysekai_music_record: [],
    mysekai_fixture: [{format_js_array(fixture_rare_items)}]
}};

// Super rare item definitions (highest rarity tier)
export const SUPER_RARE_ITEM = {{
    mysekai_material: [{format_js_array(super_rare_items)}],
    mysekai_item: [],
    mysekai_fixture: [],
    mysekai_music_record: []
}};"""

    # 写入文件
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)

    print(f"[OK] 已更新 new_config.js")
    print(f"  - 材料纹理映射: {len(item_textures)} 项")
    print(f"  - 家具纹理映射: {len(fixture_textures)} 项")
    print(f"  - 稀有材料: {len(rare_items)} 项")
    print(f"  - 超稀有材料: {len(super_rare_items)} 项")
    print(f"  - 稀有家具: {len(fixture_rare_items)} 项")


def main():
    """主函数"""
    print("开始更新配置文件...")

    try:
        materials = load_materials()
        print(f"[OK] 已加载 {len(materials)} 个材料")

        fixtures = load_fixtures()
        print(f"[OK] 已加载 {len(fixtures)} 个家具")

        update_config(materials, fixtures)
        print("\n更新完成!")

    except FileNotFoundError as e:
        print(f"[ERROR] 错误: 找不到文件 - {e}")
    except json.JSONDecodeError as e:
        print(f"[ERROR] 错误: JSON 解析失败 - {e}")
    except Exception as e:
        print(f"[ERROR] 错误: {e}")


if __name__ == '__main__':
    main()
