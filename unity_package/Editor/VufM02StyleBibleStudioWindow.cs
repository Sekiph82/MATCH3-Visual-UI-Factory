// M02 original five-theme SOURCE Style Bible review. Native Editor swatches,
// device tokens and art-sheet requirements. No imported art, approvals, game
// actions, paid fonts, source mutation, scene/prefab save or runtime packaging.
using System;
using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    public sealed class VufM02StyleBibleStudioWindow : EditorWindow
    {
        internal const string ExpectedStage =
            "DRAFT_IDENTITY_CONTRACT_OWNER_ART_NOT_PROVIDED";
        private const string Root =
            "Packages/com.match3.visual-factory/Editor/Resources/";
        private static readonly string[] Profiles = {
            "Coral_Rescue", "Garage_Legends", "Dino_Islands",
            "The_Fractured_Realms", "Wonder_Pop"
        };
        private static readonly string[] RequiredStates = {
            "idle", "greet", "celebrate", "concerned", "action"
        };
        [Serializable]
        internal sealed class Approval
        {
            public bool all_approved, original_art_received,
                font_rights_verified, device_visual_qa_verified,
                engine_lfx_gameplay_verified, production_release_allowed;
        }
        [Serializable]
        internal sealed class Typography
        {
            public int hero, page_title, section, body, caption, button;
        }
        [Serializable]
        internal sealed class Grid
        {
            public int columns_phone, columns_tablet, gutter_dp;
            public int outer_margin_phone_dp, outer_margin_tablet_dp;
        }
        [Serializable]
        internal sealed class Device
        {
            public string id;
            public int width_dp, height_dp, min_safe_top_dp, min_safe_bottom_dp;
        }
        [Serializable]
        internal sealed class Common
        {
            public int schema_version, min_touch_dp;
            public string stage, reference_style_document, font_license_status;
            public float min_body_contrast_ratio, min_large_text_contrast_ratio;
            public Typography typography_dp;
            public Grid grid;
            public Device[] screen_modes;
            public string[] responsive_rules;
            public Approval owner_auth;
        }
        [Serializable]
        internal sealed class Identity
        {
            public string id, bible_title, creative_direction, surface_material,
                mascot_role, world_restoration_identity, particle_language,
                lighting_finish, right_to_use;
            public string[] symbol_silhouettes,
                original_reference_requirements, required_character_poses,
                master_sheet_slots, forbidden_visual_patterns, ui_components;
        }
        [Serializable]
        internal sealed class Catalog
        {
            public Common common;
            public Identity[] profiles;
        }

        private Catalog catalog;
        private int profileIndex, deviceIndex;
        private string status = "Load five SOURCE art-direction contracts. No original art is supplied.";
        private Vector2 scroll;
        private Texture2D ownerPreview;

        [MenuItem("Tools/MATCH3/M02 Five-Game Style Bible and Art Identity Studio")]
        public static void Open()
        {
            var w = GetWindow<VufM02StyleBibleStudioWindow>("M02 Style Bibles");
            w.minSize = new Vector2(650, 700);
            w.Show();
        }

        internal static Catalog ValidateAndParse(string source)
        {
            if (String.IsNullOrWhiteSpace(source) || source.Length > 128 * 1024)
                throw new ArgumentException("Source Style Bible JSON missing or too large");
            var data = JsonUtility.FromJson<Catalog>(source);
            if (data == null || data.common == null ||
                data.common.schema_version != 1 ||
                data.common.stage != ExpectedStage ||
                data.common.reference_style_document !=
                    "factory/visual_director/style_profiles.v1.json" ||
                data.common.font_license_status !=
                    "SYSTEM_FALLBACK_ONLY_UNTIL_CREATOR_PROOF" ||
                data.common.min_touch_dp < 44 ||
                data.common.min_body_contrast_ratio < 4.5f ||
                data.common.min_large_text_contrast_ratio < 3f ||
                data.common.owner_auth == null ||
                data.common.owner_auth.all_approved ||
                data.common.owner_auth.original_art_received ||
                data.common.owner_auth.font_rights_verified ||
                data.common.owner_auth.device_visual_qa_verified ||
                data.common.owner_auth.engine_lfx_gameplay_verified ||
                data.common.owner_auth.production_release_allowed ||
                data.common.typography_dp == null ||
                data.common.typography_dp.body < 16 ||
                data.common.typography_dp.button < 16 ||
                data.common.grid == null ||
                data.common.grid.columns_phone != 4 ||
                data.common.grid.columns_tablet != 8 ||
                data.common.grid.gutter_dp < 12 ||
                data.common.screen_modes == null ||
                data.common.screen_modes.Length != 4 ||
                data.common.responsive_rules == null ||
                data.common.responsive_rules.Length < 6 ||
                data.profiles == null || data.profiles.Length != 5)
                throw new ArgumentException("Forged M02 preview, UI readability or owner art permissions");
            string[] screens = {
                "compact_phone","tall_phone","large_phone","portrait_tablet"
            };
            for (int i=0;i<data.common.screen_modes.Length;i++)
            {
                var d=data.common.screen_modes[i];
                if (d==null || d.id!=screens[i] || d.width_dp < 320 ||
                    d.height_dp < 568 || d.min_safe_top_dp < 0 ||
                    d.min_safe_bottom_dp < 0 || d.min_safe_top_dp +
                    d.min_safe_bottom_dp >= d.height_dp)
                    throw new ArgumentException("Invalid original device geometry");
            }
            var unique=new HashSet<string>(StringComparer.Ordinal);
            for (int i=0;i<data.profiles.Length;i++)
            {
                var p=data.profiles[i];
                if (p==null || p.id!=Profiles[i] || !unique.Add(p.id) ||
                    String.IsNullOrWhiteSpace(p.bible_title) ||
                    String.IsNullOrWhiteSpace(p.creative_direction) ||
                    String.IsNullOrWhiteSpace(p.surface_material) ||
                    String.IsNullOrWhiteSpace(p.mascot_role) ||
                    p.right_to_use !=
                    "NO_OWNER_ORIGINAL_ASSET_OR_FONT_LICENCE_EVIDENCE" ||
                    p.symbol_silhouettes==null || p.symbol_silhouettes.Length!=5 ||
                    p.original_reference_requirements==null ||
                    p.original_reference_requirements.Length<6 ||
                    p.master_sheet_slots==null || p.master_sheet_slots.Length<5 ||
                    p.required_character_poses==null ||
                    !p.required_character_poses.SequenceEqual(RequiredStates) ||
                    p.forbidden_visual_patterns==null ||
                    p.forbidden_visual_patterns.Length!=2 ||
                    p.ui_components==null || p.ui_components.Length!=10)
                    throw new ArgumentException("Five distinct original draft identities required");
            }
            return data;
        }

        internal static float Contrast(Color a, Color b)
        {
            Func<float, float> linear = v =>
                v <= .04045f ? v / 12.92f :
                Mathf.Pow((v + .055f) / 1.055f, 2.4f);
            Func<Color, float> lum = c =>
                .2126f * linear(c.r) + .7152f * linear(c.g) +
                .0722f * linear(c.b);
            float x=lum(a),y=lum(b);
            return (Mathf.Max(x,y) + .05f) / (Mathf.Min(x,y) + .05f);
        }

        internal static void ValidateOriginalPalette(string profileId)
        {
            var style=VufScreenCatalog.LoadStyle(profileId);
            var palette=style.palettes;
            var text=VufScreenCatalog.ParseColor(palette.text,"text");
            var surface=VufScreenCatalog.ParseColor(palette.surface,"surface");
            var background=VufScreenCatalog.ParseColor(palette.background,"background");
            var cta=VufScreenCatalog.ParseColor(palette.cta,"cta");
            var label=VufScreenCatalog.ParseColor(palette.cta_label,"cta_label");
            if (Contrast(text, surface)<4.5f || Contrast(text,background)<4.5f ||
                Contrast(label,cta)<4.5f)
                throw new InvalidOperationException(
                    "Actual inherited five-theme draft palette failed AA text contrast");
        }

        private void OnEnable() { TryLoad(); }
        private void TryLoad()
        {
            try
            {
                var source=AssetDatabase.LoadAssetAtPath<TextAsset>(
                    Root+"m02_identity_catalog.v1.json");
                if(source==null)
                    throw new InvalidOperationException("original source M02 catalogue missing");
                var loaded=ValidateAndParse(source.text);
                foreach (var p in Profiles) ValidateOriginalPalette(p);
                catalog=loaded;
                status="Source-only M02 Style Bible valid; original art + rights STILL MISSING.";
            }
            catch(Exception ex) { catalog=null; status="BLOCKED: "+ex.Message; }
        }

        private static void ColorSwatch(string label, string html)
        {
            var swatch=VufScreenCatalog.ParseColor(html,label);
            EditorGUILayout.BeginHorizontal();
            GUILayout.Label(label,GUILayout.Width(102));
            var r=GUILayoutUtility.GetRect(70,24,GUILayout.ExpandWidth(false));
            EditorGUI.DrawRect(r,swatch);
            GUILayout.Label(html,GUILayout.Width(88));
            EditorGUILayout.EndHorizontal();
        }

        private static void Section(string label,string[] items)
        {
            EditorGUILayout.Space();
            EditorGUILayout.LabelField(label,EditorStyles.boldLabel);
            foreach(var item in items)
                EditorGUILayout.LabelField("• "+item,EditorStyles.wordWrappedLabel);
        }

        private void OnGUI()
        {
            EditorGUILayout.LabelField("M02 | Five Original Art-Direction Contracts",
                EditorStyles.boldLabel);
            EditorGUILayout.HelpBox(
                "DRAFT SOURCE DESIGN SYSTEM, not five commissioned/owner-licensed " +
                "master artworks. All human art rights, actual font samples, " +
                "device GUI and production release still OPEN.", MessageType.Warning);
            if(GUILayout.Button("Re-check actual source palettes and identity contracts"))
                TryLoad();
            if (catalog==null)
            {
                EditorGUILayout.HelpBox(status,MessageType.Error);
                return;
            }
            profileIndex=EditorGUILayout.Popup("Game Style Bible",profileIndex,Profiles);
            var p=catalog.profiles[profileIndex];
            var common=catalog.common;
            deviceIndex=EditorGUILayout.Popup("Draft device grid",deviceIndex,
                common.screen_modes.Select(d=>d.id).ToArray());
            var mode=common.screen_modes[deviceIndex];
            scroll=EditorGUILayout.BeginScrollView(scroll);
            EditorGUILayout.LabelField(p.bible_title,EditorStyles.largeLabel);
            EditorGUILayout.LabelField(p.creative_direction,EditorStyles.wordWrappedLabel);
            EditorGUILayout.LabelField("Material: "+p.surface_material+
                " | Guide: "+p.mascot_role,EditorStyles.wordWrappedLabel);
            EditorGUILayout.LabelField(p.lighting_finish,EditorStyles.wordWrappedLabel);
            var palette=VufScreenCatalog.LoadStyle(p.id).palettes;
            ColorSwatch("Background",palette.background);
            ColorSwatch("Surface",palette.surface);
            ColorSwatch("Accent",palette.accent);
            ColorSwatch("Primary CTA",palette.cta);
            ColorSwatch("CTA Label",palette.cta_label);
            ColorSwatch("Body Text",palette.text);
            EditorGUILayout.LabelField("Measured inherited palette contrasts:");
            var text=VufScreenCatalog.ParseColor(palette.text,"text");
            var surface=VufScreenCatalog.ParseColor(palette.surface,"surface");
            var cta=VufScreenCatalog.ParseColor(palette.cta,"cta");
            var label=VufScreenCatalog.ParseColor(palette.cta_label,"cta_label");
            EditorGUILayout.LabelField("Text/surface: "+
                Contrast(text,surface).ToString("F2")+":1");
            EditorGUILayout.LabelField("CTA label/button: "+
                Contrast(label,cta).ToString("F2")+":1");
            EditorGUILayout.LabelField("Typography tokens (dp): "+
                "Hero "+common.typography_dp.hero+
                ", Title "+common.typography_dp.page_title+
                ", Body "+common.typography_dp.body+
                ", Button "+common.typography_dp.button);
            EditorGUILayout.LabelField("Grid source preview: "+
                mode.width_dp+"×"+mode.height_dp+" dp"+
                " • Top safe "+mode.min_safe_top_dp+
                " • Bottom safe "+mode.min_safe_bottom_dp);
            float usable=mode.width_dp-2*(mode.id=="portrait_tablet" ?
                common.grid.outer_margin_tablet_dp :
                common.grid.outer_margin_phone_dp);
            var cols=mode.id=="portrait_tablet" ? 8 : 4;
            float width=(usable-(cols-1)*common.grid.gutter_dp)/cols;
            EditorGUILayout.LabelField("Column width: "+width.ToString("F1")+
                " dp • Min button "+common.min_touch_dp+
                " dp (simulated layout only)");
            Section("Five independently identifiable symbol silhouettes",
                p.symbol_silhouettes);
            Section("Original art / icon / environment master requirements",
                p.original_reference_requirements);
            Section("Character pose consistency (must be owner supplied)",
                p.required_character_poses);
            Section("Master identity sheets MISSING until original art",
                p.master_sheet_slots);
            Section("Original creator/children safety restrictions",
                p.forbidden_visual_patterns);
            Section("Shared semantic UI component set",
                p.ui_components);
            EditorGUILayout.Space();
            EditorGUILayout.HelpBox(
                "No owner-licenced original characters/vehicle/creatures/runes " +
                "or font asset is attached to this token studio. " +
                "Use approved original external intake + human visual review.",
                MessageType.Info);
            EditorGUILayout.EndScrollView();
        }
    }
}
