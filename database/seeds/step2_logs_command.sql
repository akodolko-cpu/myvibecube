-- ЭТАП 2: Добавление команды /logs для админа
INSERT IGNORE INTO commands (command_name, description, is_active) VALUES
('/logs', 'Просмотр логов действий (только для admin)', TRUE);

INSERT IGNORE INTO role_commands (role_id, command_id)
SELECT r.id, c.id FROM roles r, commands c
WHERE r.role_name = 'admin' AND c.command_name = '/logs'
  AND NOT EXISTS (SELECT 1 FROM role_commands rc WHERE rc.role_id = r.id AND rc.command_id = c.id);
