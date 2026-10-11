#!/usr/bin/env python3
"""
Comprehensive update for Total War: Attila Arabic localization.
Adds:
1. campaign_effect_scopes.loc translations (all armies, all regions, factionwide)
2. All missing effect_bundles.loc trait titles and white lore text
3. All missing effects.loc trait descriptions
"""
import os
import json

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOGICAL_JSON = os.path.join(BASE, "translated", "part1_logical.json")

ITEMS = [
    # 1. campaign_effect_scopes.loc
    {"key": "campaign_effect_scopes_localised_text_faction_to_army_own", "table": "text/db/campaign_effect_scopes.loc", "en": "(all armies)", "ar": "(لكافة الجيوش)"},
    {"key": "campaign_effect_scopes_localised_text_province_to_army_factionwide", "table": "text/db/campaign_effect_scopes.loc", "en": "(all armies)", "ar": "(لكافة الجيوش)"},
    {"key": "campaign_effect_scopes_localised_text_province_to_character_when_commanding_army_own_factionwide", "table": "text/db/campaign_effect_scopes.loc", "en": "(all armies)", "ar": "(لكافة الجيوش)"},
    {"key": "campaign_effect_scopes_localised_text_faction_to_region_own", "table": "text/db/campaign_effect_scopes.loc", "en": "(all regions)", "ar": "(لكافة الأقاليم)"},
    {"key": "campaign_effect_scopes_localised_text_region_to_region_own_factionwide", "table": "text/db/campaign_effect_scopes.loc", "en": "(all regions)", "ar": "(لكافة الأقاليم)"},
    {"key": "campaign_effect_scopes_localised_text_faction_to_faction_own", "table": "text/db/campaign_effect_scopes.loc", "en": "(factionwide)", "ar": "(على مستوى الفصيل)"},
    {"key": "campaign_effect_scopes_localised_text_province_to_province_own_factionwide", "table": "text/db/campaign_effect_scopes.loc", "en": "(factionwide)", "ar": "(على مستوى الفصيل)"},
    {"key": "campaign_effect_scopes_localised_text_building_to_forces_factionwide", "table": "text/db/campaign_effect_scopes.loc", "en": "(factionwide)", "ar": "(على مستوى الفصيل)"},
    {"key": "campaign_effect_scopes_localised_text_province_to_sea_region_own_factionwide", "table": "text/db/campaign_effect_scopes.loc", "en": "(factionwide)", "ar": "(على مستوى الفصيل)"},
    {"key": "campaign_effect_scopes_localised_text_character_to_faction", "table": "text/db/campaign_effect_scopes.loc", "en": "(factionwide)", "ar": "(على مستوى الفصيل)"},
    {"key": "campaign_effect_scopes_localised_text_province_to_region_own_factionwide", "table": "text/db/campaign_effect_scopes.loc", "en": "(factionwide)", "ar": "(على مستوى الفصيل)"},
    {"key": "campaign_effect_scopes_localised_text_province_to_faction", "table": "text/db/campaign_effect_scopes.loc", "en": "(factionwide)", "ar": "(على مستوى الفصيل)"},

    # 2. effect_bundles.loc
    {"key": "effect_bundles_localised_description_att_faction_trait_lakhmids", "table": "text/db/effect_bundles.loc", "en": "A cultural melting-pot, where Arab and Persian influences coexist.", "ar": "بوتقة انصهار ثقافي تتعايش فيها التأثيرات العربية والفارسية جنباً إلى جنب.", "is_narrative": False},
    {"key": "effect_bundles_localised_description_att_faction_trait_garamantes", "table": "text/db/effect_bundles.loc", "en": "\"Whoever drinks of the water that I will give him shall never thirst\"", "ar": "\"من يشرب من هذا الماء الذي أمنحه إياه لن يظمأ أبداً إلى الأبد.\"", "is_narrative": False},
    {"key": "effect_bundles_localised_description_att_faction_trait_himyar", "table": "text/db/effect_bundles.loc", "en": "A way of life, a way of war - the harsh desert conditions dictate how both are waged.", "ar": "نمط حياة وأسلوب حرب تفرضه ظروف الصحراء القاسية وكفاح البقاء.", "is_narrative": False},
    {"key": "effect_bundles_localised_description_att_faction_trait_axum", "table": "text/db/effect_bundles.loc", "en": "A hub of free trade and vast wealth, where east and west meet.", "ar": "مركز للتجارة الحرة وثروات طائلة لا تنضب، حيث يلتقي الشرق والغرب.", "is_narrative": False},
    {"key": "effect_bundles_localised_description_att_faction_trait_arabian", "table": "text/db/effect_bundles.loc", "en": "Immune to desert attrition.", "ar": "حصانة تامة ضد الإنهاك الصحراوي في كافة المعارك والمسيرات.", "is_narrative": False},
    {"key": "effect_bundles_localised_description_att_faction_trait_african", "table": "text/db/effect_bundles.loc", "en": "Massive bonuses when defending.", "ar": "مكافآت قتالية ودفاعية هائلة عند الدفاع عن الأراضي والمدن.", "is_narrative": False},
    {"key": "effect_bundles_localised_title_att_faction_trait_african", "table": "text/db/effect_bundles.loc", "en": "Fierce Independence", "ar": "استقلال شرس", "is_narrative": False},
    {"key": "effect_bundles_localised_title_att_faction_trait_aethiopian", "table": "text/db/effect_bundles.loc", "en": "Trade Masters", "ar": "أسياد التجارة", "is_narrative": False},
    {"key": "effect_bundles_localised_description_att_faction_trait_aethiopian", "table": "text/db/effect_bundles.loc", "en": "Improved tariffs.", "ar": "تعريفات تجارية وأرباح موانئ محسنة لتعظيم الموارد.", "is_narrative": False},
    {"key": "effect_bundles_localised_title_att_faction_trait_migrators_vandals", "table": "text/db/effect_bundles.loc", "en": "Sea of the Vandals", "ar": "بحر الوندال", "is_narrative": False},
    {"key": "effect_bundles_localised_description_att_faction_trait_migrators_vandals", "table": "text/db/effect_bundles.loc", "en": "The winds cry doom, and carry death across the waves.", "ar": "رياح البحر تعصف بالموت وتحمل الهلاك عبر الأمواج لخصومهم.", "is_narrative": False},
    {"key": "effect_bundles_localised_title_att_faction_trait_migrators_alans", "table": "text/db/effect_bundles.loc", "en": "Sarmatian Horsemanship", "ar": "فروسية سارماتية", "is_narrative": False},
    {"key": "effect_bundles_localised_description_att_faction_trait_migrators_alans", "table": "text/db/effect_bundles.loc", "en": "To ride the steppes, man and steed must be one. No easy task.", "ar": "ليجوب السهوب، يجب أن يكون الفارس وجواده جسداً واحداً لا ينفصل.", "is_narrative": False},
    {"key": "effect_bundles_localised_title_att_faction_trait_migrators_ostrogoths", "table": "text/db/effect_bundles.loc", "en": "Inheritors of Rome", "ar": "ورثة روما", "is_narrative": False},
    {"key": "effect_bundles_localised_description_att_faction_trait_migrators_ostrogoths", "table": "text/db/effect_bundles.loc", "en": "Civilisation may shift and change, but the eternal city remains.", "ar": "قد تتبدل الحضارات وتتغير، لكن المدينة الخالدة تبقى رمزاً للمجد.", "is_narrative": False},
    {"key": "effect_bundles_localised_title_att_faction_trait_migrators_visigoths", "table": "text/db/effect_bundles.loc", "en": "Blood Money", "ar": "فدية الدم", "is_narrative": False},
    {"key": "effect_bundles_localised_description_att_faction_trait_migrators_visigoths", "table": "text/db/effect_bundles.loc", "en": "A tributary penance is only just, if not entirely necessary.", "ar": "دفع الجزية كفارة عادلة لمن تجرأ على غدرهم وخيانتهم.", "is_narrative": False},
    {"key": "effect_bundles_localised_title_att_faction_trait_barbarian_franks", "table": "text/db/effect_bundles.loc", "en": "Ferocious Warriors", "ar": "محاربون أشداء", "is_narrative": False},
    {"key": "effect_bundles_localised_description_att_faction_trait_barbarian_franks", "table": "text/db/effect_bundles.loc", "en": "Never without sword in-hand, nor rage in the veins.", "ar": "لا يغادر السيف أيديهم، ولا تخمد جذوة الغضب في عروقهم.", "is_narrative": False},
    {"key": "effect_bundles_localised_title_att_faction_trait_barbarian_saxons", "table": "text/db/effect_bundles.loc", "en": "Saxon Shore", "ar": "ساحل السكسون", "is_narrative": False},
    {"key": "effect_bundles_localised_description_att_faction_trait_barbarian_saxons", "table": "text/db/effect_bundles.loc", "en": "The oceans and the fields will burn, with waves of flame and steel.", "ar": "ستحترق البحار والسهول بأمواج من اللهب وفؤوس الغزاة.", "is_narrative": False},
    {"key": "effect_bundles_localised_title_att_faction_trait_eastern_sassanid", "table": "text/db/effect_bundles.loc", "en": "King of Kings", "ar": "ملك الملوك", "is_narrative": False},
    {"key": "effect_bundles_localised_description_att_faction_trait_eastern_sassanid", "table": "text/db/effect_bundles.loc", "en": "The Shah, with a watchful eye, observes, controls, and exacts tribute.", "ar": "شاهنشاه، بعين يقظة، يراقب ويوجه ويفرض سلطانه المطلق على الشرق.", "is_narrative": False},
    {"key": "effect_bundles_localised_title_att_faction_trait_roman_west", "table": "text/db/effect_bundles.loc", "en": "Cultural Integration", "ar": "الاندماج الثقافي", "is_narrative": False},
    {"key": "effect_bundles_localised_description_att_faction_trait_roman_west", "table": "text/db/effect_bundles.loc", "en": "Men are men, no matter their origin.", "ar": "الرجال هم الرجال، مهما اختلفت أصولهم ومنابتهم تحت لواء النسر.", "is_narrative": False},
    {"key": "effect_bundles_localised_title_att_faction_trait_roman_east", "table": "text/db/effect_bundles.loc", "en": "Economic Powerhouse", "ar": "القوة الاقتصادية", "is_narrative": False},
    {"key": "effect_bundles_localised_description_att_faction_trait_roman_east", "table": "text/db/effect_bundles.loc", "en": "Straddle the crossroads of the world and take pick of everything that passes through.", "ar": "السيطرة على مفترق طرق العالم وجني ثمار كل ما يمر عبره.", "is_narrative": False},

    # 3. effects.loc
    {"key": "effects_description_att_effect_suebi_dummy", "table": "text/db/effects.loc", "en": "%+n% upkeep for 10 turns for any army that loots or sacks a settlement.", "ar": "نفقات صيانة %+n% لمدة 10 أدوار لأي جيش ينهب أو يدمر مستوطنة.", "is_narrative": False},
    {"key": "effects_description_att_effect_eos_fractured_faiths", "table": "text/db/effects.loc", "en": "Fractured Faiths: Increased public order penalty for religious differences between new religions", "ar": "عقائد منقسمة: زيادة عقوبة النظام العام بسبب الاختلافات الدينية بين الأديان الجديدة", "is_narrative": False},
    {"key": "effects_description_att_effect_eos_desert_strongholds_melee_defense", "table": "text/db/effects.loc", "en": "Scourge of the Desert: %+n melee attack during desert battles", "ar": "سوط الصحراء: %+n هجوم قريب أثناء المعارك الصحراوية", "is_narrative": False},
    {"key": "effects_description_att_effect_eos_food_from_attacking_settlements", "table": "text/db/effects.loc", "en": "Food: %+n from attacking enemy settlements", "ar": "طعام: %+n عند مهاجمة مستوطنات الأعداء", "is_narrative": False},
    {"key": "effects_description_att_effect_eos_improved_marib_dam_repair", "table": "text/db/effects.loc", "en": "Improved repair of the Ma'rib dam.", "ar": "إصلاح وتدعيم متقدم لسد مأرب التاريخي", "is_narrative": False},
    {"key": "effects_description_att_effect_eos_growth_from_winning_battles", "table": "text/db/effects.loc", "en": "Growth: %+n growth from winning battles", "ar": "نمو: %+n نمو عند الانتصار في المعارك", "is_narrative": False},
]


def update():
    with open(LOGICAL_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    entries = data["entries"]
    entry_map = {e["key"]: e for e in entries}

    added = 0
    updated = 0
    for item in ITEMS:
        k = item["key"]
        if k in entry_map:
            entry_map[k].update(item)
            updated += 1
        else:
            entries.append(item)
            entry_map[k] = item
            added += 1

    with open(LOGICAL_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Updated part1_logical.json: {added} added, {updated} updated. Total: {len(entries)}")


if __name__ == "__main__":
    update()
