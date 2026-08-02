// static/js/common.js
// 项目全局通用 JavaScript 文件
// 作用：放置所有页面共享的初始化逻辑、工具函数、事件监听等
// 使用方式：在 base.html 的 {% include "includes/js.html" %} 中已引入

// 防止全局变量污染，使用立即执行函数
(function () {
    'use strict';

    // =============================================
    // 1. 全局变量与配置
    // =============================================
    const config = {
        navbarScrolledClass: 'scrolled',        // 导航栏滚动后添加的类名
        scrollThreshold: 50,                    // 滚动多少像素后触发 navbar 变化（像素）
        toastDuration: 5000,                    // flash 消息自动消失时间（毫秒）
    };


    // =============================================
    // 2. 导航栏滚动效果
    // =============================================
    function initNavbarScroll() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;

        window.addEventListener('scroll', () => {
            if (window.scrollY > config.scrollThreshold) {
                navbar.classList.add(config.navbarScrolledClass);
            } else {
                navbar.classList.remove(config.navbarScrolledClass);
            }
        });

        // 页面加载时立即检查一次（防止刷新后状态错误）
        if (window.scrollY > config.scrollThreshold) {
            navbar.classList.add(config.navbarScrolledClass);
        }
    }


    // =============================================
    // 3. Bootstrap Toast 自动关闭（可选增强）
    // =============================================
    function initToasts() {
        const toasts = document.querySelectorAll('.toast');
        toasts.forEach(toastEl => {
            const toast = new bootstrap.Toast(toastEl, {
                autohide: true,
                delay: config.toastDuration
            });
            toast.show();
        });
    }


    // =============================================
    // 3.5 卡片图标摇摆动画
    // =============================================
    function initCardIconSwing() {
        const style = document.createElement('style');
        style.textContent = `
            .entry-card-figure .bi {
                display: inline-block;
                transition: transform 0.3s ease;
            }
            .entry-card:hover .entry-card-figure .bi {
                animation: cardIconSwing 0.6s ease-in-out;
            }
            @keyframes cardIconSwing {
                0%, 100% { transform: rotate(0deg); }
                25% { transform: rotate(8deg); }
                75% { transform: rotate(-8deg); }
            }
        `;
        document.head.appendChild(style);
    }


    // =============================================
    // 4. 全局 AJAX 错误统一处理（后续使用 axios 或 fetch 时可扩展）
    // =============================================
    // 示例：如果以后使用 fetch，可在此统一处理 401、403 等错误
    function setupGlobalAjaxError() {
        document.addEventListener('ajaxError', function(e) {
            if (e.detail && e.detail.status === 401) {
                window.location.href = '/accounts/login/';
            }
        });
    }


    // =============================================
    // 5. 页面加载完成后统一初始化
    // =============================================
    document.addEventListener('DOMContentLoaded', () => {
        // FFE 项目跟进系统 - common.js 已加载

        // 初始化导航栏滚动效果
        initNavbarScroll();

        // 初始化 Toast 消息
        initToasts();

        // 初始化卡片图标摇摆动画
        initCardIconSwing();

        // 初始化全局 AJAX 错误处理（可选）
        setupGlobalAjaxError();

        // 更新北京时间显示
        window.FFE.updateBeijingTime();

        // 后续可在此添加更多全局初始化逻辑
        // 如：表单自动聚焦、暗黑模式切换、图片懒加载等
    });


    // =============================================
    // 6. 暴露全局工具函数
    // =============================================
    window.FFE = window.FFE || {};

    // 格式化日期
    window.FFE.formatDate = function(date) {
        return date.toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    // 显示成功提示
    window.FFE.showSuccess = function(message) {
        alert(message);
    };

    // 获取并显示北京时间
    window.FFE.updateBeijingTime = function() {
        const timeElement = document.getElementById('current-beijing-time');
        if (!timeElement) return;

        window.FFE.apiGet('/api/v1/time/current')
            .then(response => response.json())
            .then(data => {
                if (data.data && data.data.time) {
                    timeElement.textContent = data.data.time;
                }
            })
            .catch(error => {
                const now = new Date();
                const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
                const year = now.getFullYear();
                const month = String(now.getMonth() + 1).padStart(2, '0');
                const day = String(now.getDate()).padStart(2, '0');
                const weekday = weekdays[now.getDay()];
                const hours = String(now.getHours()).padStart(2, '0');
                const minutes = String(now.getMinutes()).padStart(2, '0');
                const seconds = String(now.getSeconds()).padStart(2, '0');
                timeElement.textContent = `${year}-${month}-${day} ${weekday} ${hours}:${minutes}:${seconds}`;
            });
    };

    // 获取 CSRF Token：优先读 Cookie，读不到（如 CSRF_COOKIE_HTTPONLY）时回退到 meta 标签
    window.FFE.getCsrfToken = function() {
        var name = 'csrftoken';
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        if (!cookieValue) {
            var meta = document.querySelector('meta[name="csrf-token"]');
            if (meta && meta.content) {
                cookieValue = meta.content;
            }
        }
        return cookieValue;
    };

    // 显示自定义 Toast 通知
    window.FFE.showToast = function(message, type, delay) {
        type = type || 'info';
        delay = delay || 3000;
        var container = document.getElementById('customToastContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'customToastContainer';
            container.className = 'custom-toast-container';
            document.body.appendChild(container);
        }
        var toast = document.createElement('div');
        toast.className = 'custom-toast ' + type;
        var span = document.createElement('span');
        span.className = 'fw-medium';
        span.textContent = message;
        toast.appendChild(span);
        var closeBtn = document.createElement('button');
        closeBtn.className = 'close-btn';
        closeBtn.setAttribute('aria-label', '关闭');
        closeBtn.textContent = '×';
        toast.appendChild(closeBtn);
        container.appendChild(toast);
        setTimeout(function() { toast.classList.add('show'); }, 100);
        toast.querySelector('.close-btn').addEventListener('click', function() {
            toast.classList.remove('show');
            setTimeout(function() { toast.remove(); }, 300);
        });
        setTimeout(function() {
            toast.classList.remove('show');
            setTimeout(function() { toast.remove(); }, 300);
        }, delay);
    };

    // 统一的 POST 请求（带 CSRF）
    window.FFE.apiPost = function(url, data) {
        return fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.FFE.getCsrfToken()
            },
            body: JSON.stringify(data),
            credentials: 'include'
        });
    };

    // 统一的 GET 请求
    window.FFE.apiGet = function(url) {
        return fetch(url, {
            credentials: 'include'
        });
    };

    // 统一的 fetch 错误处理
    window.FFE.handleFetchError = function(error, showToast_) {
        if (showToast_ !== false) {
            console.error('请求失败:', error);
            window.FFE.showToast('操作失败，请重试', 'danger');
        }
    };

    // 统一的 fetch 响应处理（含 401 重定向和错误 toast）
    window.FFE.handleFetchResponse = function(response) {
        if (response.status === 401) {
            window.location.href = '/accounts/login/';
            return null;
        }
        if (!response.ok) {
            return response.json().then(function(data) {
                window.FFE.showToast(data.error || '请求失败', 'danger');
                return null;
            });
        }
        return response.json();
    };

    // 拖放工具
    window.FFE.DragDrop = {
        draggingCard: null,

        makeSortable: function(containerSelector, cardSelector, slotSelector, onDropCallback) {
            var cards = document.querySelectorAll(cardSelector);
            var slots = document.querySelectorAll(slotSelector);

            cards.forEach(function(card) {
                card.addEventListener('dragstart', function(e) {
                    window.FFE.DragDrop.draggingCard = e.target.closest(cardSelector);
                    window.FFE.DragDrop.draggingCard.classList.add('dragging');
                    e.dataTransfer.effectAllowed = 'move';
                    e.dataTransfer.setData('text/plain', '');
                });
                card.addEventListener('dragend', function(e) {
                    if (window.FFE.DragDrop.draggingCard) {
                        window.FFE.DragDrop.draggingCard.classList.remove('dragging');
                    }
                    document.querySelectorAll(slotSelector).forEach(function(slot) {
                        slot.classList.remove('drag-over');
                    });
                });
            });

            slots.forEach(function(slot) {
                slot.addEventListener('dragover', function(e) {
                    e.preventDefault();
                    e.dataTransfer.dropEffect = 'move';
                });
                slot.addEventListener('dragenter', function(e) {
                    e.preventDefault();
                    var s = e.target.closest(slotSelector);
                    if (s) s.classList.add('drag-over');
                });
                slot.addEventListener('dragleave', function(e) {
                    var s = e.target.closest(slotSelector);
                    if (s && !s.contains(e.relatedTarget)) {
                        s.classList.remove('drag-over');
                    }
                });
                slot.addEventListener('drop', function(e) {
                    e.preventDefault();
                    var toSlot = e.target.closest(slotSelector);
                    var draggingCard = window.FFE.DragDrop.draggingCard;
                    if (!toSlot || !draggingCard) return;
                    if (onDropCallback) {
                        onDropCallback(draggingCard, toSlot);
                    }
                });
            });
        }
    };

})();
