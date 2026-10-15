# VF-08 | Safe area runtime prototype

`unity_package/Runtime/VufSafeAreaFitter.cs` is a real MonoBehaviour bound to
a fullscreen content RectTransform. It observes `Screen.safeArea` and actual
`Screen.width/height`, maps normalized bottom-left anchors and clears
offsets on changes.

The UI Composer attaches it to candidate in-game screens and scales the
Canvas at 720x1280 with MatchWidthOrHeight. This is **runtime SOURCE ONLY**
until verified inside Unity. It does not replace screenshot testing on real
iPhone and Android notches/tablets, text overflow, touch target compliance or
accessibility. Manual guide overlays in VufStudioWindow remain SIMULATION.
