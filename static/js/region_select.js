/**
 * 省市县三级联动选择器
 * 用于表单中的省市区选择
 */

document.addEventListener('DOMContentLoaded', function() {
    initRegionSelectWidgets();
});

function populateSelect(select, data, initialValue) {
    data.forEach(function(item) {
        var opt = document.createElement('option');
        opt.value = item.code;
        opt.textContent = item.name;
        if (item.code === initialValue) opt.selected = true;
        select.appendChild(opt);
    });
}

function loadProvinces(widget) {
    const provinceSelect = widget.querySelector('.region-province');
    const citySelect = widget.querySelector('.region-city');
    const districtSelect = widget.querySelector('.region-district');
    const hiddenInput = widget.querySelector('input[type="hidden"]');

    if (!provinceSelect || !citySelect || !districtSelect || !hiddenInput) return;

    let initialData = {province: '', city: '', district: ''};
    try {
        initialData = JSON.parse(hiddenInput.value) || initialData;
    } catch(e) {}

    const provinceApi = provinceSelect.dataset.api;
    window.FFE.apiGet(provinceApi)
        .then(r => r.json())
        .then(json => {
            if (json && json.data) {
                provinceSelect.innerHTML = '<option value="">请选择省份</option>';
                populateSelect(provinceSelect, json.data, initialData.province);

                if (initialData.province) {
                    loadCities(initialData.province, citySelect, districtSelect, initialData.city, initialData.district);
                }
            }
        })
        .catch(err => {
            console.error('加载省份失败:', err);
        });
}

function bindRegionEvents(widget) {
    const provinceSelect = widget.querySelector('.region-province');
    const citySelect = widget.querySelector('.region-city');
    const districtSelect = widget.querySelector('.region-district');
    const hiddenInput = widget.querySelector('input[type="hidden"]');

    if (!provinceSelect || !citySelect || !districtSelect || !hiddenInput) return;

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

    citySelect.addEventListener('change', function() {
        const cityCode = this.value;

        districtSelect.innerHTML = '<option value="">请先选择城市</option>';
        districtSelect.disabled = !cityCode;

        updateHiddenInput(hiddenInput, provinceSelect.value, cityCode, '');

        if (cityCode) {
            loadDistricts(cityCode, districtSelect, '');
        }
    });

    districtSelect.addEventListener('change', function() {
        updateHiddenInput(hiddenInput, provinceSelect.value, citySelect.value, this.value);
    });
}

function initRegionSelectWidgets() {
    document.querySelectorAll('.region-select-widget').forEach(function(widget) {
        loadProvinces(widget);
        bindRegionEvents(widget);
    });
}

function loadCities(provinceCode, citySelect, districtSelect, initialCity, initialDistrict) {
    const cityApi = citySelect.dataset.api;
    window.FFE.apiGet(cityApi + '?province=' + provinceCode)
        .then(r => r.json())
        .then(json => {
            if (json && json.data) {
                citySelect.innerHTML = '<option value="">请选择城市</option>';
                populateSelect(citySelect, json.data, initialCity);
                citySelect.disabled = false;
                
                if (initialCity) {
                    loadDistricts(initialCity, districtSelect, initialDistrict);
                }
            }
        });
}

function loadDistricts(cityCode, districtSelect, initialDistrict) {
    const districtApi = districtSelect.dataset.api;
    window.FFE.apiGet(districtApi + '?city=' + cityCode)
        .then(r => r.json())
        .then(json => {
            if (json && json.data) {
                districtSelect.innerHTML = '<option value="">请选择区县</option>';
                populateSelect(districtSelect, json.data, initialDistrict);
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
