/**
 * Antigravity Frontend DOM Dynamic Localization Engine v2.1
 * Deep localization covering secondary menus, settings tabs, and small explanatory notes.
 */
(() => {
    // Prevent double execution
    if (window.__ag_hanhua_engine__) {
        try { window.__ag_hanhua_engine__.disconnect(); } catch (e) {}
        delete window.__ag_hanhua_engine__;
    }

    // Load dictionary
    const dictMap = new Map();
    const lowerMap = new Map();

    const rawDict = window.__AG_ZH_DICT__ || {};
    for (const [k, v] of Object.entries(rawDict)) {
        if (!k || !v) continue;
        const normK = norm(k);
        dictMap.set(normK, v);
        lowerMap.set(normK.toLowerCase(), v);
    }

    // Protected keywords (Never replace as substrings)
    const PROTECTED_TERMS = [
        'antigravity', 'jetski', 'gemini', 'google ai', 'best of n',
        'google chrome', 'marketplace', 'mcp', 'citc', 'git', 'github',
        'python', 'node', 'powershell', 'bash', 'npm'
    ];

    function isProtected(s) {
        const low = s.toLowerCase();
        for (const p of PROTECTED_TERMS) {
            if (low.includes(p)) return true;
        }
        return false;
    }

    // Phrase replacement list (sorted descending by length, >= 12 chars)
    const phraseEntries = [...dictMap.entries()]
        .filter(e => e[0].length >= 12)
        .sort((a, b) => b[0].length - a[0].length);

    // Cache to prevent re-processing unmodified nodes
    const lastSeen = new WeakMap();
    const misses = new Set();

    // Critical blocklist to prevent modifying code, commands, editor, and terminal output
    const BLOCKED_TAGS = [
        'SCRIPT', 'STYLE', 'CODE', 'PRE', 'INPUT', 'TEXTAREA',
        'SVG', 'CANVAS', 'SYMBOL', 'PATH', 'MATH', 'KBD'
    ];

    // Only block actual code editor lines and terminal lines
    const BLOCKED_CLASS_SUBSTR = [
        'monaco-editor', 'suggest-widget', 'code-block'
    ];

    const BLOCKED_CLASS_TOKEN = ['terminal', 'xterm'];

    const TRANSLATABLE_ATTRS = [
        'placeholder', 'title', 'aria-label', 'alt',
        'data-title', 'data-tooltip-content', 'data-tooltip', 'tooltip',
        'aria-description', 'aria-placeholder'
    ];

    function norm(s) {
        if (!s) return '';
        return s.replace(/\s+/g, ' ')
                .replace(/[’‘]/g, "'")
                .replace(/[“”]/g, '"')
                .trim();
    }

    function isInBlockedZone(node) {
        let curr = node.nodeType === Node.TEXT_NODE ? node.parentElement : node;
        let depth = 0;
        while (curr && depth < 25) {
            if (curr.nodeType === Node.ELEMENT_NODE) {
                const tag = curr.tagName.toUpperCase();
                if (BLOCKED_TAGS.includes(tag)) return true;
                if (curr.getAttribute('contenteditable') === 'true') return true;

                const className = curr.className;
                if (typeof className === 'string') {
                    if (BLOCKED_CLASS_SUBSTR.some(cls => className.includes(cls))) return true;
                    const tokens = className.split(/\s+/);
                    if (tokens.some(t => BLOCKED_CLASS_TOKEN.includes(t))) return true;
                }
                const role = curr.getAttribute('role') || '';
                if (role === 'code' || role === 'img') return true;
            }
            curr = curr.parentElement || (curr.parentNode && curr.parentNode.host);
            depth++;
        }
        return false;
    }

    function cnDuration(s) {
        return s
            .replace(/([0-9]+)\s*days?/gi, '$1 天')
            .replace(/([0-9]+)\s*hours?/gi, '$1 小时')
            .replace(/([0-9]+)\s*minutes?/gi, '$1 分钟')
            .replace(/([0-9]+)\s*seconds?/gi, '$1 秒')
            .replace(/,\s*/g, ' ');
    }

    const REGEX_RULES = [
        // Quota & Rate limits
        [/^You have used some of your weekly limit, it will fully refresh in (.+)[.]$/i,
         (m, a) => '你已使用部分每周限额，将在 ' + cnDuration(a) + ' 后完全刷新。'],
        [/^You have used some of your (5-hour|five hour) limit, it will fully refresh in (.+)[.]$/i,
         (m, a, b) => '你已使用部分五小时限额，将在 ' + cnDuration(b) + ' 后完全刷新。'],
        [/^in (Antigravity)$/i, (m, a) => '（在 ' + a + ' 中）'],
        [/^Send feedback as (.+)$/i, (m, a) => '以 ' + a + ' 身份发送反馈'],
        
        // Selectors & Presets
        [/^Select model,\s*current:\s*(.+)$/i, (m, a) => '选择模型，当前：' + a],
        [/^Agent permissions preset selector,\s*current:\s*(.+)$/i, (m, a) => '智能体权限预设选择器，当前：' + a],
        
        // Actions & Queuing
        [/^(.+?)\s+Sends immediately$/i, (m, a) => a + ' 立即发送'],
        [/^(.+?)\s+Queues after the turn$/i, (m, a) => a + ' 排队等待当前轮次结束后发送'],
        
        // Dynamic time & count
        [/^Thought for\s*(\d+)\s*s$/i, (m, s) => '思考了 ' + s + ' 秒'],
        [/^Thought for\s*(\d+)\s*m(?:\s*(\d+)\s*s)?$/i, (m, min, sec) => '思考了 ' + min + ' 分钟' + (sec ? (' ' + sec + ' 秒') : '')],
        [/^Worked for\s*(\d+)\s*m$/i, (m, min) => '工作了 ' + min + ' 分钟'],
        [/^Worked for\s*(\d+)\s*s$/i, (m, sec) => '工作了 ' + sec + ' 秒'],
        [/^(\d+)\s*files?\s*changed$/i, (m, count) => count + ' 个文件已更改'],
        [/^(\d+)\s*suggestions?$/i, (m, count) => count + ' 条建议'],
        [/^(\d+)\s*d\s*ago$/i, (m, d) => d + ' 天前'],
        [/^(\d+)\s*h\s*ago$/i, (m, h) => h + ' 小时前'],
        [/^(\d+)\s*m\s*ago$/i, (m, min) => min + ' 分钟前'],
        [/^(\d+)\s*s\s*ago$/i, (m, sec) => sec + ' 秒前'],
        [/^just now$/i, () => '刚刚'],
        [/^Load older messages,\s*showing\s*(\d+)\s*of\s*(\d+)$/i, (m, a, b) => '加载更早的消息，显示 ' + a + ' / ' + b],
        [/^Step\s*(\d+)\s*of\s*(\d+)$/i, (m, a, b) => '第 ' + a + ' 步，共 ' + b + ' 步'],
        [/^Showing\s*(\d+)\s*of\s*(\d+)$/i, (m, a, b) => '显示第 ' + a + ' 项，共 ' + b + ' 项']
    ];

    function applyRegexRules(text) {
        for (const [re, fn] of REGEX_RULES) {
            if (re.test(text)) return text.replace(re, fn);
        }
        return text;
    }

    // Smart lookup with punctuation and shortcut handling
    function lookupWord(raw) {
        if (!raw) return null;
        const t = norm(raw);
        if (!t) return null;

        // 1. Direct match
        if (dictMap.has(t)) return dictMap.get(t);
        const low = t.toLowerCase();
        if (lowerMap.has(low) && t.length < 50) return lowerMap.get(low);

        // 2. Shortcut suffix match, e.g. "Cancel (Ctrl+D)" -> "取消 (Ctrl+D)"
        const scMatch = t.match(/^(.+?)\s*\(((?:Ctrl|Alt|Shift|Cmd|Meta|Win|Enter|Tab|Esc|Option|⌥|⌅|⇧|\+|-|[A-Za-z0-9])(?:[+-][A-Za-z0-9]+)*)\)$/);
        if (scMatch) {
            const base = scMatch[1].trim();
            const sc = scMatch[2];
            const baseTr = lookupWord(base);
            if (baseTr) {
                return baseTr + ' (' + sc + ')';
            }
        }

        // 3. Trailing punctuation, e.g. "Settings:" -> "设置:" or "Save..." -> "保存..."
        const puncMatch = t.match(/^(.+?)([:?…\.]+)$/);
        if (puncMatch) {
            const base = puncMatch[1].trim();
            const punc = puncMatch[2];
            const baseTr = lookupWord(base);
            if (baseTr) {
                return baseTr + punc;
            }
        }

        // 4. Bracketed tags, e.g. "(Recommended)" -> "(推荐)"
        const bMatch = t.match(/^\((.+?)\)$/);
        if (bMatch) {
            const base = bMatch[1].trim();
            const baseTr = lookupWord(base);
            if (baseTr) {
                return '(' + baseTr + ')';
            }
        }

        // 5. Dynamic regex rules
        const byRegex = applyRegexRules(t);
        if (byRegex !== t) return byRegex;

        return null;
    }

    function smartReplace(text) {
        let result = text;
        for (const [key, val] of phraseEntries) {
            if (result.indexOf(key) === -1) continue;
            let idx = result.indexOf(key);
            while (idx !== -1) {
                const before = idx > 0 ? result[idx - 1] : '';
                const afterIdx = idx + key.length;
                const after = afterIdx < result.length ? result[afterIdx] : '';
                const isWordBoundary =
                    (!/[\u4e00-\u9fa5A-Za-z0-9]/.test(before)) &&
                    (!/[\u4e00-\u9fa5A-Za-z0-9]/.test(after));
                if (isWordBoundary) {
                    result = result.slice(0, idx) + val + result.slice(afterIdx);
                    idx = result.indexOf(key, idx + val.length);
                } else {
                    idx = result.indexOf(key, idx + key.length);
                }
            }
        }
        return result;
    }

    function translateAttrValue(raw) {
        const tr = lookupWord(raw);
        if (tr && tr !== raw) return tr;
        return null;
    }

    function translateNode(node) {
        try {
            if (!node) return;

            if (node.nodeType === Node.ELEMENT_NODE) {
                const tag = node.tagName.toUpperCase();
                if (BLOCKED_TAGS.includes(tag) && tag !== 'INPUT' && tag !== 'TEXTAREA') return;

                // Translatable UI attributes (metadata: placeholder, title, aria-label, etc.)
                for (const attr of TRANSLATABLE_ATTRS) {
                    const v = node.getAttribute(attr);
                    if (v) {
                        const t = translateAttrValue(v);
                        if (t !== null && t !== v) {
                            node.setAttribute(attr, t);
                        }
                    }
                }

                if (node.shadowRoot) translateNode(node.shadowRoot);
                for (const child of node.childNodes) translateNode(child);

            } else if (node.nodeType === Node.TEXT_NODE) {
                const originalVal = node.nodeValue;
                if (!originalVal || originalVal.trim().length < 1) return;
                if (lastSeen.get(node) === originalVal) return;
                if (!/[A-Za-z]/.test(originalVal)) {
                    lastSeen.set(node, originalVal);
                    return;
                }
                if (isInBlockedZone(node)) {
                    lastSeen.set(node, originalVal);
                    return;
                }

                let newVal = lookupWord(originalVal);

                if (!newVal && !isProtected(norm(originalVal))) {
                    newVal = smartReplace(norm(originalVal));
                }

                if (newVal && newVal !== originalVal && newVal !== norm(originalVal)) {
                    const leading = originalVal.match(/^\s*/)[0];
                    const trailing = originalVal.match(/\s*$/)[0];
                    const finalVal = leading + newVal + trailing;
                    node.nodeValue = finalVal;
                    lastSeen.set(node, finalVal);
                } else {
                    lastSeen.set(node, originalVal);
                    if (misses.size < 1000 && originalVal.trim().length >= 3) {
                        misses.add(norm(originalVal));
                    }
                }
            }
        } catch (e) {}
    }

    const observer = new MutationObserver(mutations => {
        for (const m of mutations) {
            if (m.type === 'childList') {
                for (const n of m.addedNodes) translateNode(n);
            } else if (m.type === 'characterData') {
                translateNode(m.target);
            } else if (m.type === 'attributes' && m.target) {
                translateNode(m.target);
            }
        }
    });

    const obsOpts = {
        childList: true,
        subtree: true,
        characterData: true,
        attributes: true,
        attributeFilter: TRANSLATABLE_ATTRS
    };

    function rescanAttributes() {
        const root = document.body || document.documentElement;
        if (!root) return;
        const sel = TRANSLATABLE_ATTRS.map(a => '[' + a + ']').join(',');
        for (const el of root.querySelectorAll(sel)) {
            if (!el.isConnected) continue;
            for (const attr of TRANSLATABLE_ATTRS) {
                const v = el.getAttribute(attr);
                if (v) {
                    const t = translateAttrValue(v);
                    if (t !== null && t !== v) el.setAttribute(attr, t);
                }
            }
        }
    }

    let started = false;
    let stopped = false;
    const startEngine = () => {
        if (started || stopped) return;
        const target = document.body || document.documentElement;
        if (!target) return;
        started = true;
        observer.observe(target, obsOpts);
        translateNode(target);
        rescanAttributes();
    };

    // Shadow DOM hook
    if (typeof Element !== 'undefined' && Element.prototype && !Element.prototype.attachShadow.__ag_hooked__) {
        const origAttachShadow = Element.prototype.attachShadow;
        const hooked = function () {
            const sr = origAttachShadow.apply(this, arguments);
            const eng = window.__ag_hanhua_engine__;
            if (eng && eng.observe) {
                try { eng.observe(sr); } catch (e) {}
            }
            return sr;
        };
        hooked.__ag_hooked__ = true;
        Element.prototype.attachShadow = hooked;
    }

    startEngine();
    if (!started && typeof document !== 'undefined') {
        document.addEventListener('DOMContentLoaded', startEngine, { once: true });
    }

    setTimeout(startEngine, 300);
    setTimeout(() => { if (!stopped) { startEngine(); rescanAttributes(); } }, 1200);
    setTimeout(() => { if (!stopped) { startEngine(); rescanAttributes(); } }, 3500);

    const timerId = setInterval(() => {
        if (stopped) return;
        startEngine();
        const root = document.body || document.documentElement;
        if (root) {
            translateNode(root);
            rescanAttributes();
        }
    }, 2000);

    window.__ag_hanhua_engine__ = {
        observe: (root) => observer.observe(root, obsOpts),
        translateNode: translateNode,
        misses: misses,
        disconnect: () => {
            stopped = true;
            try { observer.disconnect(); } catch (e) {}
            try { clearInterval(timerId); } catch (e) {}
        }
    };

    console.log('[AGY-ZH] Antigravity Deep Localization Engine v2.1 running.');
})();
