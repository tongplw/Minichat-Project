CREATE DATABASE IF NOT EXISTS minichat;
USE minichat;

DROP TABLE IF EXISTS `groups`;

CREATE TABLE `groups` (
  `name` varchar(255) PRIMARY KEY,
);