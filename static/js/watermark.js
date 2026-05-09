/**
 * watermark.js
 * 网页水印防护脚本
 * 用于防止用户移除水印或使用开发者工具
 */

(function() {
    'use strict';

    // 获取水印容器配置
    const container = document.getElementById('watermarkContainer');
    if (!container) return;

    // 从data属性获取配置
    const watermarkText = container.getAttribute('data-watermark-text') || '';
    const enableShortcut = container.getAttribute('data-enable-shortcut') === 'true';
    const enableDetection = container.getAttribute('data-enable-detection') === 'true';

    const warningEl = document.getElementById('watermarkWarning');

    // 禁用快捷键
    if (enableShortcut) {
        document.addEventListener('keydown', function(e) {
            // 禁用 F12
            if (e.key === 'F12') {
                e.preventDefault();
                return false;
            }
            // 禁用 Ctrl+Shift+I (开发者工具)
            if (e.ctrlKey && e.shiftKey && e.key === 'I') {
                e.preventDefault();
                return false;
            }
            // 禁用 Ctrl+Shift+J (控制台)
            if (e.ctrlKey && e.shiftKey && e.key === 'J') {
                e.preventDefault();
                return false;
            }
            // 禁用 Ctrl+U (查看源代码)
            if (e.ctrlKey && e.key === 'u') {
                e.preventDefault();
                return false;
            }
            // 禁用 Ctrl+Shift+C (检查元素)
            if (e.ctrlKey && e.shiftKey && e.key === 'C') {
                e.preventDefault();
                return false;
            }
        });
    }

    // 检测控制台打开 - 简化版，只在控制台真的打开时警告
    if (enableDetection) {
        let warningShown = false;
        let consoleOpened = false;
        
        // 使用更可靠的方法检测控制台
        setInterval(function() {
            if (consoleOpened) return;
            
            // 检测控制台是否打开
            if (window.console && window.console.log.toString().indexOf('native code') === -1) {
                // 控制台被重写，说明打开了
                if (!warningShown && warningEl) {
                    warningShown = true;
                    consoleOpened = true;
                    warningEl.style.display = 'block';
                    setTimeout(function() {
                        if (warningEl) warningEl.style.display = 'none';
                    }, 5000);
                }
            }
        }, 2000);
    }

    // 防止通过 CSS 隐藏水印
    const style = document.createElement('style');
    style.textContent = `
        .watermark-container { 
            display: block !important; 
            visibility: visible !important;
        }
        .watermark-container[style*="display: none"] { 
            display: block !important; 
        }
        .watermark-container[style*="display:none"] { 
            display: block !important; 
        }
        .watermark-container[style*="visibility: hidden"] {
            visibility: visible !important;
        }
    `;
    document.head.appendChild(style);

    console.log('[Watermark] 水印防护已启用');

})();
