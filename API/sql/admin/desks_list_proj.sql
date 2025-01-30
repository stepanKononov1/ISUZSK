SELECT d.`desk_id`, d.`name`
FROM `Desks` AS d
JOIN `Companies_Desks` AS cd ON cd.`desk_id` = d.`desk_id`
LEFT JOIN `Projects_Desks` AS pd ON pd.`desk_id` = d.`desk_id`
WHERE cd.`company_id` = %s
AND pd.`desk_id` IS NULL;