// 功能卡片区域 JavaScript

(function() {
    'use strict';

    const CLOCK_API_URL = '/modules/system/clock/api/time/';
    let cardPositions = {};
    let availableModules = [];

    async function initDashboardCards() {
        try {
            const response = await window.FFE.apiGet('/api/v1/user/dashboard/cards/');
            const data = await response.json();
            
            if (data.success) {
                cardPositions = data.data.positions;
                availableModules = data.data.available_modules;
                renderCards();
            }
        } catch (error) {
            console.error('加载卡片布局失败:', error);
            initDefaultCards();
        }
    }

    function initDefaultCards() {
        cardPositions = {
            '1': {'module': null, 'size': 'medium', 'config': {}},
            '2': {'module': null, 'size': 'medium', 'config': {}},
            '3': {'module': null, 'size': 'medium', 'config': {}},
            '4': {'module': null, 'size': 'medium', 'config': {}},
            '5': {'module': null, 'size': 'medium', 'config': {}},
            '6': {'module': null, 'size': 'medium', 'config': {}},
        };
        renderCards();
    }

    function renderCards() {
        const slots = document.querySelectorAll('.card-slot');
        
        // 检查是否有任何位置已配置了卡片
        let hasConfiguredCards = Object.values(cardPositions).some(p => p && p.module);
        
        // 如果时钟模块可用且没有已配置的卡片，自动放置到位置1
        if (availableModules.includes('clock') && !hasConfiguredCards) {
            cardPositions['1'] = {'module': 'clock', 'size': 'medium', 'config': {}};
        }
        
        slots.forEach(slot => {
            const position = slot.dataset.position;
            const cardConfig = cardPositions[position];
            
            if (cardConfig && cardConfig.module === 'clock' && availableModules.includes('clock')) {
                loadClockCard(slot);
            }
        });
        
        initDragAndDrop();
    }

    async function loadClockCard(slot) {
        const template = document.getElementById('clock-card-template');
        if (template) {
            const clone = template.content.cloneNode(true);
            const card = clone.querySelector('.clock-card');
            slot.appendChild(card);
            
            await updateClock(card);
            startClockUpdate(card);
        }
    }

    async function updateClock(card) {
        try {
            const response = await window.FFE.apiGet(CLOCK_API_URL);
            const data = await response.json();
            
            if (data.success) {
                const dateEl = card.querySelector('.clock-date');
                const timeEl = card.querySelector('.clock-time');
                const weekdayEl = card.querySelector('.clock-weekday');
                
                if (dateEl) dateEl.textContent = data.data.date;
                if (timeEl) timeEl.textContent = data.data.time;
                if (weekdayEl) weekdayEl.textContent = data.data.weekday;
            }
        } catch (error) {
            console.error('更新时间失败:', error);
        }
    }

    function startClockUpdate(card) {
        updateClock(card);
        setInterval(() => {
            const now = new Date();
            const timeEl = card.querySelector('.clock-time');
            if (timeEl) {
                timeEl.textContent = now.toLocaleTimeString('zh-CN', { hour12: false });
            }
        }, 1000);
    }

    function initDragAndDrop() {
        window.FFE.DragDrop.makeSortable('.card-slot', '.clock-card', '.card-slot', function(card, slot) {
            var currentSlot = card.parentElement;
            var targetSlot = slot;
            if (currentSlot === targetSlot) return;
            var targetCard = targetSlot.querySelector('.clock-card');
            if (targetCard) {
                targetSlot.insertBefore(card, targetCard);
                currentSlot.appendChild(targetCard);
            } else {
                targetSlot.appendChild(card);
            }
            document.querySelectorAll('.clock-card').forEach(function(c, i) {
                c.style.order = i;
            });
        });
    }

    async function saveCardPositions() {
        try {
            const response = await window.FFE.apiPost('/api/v1/user/dashboard/cards/save/', { positions: cardPositions });
            const data = await response.json();
            if (!data.success) {
                console.error('保存卡片布局失败:', data.error);
            }
        } catch (error) {
            console.error('保存卡片布局失败:', error);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDashboardCards);
    } else {
        initDashboardCards();
    }
})();
