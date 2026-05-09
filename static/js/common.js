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
        // 目前留空，待后续引入 axios 或其他库时实现
        // 示例代码：
        // document.addEventListener('ajaxError', (e) => {
        //     if (e.detail.status === 401) {
        //         window.location.href = '/auth/login';
        //     }
        // });
    }


    // =============================================
    // 5. 页面加载完成后统一初始化
    // =============================================
    document.addEventListener('DOMContentLoaded', () => {
        console.log('FFE 项目跟进系统 - common.js 已加载');

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
    // 6. 暴露全局工具函数（可选）
    // =============================================
    window.FFE = window.FFE || {};

    // 示例：格式化日期
    window.FFE.formatDate = function(date) {
        return date.toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    // 示例：显示成功提示（后续可结合 sweetalert2）
    window.FFE.showSuccess = function(message) {
        alert(message); // 临时使用 alert，后续可替换为美观组件
    };

    // 获取并显示北京时间
    window.FFE.updateBeijingTime = function() {
        const timeElement = document.getElementById('current-beijing-time');
        if (!timeElement) return;

        // 从后端API获取时间
        fetch('/api/v1/time/current')
            .then(response => response.json())
            .then(data => {
                if (data.time) {
                    timeElement.textContent = data.time;
                }
            })
            .catch(error => {
                console.error('获取时间失败:', error);
                // 降级使用本地时间
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

})();
