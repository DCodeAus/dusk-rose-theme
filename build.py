#!/usr/bin/env python3
"""
Dusk Rose theme builder
=======================

WHAT THIS DOES
    Turns the two colour palettes below (one dark, one light) into the theme
    files VS Code reads:
        themes/dusk-rose-color-theme.json        (Dusk Rose, dark)
        themes/dusk-rose-light-color-theme.json  (Dusk Rose Light)
    It also checks every text colour is readable against its background and
    stops with an error if one is too faint, so a tweak can't quietly make the
    theme harder on your eyes.

WHAT YOU NEED FIRST
    Python 3 (already on a Mac; on Windows install it from python.org).
    Nothing else - no extra packages.

HOW TO RUN IT
    python3 build.py           # rebuild both themes
    python3 build.py --check   # only check; fails if the theme files are out
                               # of date or a colour is too faint (used by the
                               # GitHub check on every pull request)

WHAT TO DO NEXT
    To change a colour: edit it in DARK or LIGHT below, run build.py, then
    follow "Change a colour" in README.md to reinstall.

WHY ONE SCRIPT FOR BOTH THEMES
    Every part of VS Code points at a *role* ("rose", "comment", "bg") rather
    than a raw colour, so the light and dark versions always colour the same
    things the same way - you only pick what each role looks like.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent

# ---------------------------------------------------------------------------
# 1. THE PALETTES - the only part you normally need to edit.
#    Colours are hex: #RRGGBB.
# ---------------------------------------------------------------------------

DARK = {
    "name": "Dusk Rose",
    "type": "dark",
    # Backgrounds: soft slate rather than black, so text doesn't "glow".
    "bg": "#1d1e26",          # editor
    "bg_alt": "#191a21",      # sidebar, tabs bar, status bar, panels
    "bg_deep": "#14151b",     # thin borders between areas
    "bg_term": "#1a1b22",     # terminal
    "widget": "#22232d",      # popups: autocomplete, hover, find box
    "widget_border": "#30323f",
    "line_hl": "#262833",     # the line your cursor is on
    "selection": "#3d4054",
    "list_active": "#2c2e3b",
    "list_inactive": "#25262f",
    "hover": "#22232c",
    # Text, brightest to faintest.
    "fg_bright": "#e4e5ec",
    "fg": "#d6d7e0",          # normal code text / variables
    "fg_ui": "#c8c9d4",
    "fg_side": "#b4b6c4",
    "fg_muted": "#8d91a5",
    "fg_dim": "#7d8194",      # inactive tabs, inline AI suggestions, hints
    "fg_faint": "#5f6377",
    "lineno": "#5c6070",      # line numbers: dim on purpose
    "indent": "#2c2e3a",
    "indent_active": "#4a4d60",
    "whitespace": "#3a3d4c",
    # Syntax + accents.
    "rose": "#e7a1c1",        # signature colour: keywords, cursor, active tab
    "rose_cursor": "#e58fb5",
    "rose_hover": "#efb5cf",
    "green": "#a9d1a0",       # strings
    "blue": "#8fbce6",        # functions
    "lavender": "#c3aef0",    # types / classes
    "peach": "#edbb8f",       # numbers, constants, decorators
    "teal": "#9fd4d2",        # properties, keys
    "red": "#ef7a85",         # errors
    "comment": "#858aa0",
    "punct": "#a2a5b5",       # brackets, commas, operators
    "param": "#e4d2dc",       # function parameters
    "on_accent": "#1d1e26",   # text on pink buttons/badges
    "shadow": "#00000040",
    # Terminal "bright" colours (used by coloured CLI output).
    "term_black": "#2c2e3a",
    "term_bright_black": "#5c6070",
    "term_bright": {
        "red": "#f499a2", "green": "#bfe0b7", "yellow": "#f3cda9", "blue": "#a9cdf0",
        "magenta": "#efb5cf", "cyan": "#b6e2e0", "white": "#e4e5ec",
    },
}

LIGHT = {
    "name": "Dusk Rose Light",
    "type": "light",
    # Warm off-white, never pure #ffffff - pure white is the glare you squint at.
    "bg": "#faf6f4",
    "bg_alt": "#f2ece9",
    "bg_deep": "#e3dbd7",
    "bg_term": "#f6f1ef",
    "widget": "#fdfaf9",
    "widget_border": "#ddd4d0",
    "line_hl": "#f1e9e6",
    "selection": "#ecd3df",
    "list_active": "#eadfe3",
    "list_inactive": "#efe7e6",
    "hover": "#f0e9e7",
    "fg_bright": "#241f2b",
    "fg": "#3a3542",
    "fg_ui": "#4a4552",
    "fg_side": "#4f4a57",
    "fg_muted": "#6f6a78",
    "fg_dim": "#7a7582",
    "fg_faint": "#a39ea8",
    "lineno": "#aaa4ad",
    "indent": "#e6dfdc",
    "indent_active": "#c9bfc4",
    "whitespace": "#d8d0d2",
    # Same hues as the dark theme, just deeper so they read on a light page.
    "rose": "#b0396e",
    "rose_cursor": "#b0396e",
    "rose_hover": "#9a2f5f",
    "green": "#4d7a3f",
    "blue": "#2f69a3",
    "lavender": "#7650b8",
    "peach": "#a8591e",
    "teal": "#237873",
    "red": "#c23545",
    "comment": "#6f6a78",
    "punct": "#6b6675",
    "param": "#6a3f55",
    "on_accent": "#ffffff",
    "shadow": "#3a354220",
    "term_black": "#3a3542",
    "term_bright_black": "#77727f",
    "term_bright": {
        "red": "#a82c3a", "green": "#3f6833", "yellow": "#8f4b18", "blue": "#26598d",
        "magenta": "#962f5d", "cyan": "#1c6560", "white": "#6f6a78",
    },
}

# ---------------------------------------------------------------------------
# 2. READABILITY CHECK
#    Contrast ratio = how far apart text and background are (1 = invisible,
#    21 = black on white). 4.5 is the usual "comfortable to read" minimum.
#    We also cap dark-theme text at 13 - higher than that starts to glare.
# ---------------------------------------------------------------------------

MIN_CONTRAST = 4.5
MAX_DARK_CONTRAST = 13.0
# Roles that are code text and must be readable on the editor background.
TEXT_ROLES = ["fg", "rose", "green", "blue", "lavender", "peach", "teal", "red",
              "comment", "punct", "param", "fg_muted"]


def luminance(hex_colour):
    """How bright a colour looks to the eye (0 = black, 1 = white)."""
    h = hex_colour.lstrip("#")[:6]
    channels = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = channels
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def check_readability(p):
    """Return a list of problems (empty list = all good) and print a report."""
    problems = []
    print(f"\n{p['name']}  (background {p['bg']})")
    for role in TEXT_ROLES:
        ratio = contrast(p[role], p["bg"])
        flag = ""
        if ratio < MIN_CONTRAST:
            flag = "  <-- too faint"
            problems.append(f"{p['name']}: {role} {p[role]} is {ratio:.1f}:1 (need {MIN_CONTRAST})")
        elif p["type"] == "dark" and ratio > MAX_DARK_CONTRAST:
            flag = "  <-- too glaring"
            problems.append(f"{p['name']}: {role} {p[role]} is {ratio:.1f}:1 (max {MAX_DARK_CONTRAST})")
        print(f"  {role:<10} {p[role]}  {ratio:4.1f}:1{flag}")
    # Pink buttons and badges must have readable text on them too.
    ratio = contrast(p["on_accent"], p["rose"])
    print(f"  {'button':<10} {p['on_accent']} on {p['rose']}  {ratio:4.1f}:1")
    if ratio < MIN_CONTRAST:
        problems.append(f"{p['name']}: button text is {ratio:.1f}:1 (need {MIN_CONTRAST})")
    return problems


def a(colour, alpha):
    """Add transparency to a colour. alpha is 2 hex digits: '00' clear .. 'ff' solid."""
    return colour[:7] + alpha


# ---------------------------------------------------------------------------
# 3. WHERE EACH ROLE IS USED IN VS CODE
#    Any setting not listed here falls back to VS Code's default (bright blue
#    etc.), which is exactly the kind of jarring patch we're avoiding - so this
#    list is deliberately thorough.
# ---------------------------------------------------------------------------

def ui_colours(p):
    return {
        # General
        "focusBorder": a(p["rose"], "60"),
        "foreground": p["fg_ui"],
        "descriptionForeground": p["fg_muted"],
        "errorForeground": p["red"],
        "icon.foreground": p["fg_side"],
        "widget.shadow": p["shadow"],
        "selection.background": a(p["rose"], "40"),
        "sash.hoverBorder": a(p["rose"], "80"),

        # Editor
        "editor.background": p["bg"],
        "editor.foreground": p["fg"],
        "editorCursor.foreground": p["rose_cursor"],
        "editor.lineHighlightBackground": p["line_hl"],
        "editor.lineHighlightBorder": "#00000000",
        "editor.selectionBackground": p["selection"],
        "editor.inactiveSelectionBackground": a(p["selection"], "80"),
        "editor.selectionHighlightBackground": a(p["rose"], "1f"),
        "editor.wordHighlightBackground": a(p["blue"], "24"),
        "editor.wordHighlightStrongBackground": a(p["rose"], "2a"),
        "editor.findMatchBackground": a(p["peach"], "55"),
        "editor.findMatchHighlightBackground": a(p["peach"], "2a"),
        "editor.findRangeHighlightBackground": a(p["peach"], "14"),
        "editor.rangeHighlightBackground": a(p["blue"], "14"),
        "editor.hoverHighlightBackground": a(p["blue"], "1a"),
        "editor.foldBackground": a(p["lavender"], "10"),
        "editorLink.activeForeground": p["blue"],
        "editorLineNumber.foreground": p["lineno"],
        "editorLineNumber.activeForeground": p["rose"],
        "editorIndentGuide.background1": p["indent"],
        "editorIndentGuide.activeBackground1": p["indent_active"],
        "editorWhitespace.foreground": p["whitespace"],
        "editorRuler.foreground": p["indent"],
        "editorCodeLens.foreground": p["fg_dim"],
        "editorBracketMatch.background": a(p["rose"], "25"),
        "editorBracketMatch.border": a(p["rose"], "70"),
        "editorBracketHighlight.foreground1": p["rose"],
        "editorBracketHighlight.foreground2": p["blue"],
        "editorBracketHighlight.foreground3": p["lavender"],
        "editorBracketHighlight.foreground4": p["green"],
        "editorBracketHighlight.foreground5": p["peach"],
        "editorBracketHighlight.foreground6": p["teal"],
        "editorBracketHighlight.unexpectedBracket.foreground": p["red"],
        "editorError.foreground": p["red"],
        "editorWarning.foreground": p["peach"],
        "editorInfo.foreground": p["blue"],
        "editorHint.foreground": p["teal"],
        "editorUnnecessaryCode.opacity": "#000000a0",

        # Inline AI/autocomplete suggestions (grey "ghost" text) and type hints.
        # Dim enough to tell apart from real code, never bright.
        "editorGhostText.foreground": p["fg_dim"],
        "editorInlayHint.foreground": p["fg_dim"],
        "editorInlayHint.background": a(p["lavender"], "12"),
        "editorInlayHint.typeForeground": p["fg_dim"],
        "editorInlayHint.parameterForeground": p["fg_dim"],

        # Gutter (git change markers beside line numbers)
        "editorGutter.addedBackground": a(p["green"], "a0"),
        "editorGutter.modifiedBackground": a(p["blue"], "a0"),
        "editorGutter.deletedBackground": a(p["red"], "a0"),
        "editorGutter.foldingControlForeground": p["fg_muted"],

        # Scrollbar markers + minimap
        "editorOverviewRuler.border": "#00000000",
        "editorOverviewRuler.errorForeground": a(p["red"], "b0"),
        "editorOverviewRuler.warningForeground": a(p["peach"], "b0"),
        "editorOverviewRuler.infoForeground": a(p["blue"], "b0"),
        "editorOverviewRuler.addedForeground": a(p["green"], "90"),
        "editorOverviewRuler.modifiedForeground": a(p["blue"], "90"),
        "editorOverviewRuler.deletedForeground": a(p["red"], "90"),
        "editorOverviewRuler.findMatchForeground": a(p["peach"], "a0"),
        "editorOverviewRuler.selectionHighlightForeground": a(p["rose"], "a0"),
        "minimap.background": p["bg"],
        "minimap.selectionHighlight": a(p["rose"], "60"),
        "minimap.findMatchHighlight": a(p["peach"], "80"),
        "minimap.errorHighlight": a(p["red"], "a0"),
        "minimap.warningHighlight": a(p["peach"], "a0"),
        "minimapGutter.addedBackground": a(p["green"], "a0"),
        "minimapGutter.modifiedBackground": a(p["blue"], "a0"),
        "minimapGutter.deletedBackground": a(p["red"], "a0"),

        # Popups: autocomplete, hover, find box, peek
        "editorWidget.background": p["widget"],
        "editorWidget.foreground": p["fg_ui"],
        "editorWidget.border": p["widget_border"],
        "editorSuggestWidget.background": p["widget"],
        "editorSuggestWidget.border": p["widget_border"],
        "editorSuggestWidget.foreground": p["fg_ui"],
        "editorSuggestWidget.selectedBackground": p["list_active"],
        "editorSuggestWidget.highlightForeground": p["rose"],
        "editorSuggestWidget.focusHighlightForeground": p["rose"],
        "editorHoverWidget.background": p["widget"],
        "editorHoverWidget.border": p["widget_border"],
        "peekView.border": a(p["rose"], "80"),
        "peekViewEditor.background": p["bg_alt"],
        "peekViewEditor.matchHighlightBackground": a(p["peach"], "40"),
        "peekViewResult.background": p["widget"],
        "peekViewResult.selectionBackground": p["list_active"],
        "peekViewResult.matchHighlightBackground": a(p["peach"], "40"),
        "peekViewTitle.background": p["widget"],
        "peekViewTitleLabel.foreground": p["fg_bright"],
        "peekViewTitleDescription.foreground": p["fg_muted"],

        # Sticky scroll (function name pinned at top) + breadcrumbs
        "editorStickyScroll.background": p["bg"],
        "editorStickyScroll.shadow": p["shadow"],
        "editorStickyScrollHover.background": p["hover"],
        "breadcrumb.foreground": p["fg_dim"],
        "breadcrumb.focusForeground": p["fg_ui"],
        "breadcrumb.activeSelectionForeground": p["rose"],
        "breadcrumbPicker.background": p["widget"],

        # Diff view (comparing files / git changes) - soft tints, not neon blocks
        "diffEditor.insertedTextBackground": a(p["green"], "26"),
        "diffEditor.removedTextBackground": a(p["red"], "26"),
        "diffEditor.insertedLineBackground": a(p["green"], "12"),
        "diffEditor.removedLineBackground": a(p["red"], "12"),
        "diffEditor.border": p["widget_border"],
        "diffEditor.diagonalFill": a(p["fg_faint"], "30"),
        "diffEditorGutter.insertedLineBackground": a(p["green"], "20"),
        "diffEditorGutter.removedLineBackground": a(p["red"], "20"),

        # Merge conflicts
        "merge.currentHeaderBackground": a(p["green"], "40"),
        "merge.currentContentBackground": a(p["green"], "16"),
        "merge.incomingHeaderBackground": a(p["blue"], "40"),
        "merge.incomingContentBackground": a(p["blue"], "16"),
        "merge.commonHeaderBackground": a(p["lavender"], "40"),
        "merge.commonContentBackground": a(p["lavender"], "16"),
        "editorOverviewRuler.currentContentForeground": a(p["green"], "a0"),
        "editorOverviewRuler.incomingContentForeground": a(p["blue"], "a0"),

        # Tabs
        "editorGroupHeader.tabsBackground": p["bg_alt"],
        "editorGroupHeader.tabsBorder": p["bg_deep"],
        "editorGroup.border": p["bg_deep"],
        "editorGroup.dropBackground": a(p["rose"], "18"),
        "tab.activeBackground": p["bg"],
        "tab.activeForeground": p["fg_bright"],
        "tab.activeBorderTop": p["rose"],
        "tab.unfocusedActiveBorderTop": a(p["rose"], "60"),
        "tab.inactiveBackground": p["bg_alt"],
        "tab.inactiveForeground": p["fg_dim"],
        "tab.unfocusedActiveForeground": p["fg_muted"],
        "tab.hoverBackground": p["hover"],
        "tab.border": p["bg_deep"],
        "tab.activeModifiedBorder": p["peach"],

        # Activity bar (icons down the far left) + side bar
        "activityBar.background": p["bg_alt"],
        "activityBar.foreground": p["fg"],
        "activityBar.inactiveForeground": p["fg_faint"],
        "activityBar.activeBorder": p["rose"],
        "activityBar.border": p["bg_deep"],
        "activityBarBadge.background": p["rose"],
        "activityBarBadge.foreground": p["on_accent"],
        "sideBar.background": p["bg_alt"],
        "sideBar.foreground": p["fg_side"],
        "sideBar.border": p["bg_deep"],
        "sideBarTitle.foreground": p["fg_muted"],
        "sideBarSectionHeader.background": p["bg_alt"],
        "sideBarSectionHeader.foreground": p["punct"],
        "sideBarSectionHeader.border": p["bg_deep"],

        # Lists and trees (file explorer, search results, etc.)
        "list.activeSelectionBackground": p["list_active"],
        "list.activeSelectionForeground": p["fg_bright"],
        "list.inactiveSelectionBackground": p["list_inactive"],
        "list.hoverBackground": p["hover"],
        "list.highlightForeground": p["rose"],
        "list.focusOutline": a(p["rose"], "50"),
        "list.errorForeground": p["red"],
        "list.warningForeground": p["peach"],
        "list.dropBackground": a(p["rose"], "18"),
        "tree.indentGuidesStroke": p["indent_active"],

        # Command palette (Cmd+Shift+P) and pickers
        "quickInput.background": p["widget"],
        "quickInput.foreground": p["fg_ui"],
        "quickInputTitle.background": p["bg_alt"],
        "quickInputList.focusBackground": p["list_active"],
        "quickInputList.focusForeground": p["fg_bright"],
        "pickerGroup.foreground": p["rose"],
        "pickerGroup.border": p["widget_border"],
        "keybindingLabel.background": a(p["fg_faint"], "30"),
        "keybindingLabel.foreground": p["fg_ui"],
        "keybindingLabel.border": p["widget_border"],
        "keybindingLabel.bottomBorder": p["widget_border"],
        "commandCenter.background": p["bg"],
        "commandCenter.foreground": p["fg_muted"],
        "commandCenter.border": p["widget_border"],
        "commandCenter.activeBackground": p["hover"],

        # Menus
        "menu.background": p["widget"],
        "menu.foreground": p["fg_ui"],
        "menu.selectionBackground": p["list_active"],
        "menu.selectionForeground": p["fg_bright"],
        "menu.separatorBackground": p["widget_border"],
        "menu.border": p["widget_border"],

        # Notifications (pop-ups bottom-right)
        "notifications.background": p["widget"],
        "notifications.foreground": p["fg_ui"],
        "notifications.border": p["widget_border"],
        "notificationCenterHeader.background": p["bg_alt"],
        "notificationsErrorIcon.foreground": p["red"],
        "notificationsWarningIcon.foreground": p["peach"],
        "notificationsInfoIcon.foreground": p["blue"],
        "notificationLink.foreground": p["blue"],

        # Status bar + title bar
        "statusBar.background": p["bg_alt"],
        "statusBar.foreground": p["fg_muted"],
        "statusBar.border": p["bg_deep"],
        "statusBar.debuggingBackground": p["rose"],
        "statusBar.debuggingForeground": p["on_accent"],
        "statusBar.noFolderBackground": p["bg_alt"],
        "statusBarItem.hoverBackground": p["hover"],
        "statusBarItem.remoteBackground": p["rose"],
        "statusBarItem.remoteForeground": p["on_accent"],
        "statusBarItem.errorBackground": p["red"],
        "statusBarItem.errorForeground": p["on_accent"],
        "statusBarItem.warningBackground": p["peach"],
        "statusBarItem.warningForeground": p["on_accent"],
        "statusBarItem.prominentBackground": a(p["rose"], "30"),
        "titleBar.activeBackground": p["bg_alt"],
        "titleBar.activeForeground": p["punct"],
        "titleBar.inactiveBackground": p["bg_alt"],
        "titleBar.inactiveForeground": p["fg_faint"],
        "titleBar.border": p["bg_deep"],

        # Bottom panel (terminal, problems, output)
        "panel.background": p["bg_alt"],
        "panel.border": p["widget_border"],
        "panelTitle.activeBorder": p["rose"],
        "panelTitle.activeForeground": p["fg"],
        "panelTitle.inactiveForeground": p["fg_dim"],

        # Inputs, buttons, checkboxes
        "input.background": p["widget"],
        "input.foreground": p["fg"],
        "input.border": p["widget_border"],
        "input.placeholderForeground": p["fg_dim"],
        "inputOption.activeBorder": p["rose"],
        "inputOption.activeBackground": a(p["rose"], "30"),
        "inputValidation.errorBackground": p["widget"],
        "inputValidation.errorBorder": p["red"],
        "inputValidation.warningBackground": p["widget"],
        "inputValidation.warningBorder": p["peach"],
        "inputValidation.infoBackground": p["widget"],
        "inputValidation.infoBorder": p["blue"],
        "dropdown.background": p["widget"],
        "dropdown.border": p["widget_border"],
        "dropdown.foreground": p["fg_ui"],
        "checkbox.background": p["widget"],
        "checkbox.border": p["widget_border"],
        "button.background": p["rose"],
        "button.foreground": p["on_accent"],
        "button.hoverBackground": p["rose_hover"],
        "button.secondaryBackground": p["list_active"],
        "button.secondaryForeground": p["fg_ui"],
        "button.secondaryHoverBackground": p["widget_border"],
        "badge.background": p["rose"],
        "badge.foreground": p["on_accent"],
        "progressBar.background": p["rose"],
        "scrollbar.shadow": p["shadow"],
        "scrollbarSlider.background": a(p["whitespace"], "60"),
        "scrollbarSlider.hoverBackground": a(p["indent_active"], "80"),
        "scrollbarSlider.activeBackground": a(p["rose"], "60"),
        "textLink.foreground": p["blue"],
        "textLink.activeForeground": p["rose"],
        "textBlockQuote.background": p["bg_alt"],
        "textBlockQuote.border": a(p["rose"], "80"),
        "textCodeBlock.background": p["bg_alt"],
        "textPreformat.foreground": p["peach"],

        # Git colours in the file explorer
        "gitDecoration.modifiedResourceForeground": p["blue"],
        "gitDecoration.untrackedResourceForeground": p["green"],
        "gitDecoration.addedResourceForeground": p["green"],
        "gitDecoration.deletedResourceForeground": p["red"],
        "gitDecoration.conflictingResourceForeground": p["peach"],
        "gitDecoration.ignoredResourceForeground": p["fg_faint"],

        # Debugging
        "debugToolBar.background": p["widget"],
        "debugToolBar.border": p["widget_border"],
        "editor.stackFrameHighlightBackground": a(p["peach"], "22"),
        "editor.focusedStackFrameHighlightBackground": a(p["green"], "22"),
        "debugIcon.breakpointForeground": p["red"],
        "debugIcon.startForeground": p["green"],
        "debugConsole.infoForeground": p["blue"],
        "debugConsole.warningForeground": p["peach"],
        "debugConsole.errorForeground": p["red"],

        # Testing
        "testing.iconPassed": p["green"],
        "testing.iconFailed": p["red"],
        "testing.iconQueued": p["peach"],

        # Welcome page / walkthroughs
        "welcomePage.tileBackground": p["widget"],
        "welcomePage.tileHoverBackground": p["hover"],
        "walkThrough.embeddedEditorBackground": p["bg_alt"],

        # Terminal
        "terminal.background": p["bg_term"],
        "terminal.foreground": p["fg"],
        "terminalCursor.foreground": p["rose_cursor"],
        "terminal.selectionBackground": p["selection"],
        "terminal.findMatchBackground": a(p["peach"], "55"),
        "terminal.findMatchHighlightBackground": a(p["peach"], "2a"),
        "terminalCommandDecoration.defaultBackground": p["fg_faint"],
        "terminalCommandDecoration.successBackground": p["green"],
        "terminalCommandDecoration.errorBackground": p["red"],
        "terminal.ansiBlack": p["term_black"],
        "terminal.ansiRed": p["red"],
        "terminal.ansiGreen": p["green"],
        "terminal.ansiYellow": p["peach"],
        "terminal.ansiBlue": p["blue"],
        "terminal.ansiMagenta": p["rose"],
        "terminal.ansiCyan": p["teal"],
        "terminal.ansiWhite": p["fg_ui"] if p["type"] == "dark" else p["fg_muted"],
        "terminal.ansiBrightBlack": p["term_bright_black"],
        "terminal.ansiBrightRed": p["term_bright"]["red"],
        "terminal.ansiBrightGreen": p["term_bright"]["green"],
        "terminal.ansiBrightYellow": p["term_bright"]["yellow"],
        "terminal.ansiBrightBlue": p["term_bright"]["blue"],
        "terminal.ansiBrightMagenta": p["term_bright"]["magenta"],
        "terminal.ansiBrightCyan": p["term_bright"]["cyan"],
        "terminal.ansiBrightWhite": p["term_bright"]["white"] if p["type"] == "light" else p["fg_bright"],
    }


def token_colours(p):
    """Syntax colours: which kinds of code get which role."""
    def rule(scopes, colour=None, style=None):
        settings = {}
        if colour:
            settings["foreground"] = colour
        if style is not None:
            settings["fontStyle"] = style
        return {"scope": scopes, "settings": settings}

    return [
        rule(["comment", "punctuation.definition.comment"], p["comment"], "italic"),
        rule(["keyword", "storage.type", "storage.modifier", "keyword.control",
              "keyword.operator.new", "keyword.operator.expression", "keyword.operator.logical"], p["rose"]),
        rule(["keyword.operator", "punctuation", "meta.brace", "punctuation.separator",
              "punctuation.terminator"], p["punct"]),
        rule(["string", "string.quoted", "string.template", "punctuation.definition.string"], p["green"]),
        rule(["constant.character.escape", "string.regexp"], p["teal"]),
        rule(["constant.numeric", "constant.language", "support.constant", "constant.other"], p["peach"]),
        rule(["entity.name.function", "support.function", "meta.function-call entity.name.function",
              "variable.function"], p["blue"]),
        rule(["entity.name.type", "entity.name.class", "support.type", "support.class",
              "entity.other.inherited-class", "storage.type.class"], p["lavender"]),
        rule(["variable", "variable.other", "meta.definition.variable"], p["fg"]),
        rule(["variable.parameter"], p["param"], "italic"),
        rule(["variable.language", "variable.language.this", "variable.language.self"], p["rose"], "italic"),
        rule(["variable.other.property", "variable.other.object.property", "support.variable.property",
              "meta.object-literal.key", "support.type.property-name"], p["teal"]),
        rule(["entity.name.tag"], p["rose"]),
        rule(["entity.other.attribute-name"], p["peach"], "italic"),
        rule(["entity.name.namespace", "entity.name.module", "entity.name.type.module"], p["lavender"]),
        rule(["meta.decorator", "entity.name.function.decorator", "punctuation.decorator"], p["peach"], "italic"),
        # Keys in YAML/JSON/TOML config files read as properties (teal), not HTML tags.
        rule(["entity.name.tag.yaml", "support.type.property-name.json", "support.type.property-name.toml",
              "keyword.other.definition.ini"], p["teal"]),
        # PowerShell $variables and Bicep/ARM keywords keep the normal roles.
        rule(["punctuation.definition.variable.powershell"], p["fg"]),
        rule(["markup.heading", "entity.name.section"], p["rose"], "bold"),
        rule(["markup.bold"], style="bold"),
        rule(["markup.italic"], style="italic"),
        rule(["markup.inline.raw", "markup.fenced_code"], p["green"]),
        rule(["markup.underline.link", "string.other.link"], p["blue"]),
        rule(["markup.quote"], p["comment"], "italic"),
        rule(["markup.inserted"], p["green"]),
        rule(["markup.deleted"], p["red"]),
        rule(["markup.changed"], p["blue"]),
        rule(["invalid", "invalid.illegal"], p["red"]),
    ]


def semantic_colours(p):
    """Colours used when a language server (Pylance for Python, C# Dev Kit,
    TypeScript) understands the code better than plain pattern-matching."""
    return {
        "parameter": {"foreground": p["param"], "italic": True},
        "selfParameter": {"foreground": p["rose"], "italic": True},   # Python `self`
        "property": p["teal"],
        "function": p["blue"],
        "method": p["blue"],
        "class": p["lavender"],
        "struct": p["lavender"],
        "enum": p["lavender"],
        "type": p["lavender"],
        "interface": p["lavender"],
        "typeParameter": p["lavender"],
        "namespace": p["lavender"],
        "module": p["lavender"],
        "enumMember": p["peach"],
        "decorator": {"foreground": p["peach"], "italic": True},
        "macro": p["peach"],
        "event": p["teal"],
        "variable.readonly": p["peach"],
        "*.deprecated": {"strikethrough": True},
    }


def build_theme(p):
    return {
        "$schema": "vscode://schemas/color-theme",
        "name": p["name"],
        "type": p["type"],
        "semanticHighlighting": True,
        "colors": ui_colours(p),
        "tokenColors": token_colours(p),
        "semanticTokenColors": semantic_colours(p),
    }


OUTPUTS = {
    "themes/dusk-rose-color-theme.json": DARK,
    "themes/dusk-rose-light-color-theme.json": LIGHT,
}


def main():
    check_only = "--check" in sys.argv
    problems = []
    for palette in OUTPUTS.values():
        problems += check_readability(palette)

    for rel_path, palette in OUTPUTS.items():
        path = HERE / rel_path
        text = json.dumps(build_theme(palette), indent=2) + "\n"
        if check_only:
            if not path.exists() or path.read_text() != text:
                problems.append(f"{rel_path} is out of date - run: python3 build.py")
        else:
            path.parent.mkdir(exist_ok=True)
            path.write_text(text)
            print(f"\nwrote {rel_path}")

    if problems:
        print("\nPROBLEMS:")
        for line in problems:
            print("  - " + line)
        sys.exit(1)
    print("\nAll colours readable." + ("" if check_only else " Themes built."))


if __name__ == "__main__":
    main()
