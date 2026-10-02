#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 config.js
从 master 目录的 mysekaiMaterials.json、mysekaiFixtures.json 和 materials.json 读取信息并更新配置文件

用法:
    python update_config.py [master_dir]
    master_dir 不传时默认为脚本同目录下的 master 文件夹
"""

import argparse
import io
import json
import os
import sys
from typing import Any

# 设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def resolve_master_dir() -> str:
    """解析 master 数据目录：优先使用命令行参数，否则使用脚本同目录下的 master 文件夹"""
    parser = argparse.ArgumentParser(
        description='从 master 数据目录读取 mysekaiMaterials.json / mysekaiFixtures.json 并更新 new_config.js'
    )
    parser.add_argument(
        'master_dir',
        nargs='?',
        default=None,
        help='master 数据目录路径（不传则默认为脚本同目录下的 master 文件夹）'
    )
    args = parser.parse_args()

    if args.master_dir:
        return args.master_dir

    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, 'master')


def load_mysekai_materials(master_dir: str) -> list[dict[str, Any]]:
    """加载材料数据"""
    materials_path = os.path.join(master_dir, 'mysekaiMaterials.json')

    with open(materials_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_materials(master_dir: str) -> list[dict[str, Any]]:
    """加载通用材料数据 (materials.json)"""
    materials_path = os.path.join(master_dir, 'materials.json')

    with open(materials_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_fixtures(master_dir: str) -> list[dict[str, Any]]:
    """加载家具数据"""
    fixtures_path = os.path.join(master_dir, 'mysekaiFixtures.json')

    with open(fixtures_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_mysekai_item_textures(materials: list[dict[str, Any]]) -> dict[str, str]:
    """生成 mysekai_material 的纹理映射 (排除 game_character 和 birthday_party 类型)"""
    textures: dict[str, str] = {}

    for material in materials:
        # 排除 game_character 和 birthday_party 类型
        if material['mysekaiMaterialType'] in ('game_character', 'birthday_party'):
            continue

        item_id = str(material['id'])
        icon_name = material['iconAssetbundleName']
        path = f"./icon/Texture2D/{icon_name}.png"
        textures[item_id] = path

    return textures


def generate_material_textures(materials: list[dict[str, Any]]) -> dict[str, str]:
    """生成 material 的纹理映射 (仅 materialType == birthday_party_delivery)"""
    textures: dict[str, str] = {}

    for material in materials:
        if material['materialType'] != 'birthday_party_delivery':
            continue

        item_id = str(material['id'])
        textures[item_id] = f"./icon/Texture2D/material{item_id}.png"

    return textures


def generate_fixture_textures(fixtures: list[dict[str, Any]]) -> dict[str, str]:
    """生成 mysekai_fixture 的纹理映射 (只包含 plant 类型)"""
    textures: dict[str, str] = {}

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


def generate_rare_items(materials: list[dict[str, Any]]) -> list[int]:
    """生成 RARE_ITEM 列表 (rarity_2)"""
    rare_items: list[int] = []

    for material in materials:
        # 排除 game_character 和 birthday_party 类型
        if material['mysekaiMaterialType'] in ('game_character', 'birthday_party'):
            continue

        if material['mysekaiMaterialRarityType'] == 'rarity_2':
            rare_items.append(material['id'])

    return sorted(rare_items)


def generate_super_rare_items(materials: list[dict[str, Any]]) -> list[int]:
    """生成 SUPER_RARE_ITEM 列表 (rarity_3 和 rarity_4,并固定包含 5, 12, 20, 24)"""
    super_rare_items: set[int] = {5, 12, 20, 24}  # 固定包含这些ID

    for material in materials:
        # 排除 game_character 和 birthday_party 类型
        if material['mysekaiMaterialType'] in ('game_character', 'birthday_party'):
            continue

        rarity = material['mysekaiMaterialRarityType']
        if rarity in ('rarity_3', 'rarity_4'):
            super_rare_items.add(material['id'])

    return sorted(super_rare_items)


def format_js_object(data: dict[str, str], indent: int = 2) -> str:
    """格式化为 JavaScript 对象字符串"""
    lines: list[str] = []
    indent_str = ' ' * 4  # 每级缩进 4 个空格

    for key, value in data.items():
        lines.append(f'{indent_str * indent}"{key}": "{value}",')

    return '\n'.join(lines)


def format_js_array(data: list[int]) -> str:
    """格式化为 JavaScript 数组字符串"""
    return ', '.join(str(x) for x in data)


def update_config(materials: list[dict[str, Any]], fixtures: list[dict[str, Any]], game_materials: list[dict[str, Any]]) -> None:
    """更新 new_config.js 文件"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'new_config.js')

    # 生成数据
    item_textures = generate_mysekai_item_textures(materials)
    fixture_textures = generate_fixture_textures(fixtures)
    material_textures = generate_material_textures(game_materials)
    rare_items = generate_rare_items(materials)
    super_rare_items = generate_super_rare_items(materials)

    # 构建新的配置内容
    config_content = f"""// Scene configuration - per-scene coordinate transformation parameters
export const SCENES = {{
    scene1: {{
        physicalWidth: 33.333,
        offsetX: 0,
        offsetY: -40,
        imagePath: "img/grassland.png",
        xDirection: 'x-',
        yDirection: 'y-',
        reverseXY: true,
    }},
    scene2: {{
        physicalWidth: 24.806,
        offsetX: -62.015,
        offsetY: 20.672,
        imagePath: "img/flowergarden.png",
        xDirection: 'x-',
        yDirection: 'y-',
        reverseXY: true,
    }},
    scene3: {{
        physicalWidth: 20.513,
        offsetX: 0,
        offsetY: 80,
        imagePath: "img/beach.png",
        xDirection: 'x+',
        yDirection: 'y-',
        reverseXY: false,
    }},
    scene4: {{
        physicalWidth: 21.333,
        offsetX: 0,
        offsetY: -106.667,
        imagePath: "img/memorialplace.png",
        xDirection: 'x+',
        yDirection: 'y-',
        reverseXY: false,
    }}
}};

// Scene ID mapping for display names
export const SITE_ID_MAP = {{
    1: "マイホーム",
    2: "1F",
    3: "2F",
    4: "3F",
    5: "さいしょの原っぱ",
    6: "願いの砂浜",
    7: "彩りの花畑",
    8: "忘れ去られた場所"
}};

// Fixture color mapping for different fixture types
export const FIXTURE_COLORS = {{
    111: '#f9f9f9',
    112: '#f9f9f9',

    1001: '#8B6F47', // wood
    1002: '#8B6F47',
    1003: '#8B6F47',
    1004: '#8B6F47',

    2001: '#878685', // iron
    2002: '#d5750a', // copper
    2003: '#d5d5d5', // stone
    2004: '#a7c7cb',
    2005: '#9933cc',
    2006: '#00FFFF', // diamond

    3001: '#4A90E2',

    4001: '#ffd380', // flower
    4002: '#ffd380',
    4003: '#ffd380',
    4004: '#ffd380',
    4005: '#ffd380',
    4006: '#ffd380',
    4007: '#ffd380',
    4008: '#ffd380',
    4009: '#ffd380', // cotton
    4010: '#ffd380',
    4011: '#ffd380',
    4012: '#ffd380',
    4013: '#ffd380',
    4014: '#ffd380',
    4015: '#ffd380',
    4016: '#ffd380',
    4017: '#ffd380',
    4018: '#ffd380',
    4019: '#ffd380',
    4020: '#ffd380',

    5001: '#f6f5f2',
    5002: '#f6f5f2',
    5003: '#f6f5f2',
    5004: '#f6f5f2',
    5101: '#f6f5f2',
    5102: '#f6f5f2',
    5103: '#f6f5f2',
    5104: '#f6f5f2',

    6001: '#6f4e37',

    7001: '#a5d9ff',
}};

// Default fallback icon for missing textures
export const MISSING_ICON = './icon/missing.png';

// Item texture mapping - maps item IDs to their texture asset paths
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
    }},
    mysekai_blueprint: {{
        "*": "./icon/Texture2D/item_surplus_blueprint.png"
    }},
    material: {{
{format_js_object(material_textures)}
    }}
}};

// Rare item rarity tier definitions
export const RARE_ITEM = {{
    mysekai_material: [{format_js_array(rare_items)}],
    mysekai_item: [],
    mysekai_fixture: [],
    mysekai_music_record: [],
    mysekai_blueprint: [],
    material: []
}};

// Super rare item definitions (highest rarity tier)
export const SUPER_RARE_ITEM = {{
    mysekai_material: [{format_js_array(super_rare_items)}],
    mysekai_item: [],
    mysekai_fixture: [],
    mysekai_music_record: [],
    mysekai_blueprint: [],
    material: []
}};

// Ultra rare item definitions (exceptional rarity tier, overrides super rare styling)
export const ULTRA_RARE_ITEM = {{
    mysekai_material: [12],
    mysekai_item: [],
    mysekai_fixture: [],
    mysekai_music_record: [],
    mysekai_blueprint: [],
    material: []
}};
"""

    # 写入文件
    with open(config_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(config_content)

    print("[OK] 已更新 new_config.js")
    print(f"  - 材料纹理映射: {len(item_textures)} 项")
    print(f"  - 家具纹理映射: {len(fixture_textures)} 项")
    print(f"  - 庆典甘露纹理映射: {len(material_textures)} 项")
    print(f"  - 稀有材料: {len(rare_items)} 项")
    print(f"  - 超稀有材料: {len(super_rare_items)} 项")


def main() -> None:
    """主函数"""
    master_dir = resolve_master_dir()
    print(f"开始更新配置文件... (数据目录: {master_dir})")

    try:
        mysekai_materials = load_mysekai_materials(master_dir)
        print(f"[OK] 已加载 {len(mysekai_materials)} 个 mysekai 材料")

        fixtures = load_fixtures(master_dir)
        print(f"[OK] 已加载 {len(fixtures)} 个家具")

        materials = load_materials(master_dir)
        print(f"[OK] 已加载 {len(materials)} 个通用材料")

        update_config(mysekai_materials, fixtures, materials)
        print("\n更新完成!")

    except FileNotFoundError as e:
        print(f"[ERROR] 错误: 找不到文件 - {e}")
    except json.JSONDecodeError as e:
        print(f"[ERROR] 错误: JSON 解析失败 - {e}")
    except Exception as e:
        print(f"[ERROR] 错误: {e}")


if __name__ == '__main__':
    main()
