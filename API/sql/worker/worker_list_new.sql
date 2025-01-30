SELECT u.`user_id`, ui.`fullname`, ui.`age`, u.`uuid` FROM `Users` as u
JOIN `Users_info` as ui ON ui.`user_id` = u.`user_id`
JOIN `Companies_Users` as cu ON cu.`user_id` = `u`.`user_id`
WHERE cu.`company_id` = %s;