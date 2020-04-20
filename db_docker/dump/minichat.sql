
CREATE DATABASE IF NOT EXISTS minichat;
USE minichat;

DROP TABLE IF EXISTS `users`;


CREATE TABLE `users` (
  `username` varchar(255) PRIMARY KEY,
  `password` varchar(255) NULL
);

	


