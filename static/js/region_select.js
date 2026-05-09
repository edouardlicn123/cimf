/**
 * 省市县三级联动选择器
 * 用于表单中的省市区选择
 */

document.addEventListener('DOMContentLoaded', function() {
    initRegionSelectWidgets();
});

function initRegionSelectWidgets() {
    const widgets = document.querySelectorAll('.region-select-widget');
    
    widgets.forEach(function(widget) {
        const provinceSelect = widget.querySelector('.region-province');
        const citySelect = widget.querySelector('.region-city');
        const districtSelect = widget.querySelector('.region-district');
        const hiddenInput = widget.querySelector('input[type="hidden"]');
        
        if (!provinceSelect || !citySelect || !districtSelect || !hiddenInput) return;
        
        // 解析初始值
        let initialData = {province: '', city: '', district: ''};
        try {
            initialData = JSON.parse(hiddenInput.value) || initialData;
        } catch(e) {}
        
        // 加载省份
        const provinceApi = provinceSelect.dataset.api;
        fetch(provinceApi)
            .then(r => r.json())
            .then(json => {
                if (json && json.data) {
                    provinceSelect.innerHTML = '<option value="">请选择省份</option>';
                    json.data.forEach(p => {
                        const opt = document.createElement('option');
                        opt.value = p.code;
                        opt.textContent = p.name;
                        if (p.code === initialData.province) {
                            opt.selected = true;
                        }
                        provinceSelect.appendChild(opt);
                    });
                    
                    // 如果有初始省份，加载城市
                    if (initialData.province) {
                        loadCities(initialData.province, citySelect, districtSelect, initialData.city, initialData.district);
                    }
                }
            })
            .catch(err => {
                console.error('加载省份失败:', err);
            });
        
        // 省份变更事件
        provinceSelect.addEventListener('change', function() {
            const provinceCode = this.value;
            
            citySelect.innerHTML = '<option value="">请先选择省份</option>';
            districtSelect.innerHTML = '<option value="">请先选择城市</option>';
            citySelect.disabled = !provinceCode;
            districtSelect.disabled = true;
            
            updateHiddenInput(hiddenInput, provinceSelect.value, '', '');
            
            if (provinceCode) {
                loadCities(provinceCode, citySelect, districtSelect, '', '');
            }
        });
        
        // 城市变更事件
        citySelect.addEventListener('change', function() {
            const cityCode = this.value;
            
            districtSelect.innerHTML = '<option value="">请先选择城市</option>';
            districtSelect.disabled = !cityCode;
            
            updateHiddenInput(hiddenInput, provinceSelect.value, cityCode, '');
            
            if (cityCode) {
                loadDistricts(cityCode, districtSelect, '');
            }
        });
        
        // 区县变更事件
        districtSelect.addEventListener('change', function() {
            updateHiddenInput(hiddenInput, provinceSelect.value, citySelect.value, this.value);
        });
    });
}

function loadCities(provinceCode, citySelect, districtSelect, initialCity, initialDistrict) {
    const cityApi = citySelect.dataset.api;
    fetch(cityApi + '?province=' + provinceCode)
        .then(r => r.json())
        .then(json => {
            if (json && json.data) {
                citySelect.innerHTML = '<option value="">请选择城市</option>';
                json.data.forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = c.code;
                    opt.textContent = c.name;
                    if (c.code === initialCity) {
                        opt.selected = true;
                    }
                    citySelect.appendChild(opt);
                });
                citySelect.disabled = false;
                
                if (initialCity) {
                    loadDistricts(initialCity, districtSelect, initialDistrict);
                }
            }
        });
}

function loadDistricts(cityCode, districtSelect, initialDistrict) {
    const districtApi = districtSelect.dataset.api;
    fetch(districtApi + '?city=' + cityCode)
        .then(r => r.json())
        .then(json => {
            if (json && json.data) {
                districtSelect.innerHTML = '<option value="">请选择区县</option>';
                json.data.forEach(d => {
                    const opt = document.createElement('option');
                    opt.value = d.code;
                    opt.textContent = d.name;
                    if (d.code === initialDistrict) {
                        opt.selected = true;
                    }
                    districtSelect.appendChild(opt);
                });
                districtSelect.disabled = false;
            }
        });
}

function updateHiddenInput(hiddenInput, province, city, district) {
    const data = {
        province: province,
        city: city,
        district: district
    };
    hiddenInput.value = JSON.stringify(data);
}
