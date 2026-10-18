// VUF-M08-006 | Disposable view-only imported TEST_ONLY image consumer.
// Accepts ONLY an already SHA-verified source Texture2D supplied by the
// M08 External Pack Sandbox. Uses Unity's SpriteRenderer as a real preview;
// symbolic M07 visual event keys are for manual inspection ONLY. Never
// connects an Engine callback, saves a Scene, modifies importers or licenses.
using System;
using UnityEngine;

namespace Match3.VisualFactory.Editor
{
    internal static class VufExternalPackViewStage
    {
        internal static GameObject Create(
            Texture2D verifiedImportedTexture, string profile,
            string assetId, string visualEvent, out Sprite ownedSprite)
        {
            ownedSprite = null;
            if (verifiedImportedTexture == null ||
                verifiedImportedTexture.width <= 0 ||
                verifiedImportedTexture.height <= 0 ||
                String.IsNullOrEmpty(assetId) ||
                !assetId.StartsWith(profile + ".", StringComparison.Ordinal))
                throw new ArgumentException("candidate asset identity missing");
            // Uses already implemented five-theme M07 presentation-only
            // event allowlist; NOT a claimed final Engine/LFX replay binding.
            string key = VufVisualEventCatalog.EventKey(profile, visualEvent);
            var stage = new GameObject("VUF_TEMP_EXTERNAL_PACK_VIEW_ONLY",
                typeof(SpriteRenderer));
            try
            {
                stage.hideFlags =
                    HideFlags.DontSaveInEditor | HideFlags.DontSaveInBuild;
                Sprite sprite = Sprite.Create(verifiedImportedTexture,
                    new Rect(0, 0, verifiedImportedTexture.width,
                             verifiedImportedTexture.height),
                    new Vector2(.5f, .5f), 100f);
                sprite.hideFlags =
                    HideFlags.DontSaveInEditor | HideFlags.DontSaveInBuild;
                stage.GetComponent<SpriteRenderer>().sprite = sprite;
                stage.name = "VUF_TEMP_" + visualEvent + "_NO_ENGINE";
                ownedSprite = sprite;
                // 'key' only records an explicitly acknowledged view source
                // never dispatched to board, score, purchases or remote apps.
                if (String.IsNullOrEmpty(key))
                    throw new InvalidOperationException("invalid view key");
                return stage;
            }
            catch
            {
                if (ownedSprite != null) UnityEngine.Object.DestroyImmediate(ownedSprite);
                UnityEngine.Object.DestroyImmediate(stage);
                ownedSprite = null;
                throw;
            }
        }

        internal static void Dispose(GameObject stage, Sprite ownedSprite)
        {
            if (stage != null) UnityEngine.Object.DestroyImmediate(stage);
            if (ownedSprite != null) UnityEngine.Object.DestroyImmediate(ownedSprite);
        }
    }
}
