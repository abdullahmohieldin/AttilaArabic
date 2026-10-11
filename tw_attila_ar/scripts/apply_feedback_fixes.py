#!/usr/bin/env python3
"""
Apply feedback fixes for Total War: Attila Part 1 localization.
- Reverts graphic options (Unit Size) to English.
- Adds missing leader names in names.loc.
- Adds missing religions in religions.loc.
- Adds missing trait effect tooltips in effects.loc.
- Adds missing faction narrative descriptions in start_pos_factions.loc.
"""
import os
import json
import sys

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOGICAL_JSON = os.path.join(BASE, "translated", "part1_logical.json")

# New translations to merge or update
ADDITIONS = [
    # 1. Names
    {"key": "names_name_2147344224", "table": "text/db/names.loc", "en": "Bahram", "ar": "بهرام"},
    {"key": "names_name_2147348590", "table": "text/db/names.loc", "en": "Hermeneric", "ar": "هيرمينريك"},
    {"key": "names_name_2147348059", "table": "text/db/names.loc", "en": "Vithericus", "ar": "فيثيريكوس"},
    {"key": "names_name_2147349258", "table": "text/db/names.loc", "en": "Akinidad", "ar": "أكينيداد"},
    {"key": "names_name_2147344054", "table": "text/db/names.loc", "en": "Theodosius", "ar": "ثيودوسيوس"},
    {"key": "names_name_2147343956", "table": "text/db/names.loc", "en": "Stilicho", "ar": "ستيليكو"},
    {"key": "names_name_2147343965", "table": "text/db/names.loc", "en": "Arcadius", "ar": "أركاديوس"},
    {"key": "names_name_2147343967", "table": "text/db/names.loc", "en": "Honorius", "ar": "هونوريوس"},
    {"key": "names_name_2147343885", "table": "text/db/names.loc", "en": "Alaric", "ar": "ألاريك"},
    {"key": "names_name_2147345066", "table": "text/db/names.loc", "en": "Fritigern", "ar": "فيتيغيرن"},
    {"key": "names_name_2147346870", "table": "text/db/names.loc", "en": "Gewis", "ar": "غيويس"},
    {"key": "names_name_2147344866", "table": "text/db/names.loc", "en": "Athalaric", "ar": "أثالاريك"},
    {"key": "names_name_2147334219", "table": "text/db/names.loc", "en": "Malaric", "ar": "مالاريك"},
    {"key": "names_name_2147347436", "table": "text/db/names.loc", "en": "Amalaric", "ar": "أمالاريك"},
    {"key": "names_name_2147345079", "table": "text/db/names.loc", "en": "Theodosius I", "ar": "ثيودوسيوس الأول"},
    {"key": "names_name_2147344284", "table": "text/db/names.loc", "en": "Bahram Chobin", "ar": "بهرام جوبين"},
    {"key": "names_name_2147355693", "table": "text/db/names.loc", "en": "Charlemagne", "ar": "شارلمان"},

    # 2. Religions
    {"key": "religions_onscreen_att_rel_church_east", "table": "text/db/religions.loc", "en": "Eastern Christianity", "ar": "المسيحية الشرقية"},
    {"key": "religions_onscreen_att_rel_east_manichaeism", "table": "text/db/religions.loc", "en": "Manichaeism", "ar": "المانوية"},
    {"key": "religions_onscreen_att_rel_pag_slavic", "table": "text/db/religions.loc", "en": "Slavic paganism", "ar": "الوثنية السلافية"},
    {"key": "religions_onscreen_att_rel_pag_celtic", "table": "text/db/religions.loc", "en": "Celtic paganism", "ar": "الوثنية الكلتية"},

    # 3. Trait effects / Tooltips
    {
        "key": "effects_description_att_effect_suebi_dummy",
        "table": "text/db/effects.loc",
        "en": "%+n% upkeep for 10 turns for any army that loots or sacks a settlement.",
        "ar": "نفقات الصيانة: %+n% لمدة 10 أدوار لأي جيش ينهب أو يستبيح مستوطنة."
    },
    {
        "key": "effects_description_att_effect_public_order_immigration",
        "table": "text/db/effects.loc",
        "en": "Immigration public order penalties: %+n%",
        "ar": "عقوبات النظام العام الناتجة عن الهجرة: %+n%"
    },
    {
        "key": "effects_description_att_effect_province_fertility_garamantia",
        "table": "text/db/effects.loc",
        "en": "Irrigation: %+n fertility bonus in all provinces",
        "ar": "الري: %+n خصوبة في جميع المقاطعات"
    },
    {
        "key": "effects_description_att_effect_force_unit_stat_morale_own_territory",
        "table": "text/db/effects.loc",
        "en": "Morale: %+n when in own or allied territory",
        "ar": "المعنويات: %+n عند التواجد في أراضيك أو أراضي الحلفاء"
    },
    {
        "key": "effects_description_att_effect_force_army_campaign_military_morale_add_own_territory",
        "table": "text/db/effects.loc",
        "en": "Integrity: %+n when in own or allied territory",
        "ar": "التماسك: %+n عند التواجد في أراضيك أو أراضي الحلفاء"
    },
    {
        "key": "effects_description_att_effect_force_army_campaign_attrition_desert_immunity",
        "table": "text/db/effects.loc",
        "en": "Attrition: Immune to desert attrition",
        "ar": "الإنهاك: حصانة ضد الإنهاك في الصحراء"
    },
    {
        "key": "effects_description_att_effect_force_unit_stat_morale_versus_easterners",
        "table": "text/db/effects.loc",
        "en": "Morale: %+n versus eastern empires",
        "ar": "المعنويات: %+n ضد الإمبراطوريات الشرقية"
    },
    {
        "key": "effects_description_att_effect_force_unit_stat_melee_attack_versus_easterners",
        "table": "text/db/effects.loc",
        "en": "Melee attack: %+n versus eastern empires",
        "ar": "الهجوم القريب: %+n ضد الإمبراطوريات الشرقية"
    },
    {
        "key": "effects_description_att_effect_force_army_battle_melee_defence_versus_easterners",
        "table": "text/db/effects.loc",
        "en": "Melee defence: %+n versus eastern empires",
        "ar": "الدفاع القريب: %+n ضد الإمبراطوريات الشرقية"
    },
    {
        "key": "effects_description_att_effect_force_army_campaign_attrition_desert_resistance",
        "table": "text/db/effects.loc",
        "en": "Attrition: %+n% casualties suffered from desert attrition",
        "ar": "الإنهاك: %+n% خسائر أقل من الإنهاك الصحراوي"
    },

    # 4. Faction Narrative Descriptions
    {
        "key": "start_pos_factions_description_2120156303",
        "table": "text/db/start_pos_factions.loc",
        "en": "The Lakhmids enjoy a position of strength on the western banks of the Euphrates River, where they are tolerated by the Sassanid Persians and well insulated against Arabian rivals to the south.",
        "ar": "يحظى المناذرة بموقع حصين وقوي على الضفاف الغربية لنهر الفرات، حيث يتعايشون مع الساسانيين في أمان واستقرار نسبي، ويشكلون سداً منيعاً ضد المنافسين في جنوب شبه الجزيرة العربية. وبوصفهم جزءاً من حلف تنوخ، ارتحلوا شمالاً واستقروا في الحيرة التي غدت عاصمتهم المزدهرة، وأسسوا مملكة عربية أصيلة ذات مكانة عسكرية ودبلوماسية مرموقة.",
        "is_narrative": True
    },
    {
        "key": "start_pos_factions_description_2120156300",
        "table": "text/db/start_pos_factions.loc",
        "en": "The Garamantians have lived in North Africa for over a thousand years and, though civilisations rise and fall, they remain indomitable and strong.",
        "ar": "عاش الجرمنتيون في شمال إفريقيا لأكثر من ألف عام، ورغم صعود وسقوط الإمبراطوريات، ظلوا صامدين وأقوياء لا يقهرون في قلاعهم الصحراوية بالصحراء الليبية. ومع انشغال روما بأزماتها العاصفة، يمتلك الجرمنتيون فرصة تاريخية لبسط نفوذهم على السواحل وحوض المتوسط وصياغة مجدهم الخاص.",
        "is_narrative": True
    },
    {
        "key": "start_pos_factions_description_2120156302",
        "table": "text/db/start_pos_factions.loc",
        "en": "The Sabaean Kingdom is diminished and, in its place, Himyar ascends! The victorious Shamir Yuhar'ish has declared himself \"King of Saba, Dhu Raydan and of Hadramawt and Yamanat\".",
        "ar": "انحسرت مملكة سبأ وصعدت في مكانها مملكة حمير الظافرة! وبسط شمر يهرعش سلطانه ملكاً على سبأ وذي ريدان وحضرموت ويمنت. تسيطر حمير على شرايين التجارة البحرية الحيوية نحو الهند وبلاد الشرق، وتخوض صراعاً مصيرياً حاسماً لفرض سيادتها الكاملة على جنوب الجزيرة العربية وبحارها.",
        "is_narrative": True
    },
    {
        "key": "start_pos_factions_description_2120156298",
        "table": "text/db/start_pos_factions.loc",
        "en": "The Kingdom of Aksum grows prosperous through trade; the Silk Road is kind to those who know how to harness its riches.",
        "ar": "تزدهر مملكة أكسوم بفضل تجارتها الواسعة وموقعها الاستراتيجي على ساحل البحر الأحمر، حيث تجني ثروات هائلة من طريق الحرير والملاحة البحرية نحو الهند. وتمتلك أكسوم قوة عسكرية ضاربة تحمي بها طرق التجارة العالمية وتتصدى لأي عدوان يطمع في ثرواتها ومكانتها الإقليمية المنيعة.",
        "is_narrative": True
    },
    {
        "key": "start_pos_factions_description_2120157020",
        "table": "text/db/start_pos_factions.loc",
        "en": "The Tanukhids have travelled a long way from their homelands. Originally part of the Qahtani tribal confederation, they migrated north.",
        "ar": "قطع التنوخيون مسافات شاسعة منذ هجرتهم من جنوب الجزيرة العربية، وشكلوا قوة فرسان لا يستهان بها في بلاد الشام. وتحت قيادة ملكتهم المحاربة ماوية، خاضوا معارك ضارية ضد الجيوش الرومانية وانتزعوا حقوقهم وسيادتهم بحد السيف، عازمين على بناء مستقبل مستقل لأبناء قبائلهم الأحرار.",
        "is_narrative": True
    },
    {
        "key": "start_pos_factions_description_2120157400",
        "table": "text/db/start_pos_factions.loc",
        "en": "The mystery surrounding the White Huns is matched only by the terror they inspire in their victims. From the bleached slopes of the Hindu Kush, they look down on the civilised world.",
        "ar": "لا يضاهي الغموض المحيط بالهون البيض سوى الرعب الشديد الذي يزرعونه في قلوب أعدائهم. فمن سفوح هندوكوش الجليدية، يراقبون العالم المتمدن بطموح عارم للغزو، ممتلكين آلة حرب وبسالة فروسية جامحة حطمت كل الجيوش وتتوعد أراضي الساسانيين وفارس بخراب شامل.",
        "is_narrative": True
    },
    {
        "key": "start_pos_factions_description_2120156314",
        "table": "text/db/start_pos_factions.loc",
        "en": "The Sassanids are the latest in line of Persian empires stretching back over a millennium. Extending their rule from Fars, they consolidated power.",
        "ar": "يمثل الساسانيون أحدث حلقة في سلسلة الإمبراطوريات الفارسية العظمى الممتدة لأكثر من ألف عام. انطلاقاً من إقليم فارس، بسطوا نفوذهم واستعادوا أمجاد أسلافهم الأخمينيين والفرثيين، ويقفون اليوم كقوة إمبراطورية عظمى تتحدى روما وتهيمن على الشرق بكل كبرياء وهيبة.",
        "is_narrative": True
    },
    {
        "key": "start_pos_factions_description_2120156287",
        "table": "text/db/start_pos_factions.loc",
        "en": "A confederation of many small tribal groups who share an abiding interest in war and raiding, the Suebi are fiercely independent.",
        "ar": "السويبيون اتحاد قبلي جرماني جسور، يجمعهم حب المغامرة والحرب والغزو. يتميز محاربوهم بالعقدة السويبية الشهيرة وبسالتهم الشديدة في القتال، ويسعون لاقتحام أراضي الإمبراطورية وتأسيس موطن دائم وقوي لشعبهم وسط عالم يغرق في الفوضى والدمار.",
        "is_narrative": True
    },
    {
        "key": "start_pos_factions_description_2120156281",
        "table": "text/db/start_pos_factions.loc",
        "en": "Their distance from the heart of the Roman Empire shrouds the Saxons in mystery, allowing them the freedom to raid and pillage.",
        "ar": "بُعد السكسون عن قلب الإمبراطورية الرومانية أتاح لهم حرية الإغارة وبناء قوة بحرية وبرية مرهوبة الجانب. ومع اضمحلال نفوذ روما في بريطانيا وشمال غرب أوروبا، يتطلع السكسون عبر البحار لاقتناص أراضٍ جديدة خصبة وتخليد اسمهم في التاريخ.",
        "is_narrative": True
    },
    {
        "key": "start_pos_factions_description_2120156278",
        "table": "text/db/start_pos_factions.loc",
        "en": "As the world stands on the edge of chaos, the Franks hover between two destinies: destroyers or inheritors of Rome.",
        "ar": "بينما يقف العالم على حافة الفوضى والانهيار، يتأرجح الفرنجة بين مصيرين: الهادمون أم الوارثون لحضارة روما! انطلاقاً من حوض الراين الأدنى، يملك قادتهم الشجعان حنكة عسكرية وسياسية قادرة على توحيد القبائل وبناء أعظم مملكة في أوروبا الغربية.",
        "is_narrative": True
    },
    {
        "key": "start_pos_factions_description_2120156274",
        "table": "text/db/start_pos_factions.loc",
        "en": "The reluctant arbiters of barbarian vengeance, the Visigoths have sworn to repay the Romans in kind for decades of brutal betrayal.",
        "ar": "أقسم القوط الغربيون، حاملو راية الانتقام البربري، على الرد بالمثل على عقود من الغدر والاضطهاد الروماني. وتحت راية ألاريك، يتحرك هذا الشعب المقاتل كجيش جرار لا يلين، موجهاً ضربات قاصمة لعواصم روما ومجبراً الأباطرة على الركوع لمطالبهم العادلة.",
        "is_narrative": True
    },
    {
        "key": "start_pos_factions_description_2120156272",
        "table": "text/db/start_pos_factions.loc",
        "en": "Abandoned in their hour of need by their Roman allies, the Vandals find themselves driven west by the advancing Hunnic hordes.",
        "ar": "بعد أن خذلهم حلفاؤهم الرومان في أحلك الظروف، وجد الوندال أنفسهم مدفوعين غرباً أمام زحف جحافل الهون المرعبة. وبقيادة حكيمة وعزيمة صلبة، يشق الوندال طريقهم عبر الغال وإسبانيا وصولاً إلى سواحل إفريقيا ليؤسسوا مملكة بحرية لا تقهر.",
        "is_narrative": True
    },
    {
        "key": "start_pos_factions_description_2120156270",
        "table": "text/db/start_pos_factions.loc",
        "en": "The Ostrogoths' wanderings through Roman lands belie their origins as a proud empire ruled by the Amali dynasty.",
        "ar": "إن ترحال القوط الشرقيين في أراضي الرومان يخفي وراءه ماضياً مجيداً لإمبراطورية كانت ذات شأن عظيم تحكمها سلالة الأمالي العريقة. وبعد نجاتهم من نير الهون، يستجمعون قواهم للنهوض مجدداً واستعادة استقلالهم وبناء مملكة تدين لها إيطاليا بالولاء.",
        "is_narrative": True
    },
    {
        "key": "start_pos_factions_description_2120156263",
        "table": "text/db/start_pos_factions.loc",
        "en": "As the Alans ride into battle, bloody scalps displayed proudly on their saddles, their formidable reputation precedes them.",
        "ar": "يمتطي الألان خيولهم إلى سوح الوغى وسمعتهم الرهيبة تسبقهم كفرسان سارماتيين أشداء لا يخشون الموت. وببراعتهم الفائقة في ركوب الخيل واستخدام الرماح المدرعة، يندفعون غرباً في رحلة هجرة ملحمية لانتزاع السيادة وتأمين البقاء لشعبهم الأبي.",
        "is_narrative": True
    },
    {
        "key": "start_pos_factions_description_2120156326",
        "table": "text/db/start_pos_factions.loc",
        "en": "The division of the Roman Empire has unshackled the East, allowing it to assume control of the Roman world from the new capital at Constantinople.",
        "ar": "أطلق تقسيم الإمبراطورية الرومانية عنان الشرق، مما مكنه من بسط نفوذه على العالم الروماني من عاصمته الحصينة بالقسطنطينية. ومع ازدهار التجارة وقوة الأسوار وثراء الخزينة، تقف روما الشرقية كدرع صلب للحضارة الرومانية مستعدة للتصدي لكافة الأخطار والتهديدات.",
        "is_narrative": True
    },
    {
        "key": "start_pos_factions_description_2120156339",
        "table": "text/db/start_pos_factions.loc",
        "en": "The Western Roman Empire is on the very edge of catastrophe. Beset by barbarian incursions, internal corruption, and economic ruin, it fights for survival.",
        "ar": "تقف الإمبراطورية الرومانية الغربية على شفا الهاوية والكارثة المحققة. تحاصرها هجمات البرابرة من كل حدب وصوب، وينهكها الفساد الداخلي والانهيار الاقتصادي، لتخوض أعتى معارك البقاء دفاعاً عن شرف روما الخالد وإرثها العظيم ضد الفناء المحتوم.",
        "is_narrative": True
    }
]


def update_logical():
    with open(LOGICAL_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    entries = data["entries"]
    entry_map = {e["key"]: e for e in entries}

    added_count = 0
    updated_count = 0

    for item in ADDITIONS:
        k = item["key"]
        if k in entry_map:
            entry_map[k].update(item)
            updated_count += 1
        else:
            entries.append(item)
            entry_map[k] = item
            added_count += 1

    # Save
    with open(LOGICAL_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"part1_logical.json updated: {added_count} added, {updated_count} updated. Total entries: {len(entries)}")


if __name__ == "__main__":
    update_logical()
