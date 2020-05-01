
CREATE DATABASE IF NOT EXISTS minichat;
USE minichat;

DROP TABLE IF EXISTS `users`;
DROP TABLE IF EXISTS `groups`;
DROP TABLE IF EXISTS `messages`;
DROP TABLE IF EXISTS `group_user`;


CREATE TABLE `users` (
  `username` VARCHAR(255) PRIMARY KEY,
  `password` VARCHAR(255) NULL,
  `is_online` boolean NOT NULL,
  `last_login` TIMESTAMP CURRENT_TIMESTAMP
);

CREATE TABLE `groups` (
  `name` VARCHAR(255) PRIMARY KEY
);

CREATE TABLE `messages` (
  `id` int(11) unsigned PRIMARY KEY AUTO_INCREMENT,
  `message` VARCHAR(255),
  `user_id` VARCHAR(255),
  `group_id` VARCHAR(255),
  `sent_on` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
);	

CREATE TABLE `group_user` (
  `user_id` VARCHAR(255) NOT NULL,
  `group_id` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`user_id`, `group_id`)
  FOREIGN KEY(`user_id`) REFERENCES `users`(`username`),
  FOREIGN KEY(`group_id`) REFERENCES `groups`(`name`)
);