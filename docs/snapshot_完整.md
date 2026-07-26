# 代码快照

> 自动生成：2026-07-07
> 用途：避免每次 session 全库扫描，减少 token 消耗
> 快速参考（模型/服务索引）见 `docs/snapshot_快速参考.md`

### core/models.py

| 模型 | 基类 | 字段 |
|------|------|------|
| BaseModel | Model | created_at, updated_at |
| ChinaRegion | Model | LEVEL_CHOICES, code, name, level, parent... (+1) |
| SystemSetting | Model | key, value, description, updated_at |
| Taxonomy | BaseModel | name, slug, description |
| TaxonomyItem | BaseModel | taxonomy, name, description, weight |

### modules/clock/models.py

| 模型 | 基类 | 字段 |
|------|------|------|
| ClockModel | Model |  |

### modules/customer/models.py

| 模型 | 基类 | 字段 |
|------|------|------|
| CustomerFields | BaseModel | node, customer_name, customer_code, customer_type, enterprise_name... (+17) |

### modules/resident_info/models.py

| 模型 | 基类 | 字段 |
|------|------|------|
| ResidentInfoFields | Model | node, name, relation, id_card, other_id_type... (+33) |

### modules/whatsapp/models.py

| 模型 | 基类 | 字段 |
|------|------|------|
| WhatsAppTemplate | Model | title, content, is_default |
| SendBatch | Model | template(FK→WhatsAppTemplate), total_count, success_count, failed_count, status, truncated, rate_limited, resume_at, next_send_at, template_ids(JSON) |
| SendLog | Model | batch(FK→SendBatch), customer_id, phone, status, error_message, sent_at, delay_until |
| CheckBatch | Model | status, total, checked, has_wa, no_wa, invalid, format_issue, error_count |
| CheckLog | Model | batch(FK→CheckBatch), customer_id, customer_name, phone, result, attempts, attempt_details(JSON), checked_at |

## 服务层签名

### NodeService ()
| 方法 | 参数 |
|------|------|
| get_nodes | node_type_slug |
| get_node | node_type_slug, node_id |
| get_by_id | node_id |
| create_node | node_type_slug, _data, user |
| update_node | node_id, data |
| delete_node | node_id |
| get_list | node_type_slug, search |

### NodeTypeService ()
| 方法 | 参数 |
|------|------|
| get_all |  |
| get_all_including_inactive |  |
| get_by_id | node_type_id |
| get_by_id_or_404 | node_type_id |
| get_by_slug | slug |
| get_by_slug_or_404 | slug |
| get_by_slug_including_inactive | slug |
| get_by_slug_including_inactive_or_404 | slug |
| create | data |
| update | node_type_id, data |
| delete | node_type_id |
| enable | node_type_id |
| disable | node_type_id |
| toggle_active | node_type_id |
| get_node_count | node_type_id |
| get_node_types_from_modules |  |
| init_default_node_types |  |

### AuthService (BaseService)
| 方法 | 参数 |
|------|------|
| authenticate | username, password |
| login | _request, username, password |
| is_account_locked | user |
| unlock_expired_accounts |  |
| get_login_max_failures |  |
| get_login_lock_minutes |  |

### BaseService ()
| 方法 | 参数 |
|------|------|
| get_by_id | entity_id |
| get_by_slug | slug |
| get_list |  |
| create |  |
| update | entity_id |
| delete | entity_id |
| get_or_raise | entity_id, error_msg |
| get_first |  |
| get_or_none |  |

### ChinaRegionService ()
| 方法 | 参数 |
|------|------|
| import_from_file | file_path |
| import_from_url | url |
| _import_data | data |
| get_provinces |  |
| get_cities | province_code |
| get_districts | city_code |
| get_by_code | code |
| search | keyword, limit |
| get_full_path | region_code |
| get_tree |  |
| get_stats |  |
| download_to_file | url |

### CronService (SingletonMixin)
| 方法 | 参数 |
|------|------|
| __init__ |  |
| register | task |
| unregister | task_name |
| get_task | task_name |
| _should_run | task |
| _execute_task | task |
| _run_loop |  |
| start |  |
| stop |  |
| set_app_ready | ready |
| get_status |  |
| trigger | task_name |
| toggle | task_name, enabled |

### LogService ()
| 方法 | 参数 |
|------|------|
| _get_security_logger |  |
| get_client_ip | request |
| log_login_attempt | request, username, success, reason |
| log_logout | _user, username, ip |
| log_permission_denied | request, user, resource, reason |
| log_security_event | event_type, details, level |
| log_api_access | request, endpoint, user |
| log_data_export | request, user, export_type, record_count |
| log_failed_validation | request, form_name, errors |
| get_log_files |  |
| read_log | log_type, page, page_size, level |
| get_log_stats | log_type |

### CachedServiceMixin ()
| 方法 | 参数 |
|------|------|
| _get_cached | fetch_fn, key_suffix |
| _invalidate_cache | key_suffix |

### SingletonMixin ()
| 方法 | 参数 |
|------|------|
| __new__ |  |

### PermissionService ()
| 方法 | 参数 |
|------|------|
| get_all_permissions |  |
| get_system_permissions |  |
| get_role_permissions | role |
| get_role_permissions_from_db | role |
| save_role_permissions | role, permissions |
| has_permission | user, permission |
| get_user_effective_permissions | user |
| can_access_admin | user |
| init_default_role_permissions |  |
| get_node_permissions |  |

### SampleDataService ()
| 方法 | 参数 |
|------|------|
| init_sample_customers |  |

### SettingsService (CachedServiceMixin)
| 方法 | 参数 |
|------|------|
| get_all_settings | as_dict |
| get_setting | key, default, parse_json |
| save_setting | key, value, description |
| save_settings_bulk | settings_dict |
| reset_to_default | key |
| _reset_to_default_bulk |  |
| clear_cache |  |

### TaxonomyService (BaseService)
| 方法 | 参数 |
|------|------|
| get_all_taxonomies |  |
| get_taxonomy_list | search |
| check_slug_exists | slug |
| check_slug_exists_exclude | slug, exclude_id |
| get_taxonomy_by_id | taxonomy_id |
| get_taxonomy_by_slug | slug |
| create_taxonomy | name, slug, description |
| update_taxonomy | taxonomy_id, name, slug, description |
| delete_taxonomy | taxonomy_id |
| get_items | taxonomy_id |
| get_item_by_id | item_id |
| get_item | item_id |
| create_item | taxonomy_id, name, description, weight |
| update_item | item_id, name, description, weight |
| delete_item | item_id |
| reorder_items | taxonomy_id, item_ids |
| init_default_taxonomies |  |
| generate_items_ai | _taxonomy_id, _count |

### TimeService ()
| 方法 | 参数 |
|------|------|
| is_sync_enabled |  |
| get_time_server_url |  |
| get_current_time |  |
| get_current_datetime |  |
| get_timezone |  |
| get_sync_status |  |

### TimeSyncService (SingletonMixin)
| 方法 | 参数 |
|------|------|
| __init__ |  |
| _get_settings_value | key, default |
| is_enabled |  |
| get_sync_interval |  |
| get_max_retries |  |
| get_server_url |  |
| _fetch_time_from_server | url |
| _try_sync_with_servers |  |
| sync_time |  |
| get_current_time |  |
| get_current_time_str | fmt |
| get_status |  |

### UserService (BaseService)
| 方法 | 参数 |
|------|------|
| get_user_by_id | user_id |
| _protect_admin | user_id |
| _get_user_or_raise | user_id |
| get_user_by_username | username |
| get_user_list | search_term, only_active, exclude_admin, role |
| create_user | username, nickname, email, password... |
| update_user | user_id, username, nickname, email... |
| toggle_user_active | user_id, active |
| get_user_stats |  |
| update_profile | user_id, nickname, email |
| update_preferences | user_id, theme, notifications_enabled, preferred_language |
| change_password | user_id, new_password |
| get_navigation_cards | user_id |
| save_navigation_cards | user_id, cards |
| assign_position | cards |

### VersionService ()
| 方法 | 参数 |
|------|------|
| get_version |  |
| get_api_version |  |
| get_build_date |  |
| get_info |  |
| check_compatibility | client_version |
| get_supported_versions |  |

### WatermarkService ()
| 方法 | 参数 |
|------|------|
| _get_position_coords | position, img_width, img_height, marker_width... |
| add_text_watermark | image_path, output_path, text, position... |
| add_image_watermark | image_path, output_path, logo_path, position... |

### ClockService ()
| 方法 | 参数 |
|------|------|
| get_current_time |  |

### CustomerService ()
| 方法 | 参数 |
|------|------|
| get_list | search, customer_type_id, customer_level_id, user |
| get_by_id | customer_id |
| get_by_node_id | node_id |
| create | user, data |
| update | customer_id, _user, data |
| delete | customer_id |
| get_exportable_fields |  |
| get_count |  |
| get_recent_count | days |
| init_sample_data |  |

### ResidentInfoService ()
| 方法 | 参数 |
|------|------|
| get_list | search, resident_type_id, grid_id, current_community... |
| get_by_id | resident_id |
| get_by_node_id | node_id |
| create | user, data |
| update | resident_id, data |
| delete_by_node_id | node_id |
| get_count |  |
| get_recent_count | days |
| get_exportable_fields |  |
| init_sample_data |  |

### WhatsAppService ()
| 方法 | 参数 |
|------|------|
| check_health |  |
| restart_wabridge | timeout |
| ensure_healthy |  |
| get_status |  |
| send_message | phone, message |
| test_connection |  |
| create_batch | customer_ids, template_ids |
| send_next_pending |  |
| cancel_all_running |  |
| check_daily_limit |  |
| batch_check_whatsapp | customer_ids |
| check_phone | phone |
| start_recheck_all |  |
| start_recheck_remaining |  |
| stop_recheck |  |
| get_recheck_progress |  |

### TemplateService ()
| 方法 | 参数 |
|------|------|
| get_all |  |
| get_by_id | _id |
| get_default |  |
| create | title, content, is_default |
| update | _id, title, content, is_default |
| delete | _id |
| validate_variables | content |

### WhatsAppSendTask (CronTask)
| 方法 | 参数 |
|------|------|
| __init__ |  |
| execute |  |

### WABridgeRestartTask (CronTask)
| 方法 | 参数 |
|------|------|
| __init__ |  |
| execute |  |

---

## Known Design Issues

| # | File | Issue | Impact | Status |
|---|------|-------|--------|--------|
| 1 | `core/views/api/cards.py:135` | `module_contents[module_id]` 为 dict，多卡片时后覆盖前 | 每模块仅显示最后一张卡片 | TODO: 改为 list |
| 2 | `cimf_django/settings.py:383` | `DJANGO_SECRET_KEY` 仅在生产环境校验 | 开发环境可留占位密钥 | 预期行为 |
| 3 | `checks.py` CIMF_W001 | 已修复：`_extract_decorators_and_functions` 跳过缩进 def（类方法不再误报） | — | ✅ 已修复 |
| 4 | `checks.py` CIMF_W006 | PIL `Image.save()` 误报 | 2 条 false positive | 不影响功能 |
