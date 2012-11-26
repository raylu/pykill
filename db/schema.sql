DROP TABLE IF EXISTS `pkCharacters`;
DROP TABLE IF EXISTS `pkItems`;
DROP TABLE IF EXISTS `pkKillmails`;
DROP TABLE IF EXISTS `pkItemCosts`;

CREATE TABLE `pkKillmails` (
	`killID` int unsigned NOT NULL,
	`solarSystemID` int NOT NULL,
	`killTime` datetime NOT NULL,
	`moonID` int unsigned NOT NULL,
	PRIMARY KEY (`killID`),
	CONSTRAINT `fk_km_solarsystems` FOREIGN KEY (`solarSystemID`) REFERENCES `mapSolarSystems` (`solarSystemID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `pkCharacters` (
	`id` int unsigned NOT NULL AUTO_INCREMENT,
	`killID` int unsigned NOT NULL,
	`victim` tinyint(1) NOT NULL,
	`characterID` int unsigned NOT NULL,
	`characterName` varchar(64) NOT NULL,
	`shipTypeID` int NOT NULL,
	`allianceID` int unsigned NOT NULL,
	`allianceName` varchar(64) NOT NULL,
	`corporationID` int unsigned NOT NULL,
	`corporationName` varchar(64) NOT NULL,
	`factionID` int NOT NULL,
	`factionName` varchar(64) NOT NULL,
	`damageTaken` int DEFAULT NULL,
	`damageDone` int DEFAULT NULL,
	`finalBlow` tinyint(1) DEFAULT NULL,
	`securityStatus` float DEFAULT NULL,
	`weaponTypeID` int DEFAULT NULL,
	PRIMARY KEY (`id`),
	CONSTRAINT `fk_char_km` FOREIGN KEY (`killID`) REFERENCES `pkKillmails` (`killID`),
	CONSTRAINT `fk_char_types_ship` FOREIGN KEY (`shipTypeID`) REFERENCES `invTypes` (`typeID`),
	CONSTRAINT `fk_char_types_weapon` FOREIGN KEY (`weaponTypeID`) REFERENCES `invTypes` (`typeID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `pkItems` (
	`id` int unsigned NOT NULL AUTO_INCREMENT,
	`killID` int unsigned NOT NULL,
	`typeID` int NOT NULL,
	`flag` tinyint(3) unsigned NOT NULL,
	`qtyDropped` int unsigned NOT NULL,
	`qtyDestroyed` int unsigned NOT NULL,
	`singleton` tinyint(4) NOT NULL,
	PRIMARY KEY (`id`),
	CONSTRAINT `fk_item_km` FOREIGN KEY (`killID`) REFERENCES `pkKillmails` (`killID`),
	CONSTRAINT `fk_item_types` FOREIGN KEY (`typeID`) REFERENCES `invTypes` (`typeID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `pkItemCosts` (
	`typeID` int NOT NULL,
	`cost` bigint unsigned NOT NULL,
	PRIMARY KEY (`typeID`),
	CONSTRAINT `fk_itemcost_types` FOREIGN KEY (`typeID`) REFERENCES `invTypes` (`typeID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
