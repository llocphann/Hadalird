#!/usr/bin/env python3
"""Owned Obsidian task/capture settings contract; host routing is tested in Hadalis."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
todo=(ROOT/'modules/settings/ObsidianTodoSettings.qml').read_text()
required = [
    'title: Translation.tr("To-do & Quick Notes")',
    'title: Translation.tr("Task source")',
    'Translation.tr("Note path pattern")',
    'Translation.tr("Heading")',
    'id: todoMarkdownNotePattern',
    'id: todoMarkdownHeading',
    'Config.setNestedValue("todo.obsidian.dailyNote.folder", folder)',
    'Config.setNestedValue("todo.obsidian.dailyNote.format", format)',
    'Config.setNestedValue("todo.obsidian.dailyNote.plannerHeading", value)',
    'Config.setNestedValue("todo.obsidian.dailyNote.plannerHeadingLevel", value)',
    'Config.setNestedValue("todo.obsidian.dailyNote.defaultDurationMinutes", value)',
    'Config.setNestedValue("todo.obsidian.sourceMode", "markdown-note")',
    'Todo.beginObsidianSetup()',
    'Todo.cancelObsidianSetup()',
    'Todo.reactivateInternal()',
    'Todo.previewInternalToObsidian()',
    'Todo.migrateInternalToObsidian(',
    'Todo.activateObsidian()',
    'Todo.openObsidianSource()',
    'Translation.tr("Use Obsidian source")',
]
for token in required:
    assert token in todo, f"Obsidian task settings contract lost: {token}"
assert 'Config.setNestedValue("todo.backend", "obsidian")' not in todo
for token in ['Day Planner', 'Planner heading', 'font.pixelSize: Appearance.font.pixelSize.smallest', 'id: zettelkastenVaultPath', 'Translation.tr("Vault path override")']:
    assert token not in todo, token
assert todo.count('title: Translation.tr("To-do & Quick Notes")')==1
assert todo.count('placeholderText: ""')>=3
assert '/^\\/+|\\/+$/g' in todo
assert 'notes.zettelkasten.folder' in todo and 'notes.zettelkasten.defaultType' in todo
print('HADALIRD_OBSIDIAN_TODO_SETTINGS_PASS')
