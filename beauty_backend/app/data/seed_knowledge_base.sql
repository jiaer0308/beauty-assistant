-- 1. Insert Seasons
INSERT IGNORE INTO `seasons` (`name`, `description`) VALUES
('bright_spring', 'Bright Spring'),
('true_spring', 'True Spring'),
('light_spring', 'Light Spring'),
('light_summer', 'Light Summer'),
('true_summer', 'True Summer'),
('soft_summer', 'Soft Summer'),
('soft_autumn', 'Soft Autumn'),
('true_autumn', 'True Autumn'),
('dark_autumn', 'Dark Autumn'),
('dark_winter', 'Dark Winter'),
('true_winter', 'True Winter'),
('bright_winter', 'Bright Winter');

-- 2. Insert Colors
INSERT IGNORE INTO `colors` (`hex_code`, `name`) VALUES
('#f94994', 'Neon Pink'),
('#a4d13a', 'Apple Green'),
('#2187f3', 'Azure Blue'),
('#2A2B2A', 'Black Olive'),
('#F4F1EA', 'Alabaster White'),
('#3E403F', 'Onyx Gray'),
('#8A9A9A', 'Cadet Gray'),
('#635147', 'Dark Umber'),
('#D0DCE0', 'Pastel Blue Gray'),
('#87cd45', 'Lime Green'),
('#FFB347', 'Pastel Orange'),
('#FF7F50', 'Coral'),
('#4B3621', 'Cafe Noir'),
('#F2E8C6', 'Cornsilk Beige'),
('#9A463D', 'Dark Terracotta'),
('#E0B0FF', 'Mauve'),
('#778899', 'Light Slate Gray'),
('#0000FF', 'Pure Blue'),
('#FFE5B4', 'Peach Moccasin'),
('#f8b3ec', 'Light Plum Pink'),
('#B0E0E6', 'Powder Blue'),
('#D9D2CD', 'Timberwolf Gray'),
('#9F8C76', 'Dark Vanilla Khaki'),
('#EADDD7', 'Pale Taupe'),
('#000000', 'Pure Black'),
('#4A0E4E', 'Tyrian Purple'),
('#800000', 'Maroon'),
('#FFC0CB', 'Classic Pink'),
('#E6E6FA', 'Lavender'),
('#ADD8E6', 'Light Blue'),
('#708090', 'Slate Gray'),
('#F5F5F5', 'White Smoke'),
('#8B9695', 'Muted Cadet Blue'),
('#CD853F', 'Peru Brown'),
('#8B4513', 'Saddle Brown'),
('#BDB76B', 'Dark Khaki'),
('#97dbba', 'Aquamarine Green'),
('#6495ED', 'Cornflower Blue'),
('#D8BFD8', 'Thistle'),
('#4A5D23', 'Dark Olive Green'),
('#A9A9A9', 'Dark Gray'),
('#C0C0C0', 'Silver'),
('#FFFF00', 'Pure Yellow'),
('#FFA500', 'Pure Orange'),
('#FFDF00', 'Golden Yellow'),
('#BCA8B3', 'Rose Dust'),
('#7B8B88', 'Spanish Gray'),
('#02ab82', 'Teal Green'),
('#58504B', 'Wenge Brown'),
('#D5CECA', 'Platinum Gray'),
('#B9B1A6', 'Silver Sand'),
('#FF4500', 'Orange Red'),
('#FF00FF', 'Magenta'),
('#FFFFFF', 'Pure White'),
('#808000', 'Olive'),
('#CD5C5C', 'Indian Red'),
('#40E0D0', 'Turquoise'),
('#554E48', 'Taupe Brown'),
('#F5F5DC', 'Beige'),
('#C2B280', 'Ecru Sand'),
('#8A2BE2', 'Blue Violet'),
('#505e2f', 'Camouflage Green'),
('#DAA520', 'Goldenrod'),
('#fc5e1d', 'Coral Orange'),
('#3B2F2F', 'Bistre Brown'),
('#EADDCD', 'Almond Taupe'),
('#556B2F', 'Dark Olive Green'),
('#F0F8FF', 'Alice Blue'),
('#680e03', 'Blood Red'),
('#CC5500', 'Burnt Orange'),
('#005B5C', 'Dark Cyan Teal'),
('#2E3029', 'Jet Black Olive'),
('#3D2314', 'Seal Brown'),
('#D2B48C', 'Tan'),
('#B0C4DE', 'Light Steel Blue'),
('#800020', 'Burgundy'),
('#004B49', 'Midnight Green'),
('#1126a5', 'Deep Navy Blue'),
('#191970', 'Midnight Blue'),
('#F0F0F0', 'Anti-Flash White'),
('#CD7F32', 'Bronze'),
('#CC7722', 'Ochre'),
('#F5DEB3', 'Wheat'),
('#009b52', 'Shamrock Green'),
('#FF007F', 'Bright Rose'),
('#000080', 'Navy'),
('#36454F', 'Charcoal'),
('#D2691E', 'Chocolate'),
('#B87333', 'Copper'),
('#8C92AC', 'Cool Grey'),
('#7FFF00', 'Chartreuse'),
('#00FFFF', 'Cyan'),
('#1A1A1A', 'Eerie Black'),
('#E0E0E0', 'Light Gray'),
('#F8F8FF', 'Ghost White'),
('#9E7E53', 'Pale Brown');

-- 3. Insert Season Color Mappings
-- We use subqueries to dynamically fetch the ID of the season and color to avoid auto-increment mismatches

-- bright_spring
INSERT IGNORE INTO `season_colors` (`season_id`, `color_id`, `category_type`) VALUES
((SELECT id FROM seasons WHERE name = 'bright_spring'), (SELECT id FROM colors WHERE hex_code = '#f94994'), 'best'),
((SELECT id FROM seasons WHERE name = 'bright_spring'), (SELECT id FROM colors WHERE hex_code = '#a4d13a'), 'best'),
((SELECT id FROM seasons WHERE name = 'bright_spring'), (SELECT id FROM colors WHERE hex_code = '#2187f3'), 'best'),
((SELECT id FROM seasons WHERE name = 'bright_spring'), (SELECT id FROM colors WHERE hex_code = '#2A2B2A'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'bright_spring'), (SELECT id FROM colors WHERE hex_code = '#F4F1EA'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'bright_spring'), (SELECT id FROM colors WHERE hex_code = '#3E403F'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'bright_spring'), (SELECT id FROM colors WHERE hex_code = '#8A9A9A'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'bright_spring'), (SELECT id FROM colors WHERE hex_code = '#635147'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'bright_spring'), (SELECT id FROM colors WHERE hex_code = '#D0DCE0'), 'avoid');

-- true_spring
INSERT IGNORE INTO `season_colors` (`season_id`, `color_id`, `category_type`) VALUES
((SELECT id FROM seasons WHERE name = 'true_spring'), (SELECT id FROM colors WHERE hex_code = '#87cd45'), 'best'),
((SELECT id FROM seasons WHERE name = 'true_spring'), (SELECT id FROM colors WHERE hex_code = '#FFB347'), 'best'),
((SELECT id FROM seasons WHERE name = 'true_spring'), (SELECT id FROM colors WHERE hex_code = '#FF7F50'), 'best'),
((SELECT id FROM seasons WHERE name = 'true_spring'), (SELECT id FROM colors WHERE hex_code = '#4B3621'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'true_spring'), (SELECT id FROM colors WHERE hex_code = '#F2E8C6'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'true_spring'), (SELECT id FROM colors WHERE hex_code = '#9A463D'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'true_spring'), (SELECT id FROM colors WHERE hex_code = '#E0B0FF'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'true_spring'), (SELECT id FROM colors WHERE hex_code = '#778899'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'true_spring'), (SELECT id FROM colors WHERE hex_code = '#0000FF'), 'avoid');

-- light_spring
INSERT IGNORE INTO `season_colors` (`season_id`, `color_id`, `category_type`) VALUES
((SELECT id FROM seasons WHERE name = 'light_spring'), (SELECT id FROM colors WHERE hex_code = '#FFE5B4'), 'best'),
((SELECT id FROM seasons WHERE name = 'light_spring'), (SELECT id FROM colors WHERE hex_code = '#f8b3ec'), 'best'),
((SELECT id FROM seasons WHERE name = 'light_spring'), (SELECT id FROM colors WHERE hex_code = '#B0E0E6'), 'best'),
((SELECT id FROM seasons WHERE name = 'light_spring'), (SELECT id FROM colors WHERE hex_code = '#D9D2CD'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'light_spring'), (SELECT id FROM colors WHERE hex_code = '#9F8C76'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'light_spring'), (SELECT id FROM colors WHERE hex_code = '#EADDD7'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'light_spring'), (SELECT id FROM colors WHERE hex_code = '#000000'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'light_spring'), (SELECT id FROM colors WHERE hex_code = '#4A0E4E'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'light_spring'), (SELECT id FROM colors WHERE hex_code = '#800000'), 'avoid');

-- light_summer
INSERT IGNORE INTO `season_colors` (`season_id`, `color_id`, `category_type`) VALUES
((SELECT id FROM seasons WHERE name = 'light_summer'), (SELECT id FROM colors WHERE hex_code = '#FFC0CB'), 'best'),
((SELECT id FROM seasons WHERE name = 'light_summer'), (SELECT id FROM colors WHERE hex_code = '#E6E6FA'), 'best'),
((SELECT id FROM seasons WHERE name = 'light_summer'), (SELECT id FROM colors WHERE hex_code = '#ADD8E6'), 'best'),
((SELECT id FROM seasons WHERE name = 'light_summer'), (SELECT id FROM colors WHERE hex_code = '#708090'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'light_summer'), (SELECT id FROM colors WHERE hex_code = '#F5F5F5'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'light_summer'), (SELECT id FROM colors WHERE hex_code = '#8B9695'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'light_summer'), (SELECT id FROM colors WHERE hex_code = '#CD853F'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'light_summer'), (SELECT id FROM colors WHERE hex_code = '#8B4513'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'light_summer'), (SELECT id FROM colors WHERE hex_code = '#BDB76B'), 'avoid');

-- true_summer
INSERT IGNORE INTO `season_colors` (`season_id`, `color_id`, `category_type`) VALUES
((SELECT id FROM seasons WHERE name = 'true_summer'), (SELECT id FROM colors WHERE hex_code = '#97dbba'), 'best'),
((SELECT id FROM seasons WHERE name = 'true_summer'), (SELECT id FROM colors WHERE hex_code = '#6495ED'), 'best'),
((SELECT id FROM seasons WHERE name = 'true_summer'), (SELECT id FROM colors WHERE hex_code = '#D8BFD8'), 'best'),
((SELECT id FROM seasons WHERE name = 'true_summer'), (SELECT id FROM colors WHERE hex_code = '#4A5D23'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'true_summer'), (SELECT id FROM colors WHERE hex_code = '#A9A9A9'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'true_summer'), (SELECT id FROM colors WHERE hex_code = '#C0C0C0'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'true_summer'), (SELECT id FROM colors WHERE hex_code = '#FFFF00'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'true_summer'), (SELECT id FROM colors WHERE hex_code = '#FFA500'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'true_summer'), (SELECT id FROM colors WHERE hex_code = '#FFDF00'), 'avoid');

-- soft_summer
INSERT IGNORE INTO `season_colors` (`season_id`, `color_id`, `category_type`) VALUES
((SELECT id FROM seasons WHERE name = 'soft_summer'), (SELECT id FROM colors WHERE hex_code = '#BCA8B3'), 'best'),
((SELECT id FROM seasons WHERE name = 'soft_summer'), (SELECT id FROM colors WHERE hex_code = '#7B8B88'), 'best'),
((SELECT id FROM seasons WHERE name = 'soft_summer'), (SELECT id FROM colors WHERE hex_code = '#02ab82'), 'best'),
((SELECT id FROM seasons WHERE name = 'soft_summer'), (SELECT id FROM colors WHERE hex_code = '#58504B'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'soft_summer'), (SELECT id FROM colors WHERE hex_code = '#D5CECA'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'soft_summer'), (SELECT id FROM colors WHERE hex_code = '#B9B1A6'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'soft_summer'), (SELECT id FROM colors WHERE hex_code = '#FF4500'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'soft_summer'), (SELECT id FROM colors WHERE hex_code = '#FF00FF'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'soft_summer'), (SELECT id FROM colors WHERE hex_code = '#FFFFFF'), 'avoid');

-- soft_autumn
INSERT IGNORE INTO `season_colors` (`season_id`, `color_id`, `category_type`) VALUES
((SELECT id FROM seasons WHERE name = 'soft_autumn'), (SELECT id FROM colors WHERE hex_code = '#808000'), 'best'),
((SELECT id FROM seasons WHERE name = 'soft_autumn'), (SELECT id FROM colors WHERE hex_code = '#CD5C5C'), 'best'),
((SELECT id FROM seasons WHERE name = 'soft_autumn'), (SELECT id FROM colors WHERE hex_code = '#40E0D0'), 'best'),
((SELECT id FROM seasons WHERE name = 'soft_autumn'), (SELECT id FROM colors WHERE hex_code = '#554E48'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'soft_autumn'), (SELECT id FROM colors WHERE hex_code = '#F5F5DC'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'soft_autumn'), (SELECT id FROM colors WHERE hex_code = '#C2B280'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'soft_autumn'), (SELECT id FROM colors WHERE hex_code = '#0000FF'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'soft_autumn'), (SELECT id FROM colors WHERE hex_code = '#8A2BE2'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'soft_autumn'), (SELECT id FROM colors WHERE hex_code = '#C0C0C0'), 'avoid');

-- true_autumn
INSERT IGNORE INTO `season_colors` (`season_id`, `color_id`, `category_type`) VALUES
((SELECT id FROM seasons WHERE name = 'true_autumn'), (SELECT id FROM colors WHERE hex_code = '#505e2f'), 'best'),
((SELECT id FROM seasons WHERE name = 'true_autumn'), (SELECT id FROM colors WHERE hex_code = '#DAA520'), 'best'),
((SELECT id FROM seasons WHERE name = 'true_autumn'), (SELECT id FROM colors WHERE hex_code = '#fc5e1d'), 'best'),
((SELECT id FROM seasons WHERE name = 'true_autumn'), (SELECT id FROM colors WHERE hex_code = '#3B2F2F'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'true_autumn'), (SELECT id FROM colors WHERE hex_code = '#EADDCD'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'true_autumn'), (SELECT id FROM colors WHERE hex_code = '#556B2F'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'true_autumn'), (SELECT id FROM colors WHERE hex_code = '#FF00FF'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'true_autumn'), (SELECT id FROM colors WHERE hex_code = '#F0F8FF'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'true_autumn'), (SELECT id FROM colors WHERE hex_code = '#000000'), 'avoid');

-- dark_autumn
INSERT IGNORE INTO `season_colors` (`season_id`, `color_id`, `category_type`) VALUES
((SELECT id FROM seasons WHERE name = 'dark_autumn'), (SELECT id FROM colors WHERE hex_code = '#680e03'), 'best'),
((SELECT id FROM seasons WHERE name = 'dark_autumn'), (SELECT id FROM colors WHERE hex_code = '#CC5500'), 'best'),
((SELECT id FROM seasons WHERE name = 'dark_autumn'), (SELECT id FROM colors WHERE hex_code = '#005B5C'), 'best'),
((SELECT id FROM seasons WHERE name = 'dark_autumn'), (SELECT id FROM colors WHERE hex_code = '#2E3029'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'dark_autumn'), (SELECT id FROM colors WHERE hex_code = '#3D2314'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'dark_autumn'), (SELECT id FROM colors WHERE hex_code = '#D2B48C'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'dark_autumn'), (SELECT id FROM colors WHERE hex_code = '#E6E6FA'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'dark_autumn'), (SELECT id FROM colors WHERE hex_code = '#B0C4DE'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'dark_autumn'), (SELECT id FROM colors WHERE hex_code = '#FFFFFF'), 'avoid');

-- dark_winter
INSERT IGNORE INTO `season_colors` (`season_id`, `color_id`, `category_type`) VALUES
((SELECT id FROM seasons WHERE name = 'dark_winter'), (SELECT id FROM colors WHERE hex_code = '#800020'), 'best'),
((SELECT id FROM seasons WHERE name = 'dark_winter'), (SELECT id FROM colors WHERE hex_code = '#004B49'), 'best'),
((SELECT id FROM seasons WHERE name = 'dark_winter'), (SELECT id FROM colors WHERE hex_code = '#1126a5'), 'best'),
((SELECT id FROM seasons WHERE name = 'dark_winter'), (SELECT id FROM colors WHERE hex_code = '#000000'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'dark_winter'), (SELECT id FROM colors WHERE hex_code = '#191970'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'dark_winter'), (SELECT id FROM colors WHERE hex_code = '#F0F0F0'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'dark_winter'), (SELECT id FROM colors WHERE hex_code = '#CD7F32'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'dark_winter'), (SELECT id FROM colors WHERE hex_code = '#CC7722'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'dark_winter'), (SELECT id FROM colors WHERE hex_code = '#F5DEB3'), 'avoid');

-- true_winter
INSERT IGNORE INTO `season_colors` (`season_id`, `color_id`, `category_type`) VALUES
((SELECT id FROM seasons WHERE name = 'true_winter'), (SELECT id FROM colors WHERE hex_code = '#009b52'), 'best'),
((SELECT id FROM seasons WHERE name = 'true_winter'), (SELECT id FROM colors WHERE hex_code = '#FF007F'), 'best'),
((SELECT id FROM seasons WHERE name = 'true_winter'), (SELECT id FROM colors WHERE hex_code = '#0000FF'), 'best'),
((SELECT id FROM seasons WHERE name = 'true_winter'), (SELECT id FROM colors WHERE hex_code = '#FFFFFF'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'true_winter'), (SELECT id FROM colors WHERE hex_code = '#000080'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'true_winter'), (SELECT id FROM colors WHERE hex_code = '#36454F'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'true_winter'), (SELECT id FROM colors WHERE hex_code = '#D2691E'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'true_winter'), (SELECT id FROM colors WHERE hex_code = '#B87333'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'true_winter'), (SELECT id FROM colors WHERE hex_code = '#8C92AC'), 'avoid');

-- bright_winter
INSERT IGNORE INTO `season_colors` (`season_id`, `color_id`, `category_type`) VALUES
((SELECT id FROM seasons WHERE name = 'bright_winter'), (SELECT id FROM colors WHERE hex_code = '#FF00FF'), 'best'),
((SELECT id FROM seasons WHERE name = 'bright_winter'), (SELECT id FROM colors WHERE hex_code = '#7FFF00'), 'best'),
((SELECT id FROM seasons WHERE name = 'bright_winter'), (SELECT id FROM colors WHERE hex_code = '#00FFFF'), 'best'),
((SELECT id FROM seasons WHERE name = 'bright_winter'), (SELECT id FROM colors WHERE hex_code = '#1A1A1A'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'bright_winter'), (SELECT id FROM colors WHERE hex_code = '#E0E0E0'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'bright_winter'), (SELECT id FROM colors WHERE hex_code = '#F8F8FF'), 'neutral'),
((SELECT id FROM seasons WHERE name = 'bright_winter'), (SELECT id FROM colors WHERE hex_code = '#DAA520'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'bright_winter'), (SELECT id FROM colors WHERE hex_code = '#9E7E53'), 'avoid'),
((SELECT id FROM seasons WHERE name = 'bright_winter'), (SELECT id FROM colors WHERE hex_code = '#CC7722'), 'avoid');

