#!/usr/bin/env python3
"""
GAMMA DEEP DIVE - Spotlight & Fullscreen Controls
Comprehensive analysis to find how to activate these modes
"""

import time
import json
from playwright.sync_api import sync_playwright

def deep_dive_controls():
    """Deep dive into GAMMA's spotlight and fullscreen controls"""

    gamma_url = "https://gamma.app/docs/What-If-I-Cant-Pay-the-Judgment-217gvxmpmzlgk6n?mode=present#card-bakvgbrqp803elh"

    print("="*70)
    print("GAMMA DEEP DIVE - Spotlight & Fullscreen Controls")
    print("="*70)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--start-maximized'])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        print(f"\nOpening: {gamma_url}")
        page.goto(gamma_url)

        print("Waiting 10 seconds for complete load...")
        time.sleep(10)

        print("\n" + "="*70)
        print("PHASE 1: FINDING ALL BUTTONS AND CONTROLS")
        print("="*70 + "\n")

        # Find all interactive elements
        controls_analysis = page.evaluate("""() => {
            const analysis = {
                allButtons: [],
                suspiciousElements: [],
                ariaLabels: [],
                dataAttributes: []
            };

            // Get ALL buttons
            const buttons = document.querySelectorAll('button');
            buttons.forEach((btn, idx) => {
                const info = {
                    index: idx,
                    text: btn.innerText.trim(),
                    ariaLabel: btn.getAttribute('aria-label'),
                    title: btn.getAttribute('title'),
                    className: btn.className,
                    id: btn.id,
                    onClick: btn.onclick ? 'has onclick' : 'no onclick'
                };

                // Check if relevant to spotlight or fullscreen
                const lowerText = (info.text + ' ' + (info.ariaLabel || '') + ' ' + (info.title || '')).toLowerCase();
                if (lowerText.includes('spotlight') || lowerText.includes('full') ||
                    lowerText.includes('screen') || lowerText.includes('present') ||
                    lowerText.includes('auto') || lowerText.includes('exit')) {
                    analysis.suspiciousElements.push(info);
                }

                analysis.allButtons.push(info);
            });

            // Get all elements with aria-label
            const ariaElements = document.querySelectorAll('[aria-label]');
            ariaElements.forEach(elem => {
                const label = elem.getAttribute('aria-label');
                if (label) {
                    analysis.ariaLabels.push({
                        tag: elem.tagName,
                        ariaLabel: label,
                        className: elem.className,
                        id: elem.id
                    });
                }
            });

            // Get all data attributes
            const dataElements = document.querySelectorAll('[data-spotlight], [data-fullscreen], [data-mode], [data-state]');
            dataElements.forEach(elem => {
                const attrs = {};
                for (const attr of elem.attributes) {
                    if (attr.name.startsWith('data-')) {
                        attrs[attr.name] = attr.value;
                    }
                }
                analysis.dataAttributes.push({
                    tag: elem.tagName,
                    attributes: attrs,
                    className: elem.className
                });
            });

            return analysis;
        }""")

        print(f"Found {len(controls_analysis['allButtons'])} total buttons")
        print(f"Found {len(controls_analysis['suspiciousElements'])} suspicious elements\n")

        if controls_analysis['suspiciousElements']:
            print("🎯 SUSPICIOUS ELEMENTS (likely controls):")
            for elem in controls_analysis['suspiciousElements']:
                print(f"\n  Button {elem['index']}:")
                print(f"    Text: '{elem['text']}'")
                print(f"    Aria-label: {elem['ariaLabel']}")
                print(f"    Title: {elem['title']}")
                print(f"    Class: {elem['className'][:60]}...")

        if controls_analysis['dataAttributes']:
            print("\n📊 DATA ATTRIBUTES:")
            for item in controls_analysis['dataAttributes']:
                print(f"  <{item['tag']}> {item['attributes']}")

        print("\n" + "="*70)
        print("PHASE 2: TESTING SPOTLIGHT ACTIVATION")
        print("="*70 + "\n")

        # Take screenshot before
        page.screenshot(path='gamma_before_spotlight.png')
        print("📸 Screenshot before: gamma_before_spotlight.png")

        # Try multiple methods to activate spotlight
        spotlight_results = {}

        # Method 1: Press 'S' key
        print("\n[Method 1] Pressing 'S' key...")
        before_classes = page.evaluate("() => document.body.className")
        page.keyboard.press('s')
        time.sleep(2)
        after_classes = page.evaluate("() => document.body.className")

        spotlight_results['s_key'] = {
            'before_classes': before_classes,
            'after_classes': after_classes,
            'changed': before_classes != after_classes
        }

        if spotlight_results['s_key']['changed']:
            print("  ✅ Classes changed! Spotlight might be active")
            print(f"     Before: {before_classes[:80]}")
            print(f"     After:  {after_classes[:80]}")
        else:
            print("  ⚠️  No change in body classes")

        page.screenshot(path='gamma_after_s_key.png')
        print("  📸 Screenshot: gamma_after_s_key.png")

        # Method 2: Look for and click spotlight button
        print("\n[Method 2] Searching for spotlight button...")
        spotlight_button = page.evaluate("""() => {
            const buttons = document.querySelectorAll('button');
            for (const btn of buttons) {
                const text = (btn.innerText + ' ' + (btn.getAttribute('aria-label') || '')).toLowerCase();
                if (text.includes('spotlight')) {
                    return {
                        found: true,
                        text: btn.innerText,
                        ariaLabel: btn.getAttribute('aria-label'),
                        className: btn.className
                    };
                }
            }
            return { found: false };
        }""")

        if spotlight_button['found']:
            print(f"  ✅ Found spotlight button!")
            print(f"     Text: {spotlight_button['text']}")
            print(f"     Aria: {spotlight_button['ariaLabel']}")
            # Try clicking it
            try:
                if spotlight_button['ariaLabel']:
                    page.click(f"button[aria-label='{spotlight_button['ariaLabel']}']")
                    time.sleep(2)
                    page.screenshot(path='gamma_after_spotlight_button.png')
                    print("  📸 Screenshot: gamma_after_spotlight_button.png")
            except Exception as e:
                print(f"  ⚠️  Couldn't click: {e}")
        else:
            print("  ⚠️  No spotlight button found")

        print("\n" + "="*70)
        print("PHASE 3: DETECTING SPOTLIGHT STATE")
        print("="*70 + "\n")

        # Check current state
        current_state = page.evaluate("""() => {
            const state = {
                bodyClasses: document.body.className,
                htmlClasses: document.documentElement.className,
                hasSpotlightInBody: document.body.className.toLowerCase().includes('spotlight'),
                allClassesWithSpotlight: []
            };

            // Find all elements with 'spotlight' in class
            const allElements = document.querySelectorAll('*');
            allElements.forEach(elem => {
                if (elem.className && typeof elem.className === 'string') {
                    if (elem.className.toLowerCase().includes('spotlight')) {
                        state.allClassesWithSpotlight.push({
                            tag: elem.tagName,
                            classes: elem.className
                        });
                    }
                }
            });

            return state;
        }""")

        print(f"Body has 'spotlight': {current_state['hasSpotlightInBody']}")
        print(f"Elements with 'spotlight' in class: {len(current_state['allClassesWithSpotlight'])}")

        if current_state['allClassesWithSpotlight']:
            print("\n  Elements with spotlight:")
            for item in current_state['allClassesWithSpotlight'][:5]:
                print(f"    <{item['tag']}> {item['classes'][:60]}")

        print("\n" + "="*70)
        print("PHASE 4: TESTING FULLSCREEN ACTIVATION")
        print("="*70 + "\n")

        # Method 1: JavaScript API
        print("[Method 1] JavaScript Fullscreen API...")
        try:
            fullscreen_result = page.evaluate("""() => {
                const elem = document.documentElement;
                if (elem.requestFullscreen) {
                    elem.requestFullscreen();
                    return { success: true, method: 'requestFullscreen' };
                } else if (elem.webkitRequestFullscreen) {
                    elem.webkitRequestFullscreen();
                    return { success: true, method: 'webkitRequestFullscreen' };
                } else {
                    return { success: false, method: 'none' };
                }
            }""")
            print(f"  Result: {fullscreen_result}")
            time.sleep(3)

            is_fullscreen = page.evaluate("() => !!document.fullscreenElement")
            print(f"  Is fullscreen: {is_fullscreen}")

            if is_fullscreen:
                print("  ✅ Fullscreen activated!")
                page.screenshot(path='gamma_fullscreen_active.png')
                print("  📸 Screenshot: gamma_fullscreen_active.png")
        except Exception as e:
            print(f"  ⚠️  Error: {e}")

        # Method 2: Look for fullscreen button
        print("\n[Method 2] Searching for fullscreen button...")
        fullscreen_button = page.evaluate("""() => {
            const buttons = document.querySelectorAll('button');
            for (const btn of buttons) {
                const text = (btn.innerText + ' ' + (btn.getAttribute('aria-label') || '') + ' ' + (btn.getAttribute('title') || '')).toLowerCase();
                if (text.includes('full') || text.includes('expand')) {
                    return {
                        found: true,
                        text: btn.innerText,
                        ariaLabel: btn.getAttribute('aria-label'),
                        title: btn.getAttribute('title')
                    };
                }
            }
            return { found: false };
        }""")

        if fullscreen_button['found']:
            print(f"  ✅ Found button with 'full' or 'expand'!")
            print(f"     Text: {fullscreen_button['text']}")
            print(f"     Aria: {fullscreen_button['ariaLabel']}")
            print(f"     Title: {fullscreen_button['title']}")
        else:
            print("  ⚠️  No fullscreen button found")

        # Method 3: Try 'F' key
        print("\n[Method 3] Trying 'F' key...")
        page.keyboard.press('f')
        time.sleep(2)
        is_fullscreen_f = page.evaluate("() => !!document.fullscreenElement")
        print(f"  Is fullscreen after 'F': {is_fullscreen_f}")

        if is_fullscreen_f:
            print("  ✅ 'F' key activated fullscreen!")
            page.screenshot(path='gamma_fullscreen_f_key.png')

        print("\n" + "="*70)
        print("PHASE 5: EXAMINING KEYBOARD EVENT HANDLERS")
        print("="*70 + "\n")

        # Check what keys are listened to
        keyboard_info = page.evaluate("""() => {
            const info = {
                windowListeners: {
                    keydown: !!window.onkeydown,
                    keyup: !!window.onkeyup,
                    keypress: !!window.onkeypress
                },
                documentListeners: {
                    keydown: !!document.onkeydown,
                    keyup: !!document.onkeyup,
                    keypress: !!document.onkeypress
                }
            };

            return info;
        }""")

        print(f"Window keyboard listeners: {keyboard_info['windowListeners']}")
        print(f"Document keyboard listeners: {keyboard_info['documentListeners']}")

        # Save all findings
        all_findings = {
            'controls': controls_analysis,
            'spotlight': spotlight_results,
            'current_state': current_state,
            'keyboard': keyboard_info
        }

        with open('gamma_controls_deep_dive.json', 'w') as f:
            json.dump(all_findings, f, indent=2)

        print("\n💾 All findings saved to: gamma_controls_deep_dive.json")

        print("\n" + "="*70)
        print("FINAL RECOMMENDATIONS")
        print("="*70 + "\n")

        print("Check the screenshots:")
        print("  1. gamma_before_spotlight.png - Initial state")
        print("  2. gamma_after_s_key.png - After pressing 'S'")
        print("  3. gamma_fullscreen_active.png - Fullscreen active (if worked)")

        print("\nBrowser will stay open for 30 seconds...")
        print("Manually try:")
        print("  - Press 'S' to toggle spotlight")
        print("  - Press 'F' to try fullscreen")
        print("  - Look for buttons in the UI")
        time.sleep(30)

        browser.close()

if __name__ == "__main__":
    try:
        from playwright.sync_api import sync_playwright
        deep_dive_controls()
    except ImportError:
        print("ERROR: Playwright not installed")
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

    input("\nPress Enter to exit...")
