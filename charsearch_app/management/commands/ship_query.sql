SELECT
Ships.typeName AS ShipName,
Ships.typeID as ShipID,
Grouping.groupName AS ShipType,
Grouping.groupID as GroupID,
Skills.typeName AS RequiredSkill,
Skills.typeID as SkillID,
COALESCE(SkillLevel.valueInt, SkillLevel.valueFloat) AS RequiredLevel
FROM
dgmTypeAttributes AS SkillName
INNER JOIN invTypes AS Ships ON Ships.typeID = SkillName.typeID
INNER JOIN invGroups AS Grouping ON Grouping.groupID = Ships.groupID
INNER JOIN invTypes AS Skills ON (Skills.typeID = SkillName.valueInt OR Skills.typeID = SkillName.valueFloat) AND SkillName.attributeID IN (182, 183, 184, 1285, 1289, 1290)
INNER JOIN dgmTypeAttributes AS SkillLevel ON SkillLevel.typeID = SkillName.typeID AND SkillLevel.attributeID IN (277, 278, 279, 1286, 1287, 1288)
WHERE
Grouping.categoryID = 6 AND -- categoryID is ship type
Ships.published = 1 AND
((SkillName.attributeID = 182 AND
SkillLevel.attributeID = 277) OR
(SkillName.attributeID = 183 AND
SkillLevel.attributeID = 278) OR
(SkillName.attributeID = 184 AND
SkillLevel.attributeID = 279) OR
(SkillName.attributeID = 1285 AND
SkillLevel.attributeID = 1286) OR
(SkillName.attributeID = 1289 AND
SkillLevel.attributeID = 1287) OR
(SkillName.attributeID = 1290 AND
SkillLevel.attributeID = 1288))
ORDER BY ShipName
