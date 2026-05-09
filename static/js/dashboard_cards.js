// 功能卡片区域 JavaScript

(function() {
    'use strict';

    const CLOCK_API_URL = '/modules/system/clock/api/time/';
    let cardPositions = {};
    let availableModules = [];
    let draggingCard = null;

    async function initDashboardCards() {
        try {
            const response = await fetch('/api/v1/user/dashboard/cards/', {
                credentials: 'include'
            });
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
            const response = await fetch(CLOCK_API_URL, {
                credentials: 'include'
            });
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
        const cards = document.querySelectorAll('.clock-card');
        const slots = document.querySelectorAll('.card-slot');
        
        cards.forEach(card => {
            card.addEventListener('dragstart', onDragStart);
            card.addEventListener('dragend', onDragEnd);
        });
        
        slots.forEach(slot => {
            slot.addEventListener('dragover', onDragOver);
            slot.addEventListener('drop', onDrop);
            slot.addEventListener('dragenter', onDragEnter);
            slot.addEventListener('dragleave', onDragLeave);
        });
    }

    function onDragStart(e) {
        draggingCard = e.target;
        e.target.classList.add('dragging');
        e.dataTransfer.setData('text/plain', e.target.closest('.card-slot').dataset.position);
        e.dataTransfer.effectAllowed = 'move';
    }

    function onDragEnd(e) {
        e.target.classList.remove('dragging');
        document.querySelectorAll('.card-slot').forEach(slot => {
            slot.classList.remove('drag-over');
        });
    }

    function onDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    }

    function onDragEnter(e) {
        e.preventDefault();
        e.target.closest('.card-slot').classList.add('drag-over');
    }

    function onDragLeave(e) {
        e.target.closest('.card-slot').classList.remove('drag-over');
    }

    function onDrop(e) {
        e.preventDefault();
        const fromPosition = e.dataTransfer.getData('text/plain');
        const toSlot = e.target.closest('.card-slot');
        const toPosition = toSlot.dataset.position;
        
        if (fromPosition === toPosition) return;
        
        const fromSlot = document.querySelector(`.card-slot[data-position="${fromPosition}"]`);
        const toCard = toSlot.querySelector('.clock-card');
        const fromCard = fromSlot.querySelector('.clock-card');
        
        if (toCard && fromCard) {
            toSlot.appendChild(fromCard);
            fromSlot.appendChild(toCard);
            
            swapPositions(fromPosition, toPosition);
            saveCardPositions();
        } else if (fromCard && !toCard) {
            toSlot.appendChild(fromCard);
            swapPositions(fromPosition, toPosition);
            saveCardPositions();
        }
    }

    function swapPositions(from, to) {
        const temp = cardPositions[from];
        cardPositions[from] = cardPositions[to];
        cardPositions[to] = temp;
    }

    async function saveCardPositions() {
        try {
            const response = await fetch('/api/v1/user/dashboard/cards/save/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                },
                body: JSON.stringify({ positions: cardPositions }),
                credentials: 'include',
            });
            const data = await response.json();
            if (!data.success) {
                console.error('保存卡片布局失败:', data.error);
            }
        } catch (error) {
            console.error('保存卡片布局失败:', error);
        }
    }

    function getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDashboardCards);
    } else {
        initDashboardCards();
    }
})();
