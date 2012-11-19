DROP TABLE IF EXISTS `pkCharacters`;
DROP TABLE IF EXISTS `pkItems`;
DROP TABLE IF EXISTS `pkKillmails`;

CREATE TABLE `pkKillmails` (
	`killID` int(20) unsigned NOT NULL,
	`solarSystemID` int(20) unsigned NOT NULL,
	`killTime` datetime NOT NULL,
	`moonID` int(20) unsigned NOT NULL,
	PRIMARY KEY (`killID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `pkCharacters` (
	`id` int(20) unsigned NOT NULL AUTO_INCREMENT,
	`killID` int(20) unsigned NOT NULL,
	`victim` tinyint(1) NOT NULL,
	`characterID` int(20) unsigned NOT NULL,
	`characterName` varchar(64) NOT NULL,
	`shipTypeID` int(20) NOT NULL,
	`allianceID` int(20) NOT NULL,
	`allianceName` varchar(64) NOT NULL,
	`corporationID` int(20) NOT NULL,
	`corporationName` varchar(64) NOT NULL,
	`factionID` int(20) NOT NULL,
	`factionName` varchar(64) NOT NULL,
	`damageTaken` int(20) DEFAULT NULL,
	`damageDone` int(20) DEFAULT NULL,
	`finalBlow` tinyint(1) DEFAULT NULL,
	`securityStatus` float DEFAULT NULL,
	`weaponTypeID` int(20) DEFAULT NULL,
	PRIMARY KEY (`id`),
	KEY `fk_killmails` (`killID`),
	CONSTRAINT `fk_killmails` FOREIGN KEY (`killID`) REFERENCES `pkKillmails` (`killID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `pkItems` (
	`id` int(20) unsigned NOT NULL AUTO_INCREMENT,
	`typeID` int(20) unsigned NOT NULL,
	`killID` int(20) unsigned NOT NULL,
	`flag` tinyint(3) unsigned NOT NULL,
	`qtyDropped` int(20) unsigned NOT NULL,
	`qtyDestroyed` int(20) unsigned NOT NULL,
	`singleton` tinyint(4) NOT NULL,
	PRIMARY KEY (`id`),
	KEY `killID` (`killID`),
	CONSTRAINT `items_ibfk_1` FOREIGN KEY (`killID`) REFERENCES `pkKillmails` (`killID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
