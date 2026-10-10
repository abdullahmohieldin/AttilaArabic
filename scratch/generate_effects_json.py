#!/usr/bin/env python3
"""Build comprehensive translations for all 109 faction trait effect tooltip lines."""
import json

# Full dictionary mapping of effect key to Arabic translation
# Format tokens like %+n%, %+n, % must be preserved exactly
EFFECTS_AR = {
    # 0..10
    "effects_description_att_faction_trait_venedi_growth": "النمو: %+n",
    "effects_description_att_effect_faction_trait_roman_east_economic_powerhouse_2_trade_tarrifs": "تعريفات التجارة: %+n%",
    "effects_description_att_faction_trait_sclaveni_dummy": "المعنويات، والدفاع والهجوم عن قرب: %+n والضرر عن قرب: +20% عند قتال الفصائل البدوية",
    "effects_description_bel_faction_trait_roman_expedition_3_integrity": "حاشية القائد: %+n تماسك الجيش",
    "effects_description_att_effect_faction_trait_norse_geats_cold_blood_2_immune_snow_attrition": "مناعة ضد خسائر الثلوج",
    "effects_description_att_faction_trait_antes_morale_grassland_desert_plains": "ضرر القتال عن قرب: %+n عند القتال في السهول العشبية أو الصحراوية",
    "effects_description_att_faction_trait_antes_attack_grassland_desert_plains": "المعنويات: %+n عند القتال في السهول العشبية أو الصحراوية",
    "effects_description_att_faction_trait_antes_damage_grassland_desert_plains": "الهجوم عن قرب: %+n عند القتال في السهول العشبية أو الصحراوية",
    "effects_description_att_faction_trait_garamantes_conversion": "%+n% وقت تحويل سلسلة المباني الرئيسية",
    "effects_description_att_faction_trait_himyar_no_replenishment": "مخربو الصحراء: يمنع تجنيد وتعويض القوات الأجنبية في المناطق التي تتواجد بها الجيوش",
    "effects_description_att_faction_trait_tanukhids_muster_stance": "صفوف متزايدة: وضع الغارة يمنح وحدات ميليشيا تمرد مجانية",

    # 11..20
    "effects_description_att_effect_faction_trait_barbarian_saxon_saxon_shore_1_income_for_settlement_damage": "الدخل: %+n مقابل كل 10% ضرر يلحق بالمستوطنات أثناء المعركة",
    "effects_description_att_effect_faction_trait_eastern_grand_school_1_sanitation_per_province_capital": "الصحة العامة: %+n لكل عاصمة ولاية تسيطر عليها",
    "effects_description_att_effect_faction_trait_barbarian_burgundian_1": "عزيمة جليدية: %+n% تعويض خسائر الوحدات",
    "effects_description_att_effect_faction_trait_barbarian_burgundian_2": "معيشة قاسية: %+n طعام لكل إقليم ذي خصوبة ضعيفة",
    "effects_description_att_effect_faction_trait_norse_danes_seaborn_1_immune_seasickness": "مناعة ضد دوار البحر",
    "effects_description_att_faction_trait_lakhmids_sassanid_units": "إمكانية تجنيد وحدات ساسانية في المستوطنات التي تحوي مباني عسكرية ساسانية",
    "effects_description_att_effect_faction_trait_migrators_great_migration_growth": "النمو: %+n عند بدء الهجرة أو الاستقرار",
    "effects_description_att_effect_faction_trait_migrators_vandals_pirate_raiders_2_income_from_raid_sack": "الدخل: %+n% من الغارات والنهب",
    "effects_description_att_effect_faction_trait_steppe_horses": "خيول النخبة: %+n% سرعة المعركة لمجندي سلاح الفرسان",
    "effects_description_att_effect_faction_trait_norse_danes_seaborn_2_immune_sea_attrition": "مناعة ضد خسائر أعالي البحار",

    # 21..30
    "effects_description_att_effect_faction_trait_nomads_scourge_christian_fear": "معنويات العدو: %+n عند قتال الفصائل المسيحية",
    "effects_description_bel_faction_trait_franks_cav_xp": "إرث ألاني: %+n خبرة لوحدات الفرسان عند التجنيد",
    "effects_description_att_effect_faction_trait_migrators_visigoths_blood_money_2_income_from_migrate": "الدخل: %+n% أثناء الهجرة عبر الأراضي الرومانية",
    "effects_description_cha_faction_trait_asturias_raze_abandon": "إمكانية تدمير المستوطنات والتخلي عنها",
    "effects_description_att_effect_faction_trait_migrators_ostrogoths_honorary_romans_2_roman_unit_recruitment": "إمكانية تجنيد وحدات رومانية في المستوطنات التي تحوي مباني عسكرية رومانية",
    "effects_description_att_faction_trait_lakhmids_puppet_wealth": "سلام مدعوم: %+n ثروة لكل دورة طالما في سلام مع الساسانيين",
    "effects_description_att_effect_faction_trait_roman_west_plurality_1_upkeep_per_foreign_unit": "تكاليف الصيانة: %+n% لكل وحدة غير رومانية في الجيش",
    "effects_description_bel_faction_trait_vandals_2_breakers_success": "خبراء التخريب: %+n% لفرصة نجاح عمليات التخريب",
    "effects_description_att_effect_faction_trait_nomads_huns_horsemen_1_conquest_growth": "الغزو: %+n نمو ناتج عن تدمير المستوطنات",
    "effects_description_att_effect_faction_trait_barbarian_saxon_saxon_shore_2_morale_for_raiding": "التماسك: %+n عند شن الغارات",

    # 31..40
    "effects_description_att_effect_faction_trait_norse_geats_cold_blood_1_morale_in_winter": "المعنويات: %+n عند القتال خلال فصل الشتاء",
    "effects_description_att_effect_faction_trait_nomads_huns_horsemen_3_famine_food_drain": "المجاعة: %+n استهلاك الطعام في الولايات التي يتواجد بها الحشد",
    "effects_description_att_faction_trait_slavs_defence_against_nomads": "الدفاع عن قرب: %+n عند قتال الفصائل البدوية",
    "effects_description_bel_faction_trait_vandals_battle_morale": "صيحة الحرب: %+n لمعنويات الوحدات داخل أراضيها أو أراضي الحلفاء",
    "effects_description_att_faction_trait_celts_dummy_1": "-15% تقليل سرعة الحركة أثناء وضع الغارة",
    "effects_description_bel_faction_trait_visigoths_conversion": "إقناع راسخ: معدل مرتفع للتحول الديني في جميع الولايات الخاضعة",
    "effects_description_att_faction_trait_himyar_fatigue": "معدل الإرهاق: %+n% لجميع الوحدات",
    "effects_description_att_faction_trait_antes_defence_forest": "الدفاع عن قرب: %+n عند القتال داخل الغابات",
    "effects_description_att_faction_trait_antes_defence_grassland_desert_plains": "الهجوم عن قرب: %+n عند القتال في السهول العشبية أو الصحراوية",
    "effects_description_bel_faction_trait_franks_research": "العلم والمعرفة: %+n% لمعدل البحث العلمي",

    # 41..50
    "effects_description_att_faction_trait_tanukhids_food": "حشد ضارٍ: الحصول على الطعام يتم فقط من معارك المستوطنات أثناء وضع الحشد",
    "effects_description_att_faction_trait_slavs_ambush_defence": "الدفاع عن قرب: %+n أثناء الكمائن",
    "effects_description_att_effect_faction_trait_barbarian_langobard_1": "المحررون: مضاعفة تعويض خسائر الوحدات عند دمج الأسرى بعد المعركة",
    "effects_description_att_effect_faction_trait_barbarian_langobard_2": "غضب يد الخالق: %+n لمعنويات الوحدات عند قتال جيوش الديانات الأخرى",
    "effects_description_att_effect_faction_trait_norse_raiders_income_from_sack_loot_raid": "الدخل: %+n% من النهب والسلب والغارات",
    "effects_description_att_effect_faction_trait_suebi_horde_buildings": "تكلفة تشييد مباني الحشد: %+n%",
    "effects_description_att_effect_faction_trait_norse_jutes_despoilers_2_income_from_raze": "الدخل: %+n% من تدمير المستوطنات وتسويتها بالأرض",
    "effects_description_att_effect_faction_trait_migrators_alans_sarmatian_horsemanship_1_cavalry_xp_gain": "معدل اكتساب خبرة المعارك: %+n%% لوحدات الفرسان",
    "effects_description_att_faction_trait_celts_raiding_1": "دخل الغارات في الأراضي المحايدة: %+n%",
    "effects_description_att_faction_trait_celts_raiding_2": "دخل الغارات في أراضي الأعداء: %+n%",

    # 51..60
    "effects_description_att_faction_trait_sands_sanitation": "لفح الصحراء: %+n الصحة العامة",
    "effects_description_att_faction_trait_sands_conversion": "رياح التغيير: %+n لمعدل التحول الديني",
    "effects_description_bel_faction_trait_ostrogths_roman_diplomacy": "التشكك الروماني: تراجع العلاقات الدبلوماسية مع الإمبراطورية الرومانية",
    "effects_description_att_effect_faction_trait_barbarian_new_kingdoms_building_conversion": "معدل تحويل المباني: %+n%",
    "effects_description_att_faction_trait_venedi_farm_income": "الدخل: %+n% من المزارع",
    "effects_description_bel_faction_trait_visigoths_tributary_income": "دية الدم: %+n من تأسيس الدول التابعة",
    "effects_description_att_effect_faction_trait_eastern_sassanid_king_of_kings_1_income_from_vassals": "الدخل: %+n% جزية من الدول التابعة",
    "effects_description_att_effect_faction_trait_migrators_vandals_pirate_raiders_1_superior_naval": "إمكانية تجنيد وحدات بحرية فائقة الجودة",
    "effects_description_att_faction_trait_antes_river_dummy": "المعنويات، والدفاع والهجوم عن قرب: %+n وضرر القتال عن قرب: +20% عند خوض معركة نهرية",
    "effects_description_att_effect_faction_trait_roman_foederati_horde_levy": "إمكانية حشد وحدات من الحشود الصديقة المارة عبر الأراضي الرومانية",

    # 61..70
    "effects_description_att_faction_trait_antes_grassland_desert_plains_dummy": "المعنويات، والدفاع والهجوم عن قرب: %+n وضرر القتال: -10% عند القتال في السهول أو الحقول المفتوحة",
    "effects_description_att_faction_trait_antes_defence_river": "الدفاع عن قرب: %+n عند خوض معركة نهرية",
    "effects_description_bel_faction_trait_roman_expedition_2_stance_cost_reduction": "العزيمة الرومانية: بلا تكلفة حركة لوضعي التحصين والتخييم",
    "effects_description_att_effect_faction_trait_nomads_huns_horsemen_2_war_morale": "الحرب: %+n للتماسك مقابل كل حرب تخوضها الفصيل",
    "effects_description_bel_faction_trait_vandals_1_raiding": "القرصنة: زيادة %+n% في دخل الغارات في جميع الولايات والمناطق البحرية",
    "effects_description_att_effect_faction_trait_barbarian_alamanni_1": "زراعة بارعة: دخل زراعي إضافي في الأقاليم ذات الخصوبة الضعيفة",
    "effects_description_att_effect_faction_trait_barbarian_alamanni_2": "هيبة الملوك: %+n% لنطاق تأثير القائد العسكري",
    "effects_description_att_faction_trait_tanukhids_growth": "حشود النصر: نمو إضافي للحشد مكتسب من الانتصارات في المعارك",
    "effects_description_att_effect_faction_trait_nomads_white_huns_war_morale": "التماسك: %+n للتماسك مقابل كل حرب تخوضها الفصيل",
    "effects_description_bel_faction_trait_vandals_naval_superiority": "صنيعة البحار: إمكانية تجنيد وحدات بحرية عالية الجودة",

    # 71..80
    "effects_description_att_effect_faction_trait_eastern_sassanid_king_of_kings_2_levies_from_vassals": "مجندو الدول التابعة: %+n من كل نوع من وحدات الحشد",
    "effects_description_att_effect_faction_trait_migrators_ostrogoths_honorary_romans_1_no_resistance": "انعدام الاضطرابات عند احتلال مستوطنات الفصائل الرومانية",
    "effects_description_att_effect_faction_trait_eastern_grand_school_2_research_per_province_capital": "معدل البحث: %+n% لكل عاصمة ولاية تسيطر عليها",
    "effects_description_att_faction_trait_lakhmids_settlement_replenishment": "مدن سماوية: %+n% زيادة في تعويض خسائر الوحدات داخل المستوطنة",
    "effects_description_att_effect_faction_trait_roman_west_plurality_2_refugee_increase": "هجرة مستمرة إلى أراضي الإمبراطورية",
    "effects_description_bel_faction_trait_visigoths_tolerance": "تسامح: انعدام عقوبات النظام العام الناجمة عن الهجرة في الولايات الخاضعة",
    "effects_description_bel_faction_trait_roman_expedition_1_reclaim": "استرداد المجد: بإمكان الحملة استعادة الأقاليم وضمها للإمبراطورية الرومانية",
    "effects_description_att_faction_trait_antes_forest_dummy": "المعنويات، والدفاع والهجوم عن قرب: %+n وضرر القتال: +20% عند القتال في الغابات",
    "effects_description_att_effect_faction_trait_migrators_visigoths_blood_money_3_income_from_new_vassals": "الدخل: %+n من تأسيس الدول التابعة",
    "effects_description_att_faction_trait_slavs_damage_against_nomads": "ضرر القتال عن قرب: %+n عند قتال الفصائل البدوية",

    # 81..90
    "effects_description_att_faction_trait_slavs_attack_against_nomads": "الهجوم عن قرب: %+n عند قتال الفصائل البدوية",
    "effects_description_att_faction_trait_slavs_morale_against_nomads": "المعنويات: %+n عند قتال الفصائل البدوية",
    "effects_description_bel_faction_trait_ostrogths_2_roman_occupation": "احتلال سلمي: انعدام الاضطراب في النظام العام عند احتلال المستوطنات",
    "effects_description_att_faction_trait_axum_trade": "براعة التجارة: %+n% من دخل التجارة",
    "effects_description_att_effect_faction_trait_nomads_huns_horsemen_4_death_no_replenish": "الموت المحقق: إيقاف تعويض الخسائر للأعداء في الأقاليم التي يتواجد بها الحشد",
    "effects_description_att_faction_trait_antes_morale_river": "المعنويات: %+n عند خوض معركة نهرية",
    "effects_description_att_faction_trait_axum_mercs": "حرس التجار: %+n% لمعدل تعويض وتجدد المرتزقة المتاحين",
    "effects_description_att_faction_trait_antes_attack_river": "المعنويات: %+n عند خوض معركة نهرية",
    "effects_description_bel_faction_trait_franks_casualties": "شرف المعركة: لا عقوبة على التماسك جراء الخسائر التي تكبدها الجيش في المعركة",
    "effects_description_att_faction_trait_venedi_farms_dummy": "مزارع الفينيدي: لا تأثيرات سلبية للمزارع (على القذارة أو النظام العام)",

    # 91..100
    "effects_description_att_effect_faction_trait_migrators_alans_sarmatian_horsemanship_2_casualty_exemption": "انعدام الخسائر بعد المعركة لوحدات الفرسان المنسحبة أو المنهزمة",
    "effects_description_att_faction_trait_antes_damage_river": "الهجوم عن قرب: %+n عند خوض معركة نهرية",
    "effects_description_att_faction_trait_axum_food": "شبكة الإمداد: %+n طعام من كل طريق تجاري نشط (الحد الأقصى: 150)",
    "effects_description_att_effect_faction_trait_barbarian_franks_ferocity_1_morale_for_casualties_inflicted": "التماسك: %+n% عقوبة ناتجة عن الخسائر المتكبدة",
    "effects_description_bel_faction_trait_roman_expedition_fatigue_recovery": "تدريب بدني: %+n% لمعدل التعافي من الإرهاق",
    "effects_description_att_faction_trait_slavs_ambush_morale": "المعنويات: %+n أثناء الكمائن",
    "effects_description_att_effect_faction_trait_norse_jutes_despoilers_1_income_from_units_destroyed": "دخل إضافي مقابل كل وحدة عدوة يتم إبادتها",
    "effects_description_att_faction_trait_slavs_ambush_attack": "الهجوم عن قرب: %+n أثناء الكمائن",
    "effects_description_att_effect_faction_trait_migrators_visigoths_blood_money_1_food_from_migrate": "الطعام: %+n أثناء الهجرة عبر الأراضي الرومانية",
    "effects_description_att_effect_faction_trait_roman_east_economic_powerhouse_1_treasury_interest": "الدخل: %+n% فائدة على الخزينة في نهاية كل دورة",

    # 101..108
    "effects_description_att_faction_trait_antes_morale_forest": "ضرر القتال عن قرب: %+n عند القتال في الغابات",
    "effects_description_att_faction_trait_antes_damage_forest": "الهجوم عن قرب: %+n عند القتال في الغابات",
    "effects_description_att_faction_trait_antes_attack_forest": "المعنويات: %+n عند القتال في الغابات",
    "effects_description_att_faction_trait_venedi_industry_culture_commerce": "الدخل: %+n% من التجارة والصناعة والثقافة",
    "effects_description_att_faction_trait_himyar_marib_dam": "سد مأرب: مبنى فريد يعزز الخصوبة في العاصمة",
    "effects_description_att_faction_trait_ebdani_1": "دخل السلب والنهب: %+n%",
    "effects_description_bel_faction_trait_ostrogths_1_victory_battle_morale": "حماسة النصر: +10 معنويات لمدة 5 دورات (للجيش الرئيسي فقط) بعد الانتصار في المعركة",
    "effects_description_att_effect_faction_trait_barbarian_franks_ferocity_2_damage_for_casualties_suffered": "ضرر القتال عن قرب: %+n% مقابل كل 25% خسائر تتكبدها الوحدة",
}

with open('scratch/all_faction_trait_effects.json', 'r', encoding='utf-8') as f:
    orig = json.load(f)

entries = []
for item in orig:
    key = item['key']
    en = item['en']
    ar = EFFECTS_AR.get(key, "")
    if not ar:
        print(f"WARNING: Missing translation for {key}: {en}")
    entries.append({
        "key": key,
        "table": "text/db/effects.loc",
        "ar": ar,
        "en": en
    })

output_data = {
    "description": "Total War: ATTILA — Faction Trait Tooltip Effects Localisation (All 109 effects)",
    "entries": entries
}

with open('data/translations/faction_traits_effects.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"Successfully generated data/translations/faction_traits_effects.json with {len(entries)} entries!")
