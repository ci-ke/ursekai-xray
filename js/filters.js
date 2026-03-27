/**
 * Filters Module
 * Handles all filtering logic for items
 */

import { RARE_ITEM, SUPER_RARE_ITEM, ITEM_TEXTURES } from './config.js';
import { filterState, sceneState, FILTER_DEBOUNCE_DELAY } from './state.js';

// Callback for redrawing points - set by ui.js during initialization
let onFilterChange = null;

/**
 * Set the callback for when filter changes
 */
export function setFilterChangeCallback(callback) {
    onFilterChange = callback;
}

/**
 * Check if item should be displayed based on current filter
 */
export function shouldShowItem(category, itemId) {
    if (filterState.filterMode === 'all') {
        return true;
    } else if (filterState.filterMode === 'rare') {
        const rareItems = RARE_ITEM[category] || [];
        return rareItems.includes(parseInt(itemId));
    } else if (filterState.filterMode === 'custom') {
        // Wildcard key "*" means the whole category is toggled as one unit
        if (filterState.selectedItems.has(`${category}:*`)) return true;
        return filterState.selectedItems.has(`${category}:${itemId}`);
    }
    return true;
}

/**
 * Change filter mode and trigger redraw
 */
export function changeFilterMode() {
    const selected = document.querySelector('input[name="filterMode"]:checked');
    filterState.filterMode = selected.value;
    const customCheckboxes = document.getElementById('itemCheckboxContainer');

    if (filterState.filterMode === 'custom') {
        customCheckboxes.style.display = 'grid';
    } else {
        customCheckboxes.style.display = 'none';
    }

    // Debounce filter changes to avoid multiple redraws during rapid filter toggles
    clearTimeout(filterState.filterDebounceTimer);
    filterState.filterDebounceTimer = setTimeout(() => {
        if (onFilterChange) {
            onFilterChange();
        }
    }, FILTER_DEBOUNCE_DELAY);
}

/**
 * Initialize item checkboxes for custom filter
 * Rebuilds based on items actually present in loaded harvest data
 */
export function initializeItemCheckboxes() {
    const container = document.getElementById('itemCheckboxContainer');

    // Collect all category:itemId pairs actually present across all scenes
    const seen = new Map(); // key: "category:itemId" -> { category, itemId, path }
    const musicRecordSeen = false;

    for (const sceneName in sceneState.harvestData) {
        const points = sceneState.harvestData[sceneName];
        if (!Array.isArray(points)) continue;
        points.forEach(point => {
            for (const category in point.reward) {
                if (!point.reward.hasOwnProperty(category)) continue;
                for (const itemId in point.reward[category]) {
                    if (!point.reward[category].hasOwnProperty(itemId)) continue;

                    // music_record: collapse all ids into one wildcard entry
                    if (category === 'mysekai_music_record') {
                        const key = `${category}:*`;
                        if (!seen.has(key)) {
                            seen.set(key, {
                                category,
                                itemId: '*',
                                path: ITEM_TEXTURES[category]?.['*'] || './icon/missing.png'
                            });
                        }
                    } else {
                        const key = `${category}:${itemId}`;
                        if (!seen.has(key)) {
                            const path = ITEM_TEXTURES[category]?.[itemId] || './icon/missing.png';
                            seen.set(key, { category, itemId, path });
                        }
                    }
                }
            }
        });
    }

    // If no data loaded yet, nothing to show
    if (seen.size === 0) {
        container.innerHTML = '<div style="color:#aaa;font-size:12px;padding:4px;">Load data first</div>';
        if (filterState.filterMode !== 'custom') container.style.display = 'none';
        return;
    }

    // Rebuild container, preserving checked state
    container.innerHTML = '';

    // Sort: by category then itemId numerically
    const allItems = Array.from(seen.values()).sort((a, b) => {
        if (a.category !== b.category) return a.category.localeCompare(b.category);
        if (a.itemId === '*') return 1;
        if (b.itemId === '*') return -1;
        return parseInt(a.itemId) - parseInt(b.itemId);
    });

    allItems.forEach(item => {
        const checkbox = document.createElement('div');
        checkbox.className = 'item-checkbox';

        const inputId = `item-${item.category}-${item.itemId}`;
        const input = document.createElement('input');
        input.type = 'checkbox';
        input.id = inputId;
        input.value = `${item.category}:${item.itemId}`;
        // Restore checked state if previously selected
        input.checked = filterState.selectedItems.has(input.value);
        input.onchange = (e) => {
            if (e.target.checked) {
                filterState.selectedItems.add(e.target.value);
            } else {
                filterState.selectedItems.delete(e.target.value);
            }
            clearTimeout(filterState.filterDebounceTimer);
            filterState.filterDebounceTimer = setTimeout(() => {
                if (onFilterChange) onFilterChange();
            }, FILTER_DEBOUNCE_DELAY);
        };

        const label = document.createElement('label');
        label.htmlFor = inputId;
        const titleText = item.itemId === '*'
            ? `${item.category} (all)`
            : `${item.category} #${item.itemId}`;
        label.title = titleText;

        const img = document.createElement('img');
        img.src = item.path;
        img.alt = titleText;
        img.onerror = function() { this.src = './icon/missing.png'; };

        label.appendChild(img);
        checkbox.appendChild(input);
        checkbox.appendChild(label);
        container.appendChild(checkbox);
    });

    if (filterState.filterMode !== 'custom') container.style.display = 'none';
}

/**
 * Toggle filter panel visibility
 */
export function toggleFilterPanel() {
    const filterPanel = document.getElementById('filterPanel');
    filterPanel.classList.toggle('active');
    if (filterPanel.classList.contains('active')) {
        initializeItemCheckboxes();
    }
}

/**
 * Check if reward contains rare item
 */
export function doContainsRareItem(reward, isSuperRare = false) {
    let compareList = isSuperRare ? SUPER_RARE_ITEM : RARE_ITEM;
    for (const category in reward) {
        if (reward.hasOwnProperty(category) && compareList.hasOwnProperty(category)) {
            for (const itemId of Object.keys(reward[category])) {
                if (compareList[category].includes(parseInt(itemId))) {
                    return true;
                }
            }
        }
    }
    return false;
}
