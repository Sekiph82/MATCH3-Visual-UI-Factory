# VF-07 | Real, layered Unity UI Composer (prototype)

Unity menu: **Tools > MATCH3 > Interactive UI Composer**.
The prototype creates NEW, non-overwritten uGUI `.prefab` candidates containing
an actual `Canvas`, `CanvasScaler`, `GraphicRaycaster`, `Image` layers,
`Text` and a `Button`. The Button is deliberately `interactable=false`
because **no Engine gameplay action or reward authority is connected**.
`VufSafeAreaFitter` is attached to the content RectTransform for phone insets.
Profiles: all five games. Available source-level *layout archetypes*: Home,
Gameplay HUD, World Map, Shop, Events, Collection, Settings.

**Not implemented:** full 28 Coral experiences as interactive prefabs, real
screen artwork, callbacks, data bindings, font approvals, localization,
button actions, actual animations, device testing or playmode verification.
Editor must compile Unity 6000.6.5f1 and produce a prefab before saying this
works outside source code. The first build needs `com.unity.ugui@2.6.0`
which the UPM package declares. Approved asset masters are never replaced.
